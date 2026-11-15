import time
from urllib.parse import quote

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ContactInquiry, Driver, NewsletterSubscriber, Order, OrderItem
from .serializers import DriverSerializer, OrderSerializer
from .stock import StockError, decrease_stock, restore_stock, validate_order_stock


def maps_url(lat, lng):
    return f"https://www.google.com/maps?q={lat},{lng}"


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payload = request.data.get("data") or request.data
        items = payload.get("items") if isinstance(payload.get("items"), list) else []
        order_number = f"ATL-{int(time.time() * 1000)}"

        try:
            validate_order_stock(items)
        except StockError as exc:
            return Response({"error": {"message": str(exc)}}, status=status.HTTP_400_BAD_REQUEST)

        stock_reduced = False
        try:
            decrease_stock(items)
            stock_reduced = True

            order = Order.objects.create(
                order_number=order_number,
                first_name=payload.get("firstName", ""),
                last_name=payload.get("lastName", ""),
                email=payload.get("email", ""),
                street_address=payload.get("streetAddress", ""),
                postal_code=payload.get("postalCode", ""),
                city=payload.get("city", ""),
                country=payload.get("country", ""),
                payment_method="cash_on_delivery",
                order_status="pending",
                total=int(payload.get("total") or 0),
                customer_id=request.user.id,
                customer_username=request.user.username,
            )
            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        product_name=item.get("productName", ""),
                        product_document_id=str(item.get("productDocumentId") or ""),
                        quantity=int(item.get("quantity") or 1),
                        unit_price=int(item.get("unitPrice") or 0),
                        color=item.get("color") or "",
                        size=item.get("size") or "",
                        image_url=item.get("imageUrl") or "",
                    )
                    for item in items
                ]
            )

            admin_email = getattr(settings, "ADMIN_NOTIFICATION_EMAIL", "") or ""
            if admin_email:
                try:
                    send_mail(
                        subject=f"New order {order_number}",
                        message=f"Order {order_number} from {request.user.username} — total {order.total}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[admin_email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            order = Order.objects.prefetch_related("items").get(pk=order.id)
            return Response({"data": OrderSerializer(order).data}, status=status.HTTP_201_CREATED)
        except StockError as exc:
            if stock_reduced:
                restore_stock(items)
            return Response({"error": {"message": str(exc)}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            if stock_reduced:
                restore_stock(items)
            raise


class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = (
            Order.objects.filter(customer_id=request.user.id)
            .prefetch_related("items")
            .select_related("driver", "fulfillment_source")
        )
        return Response({"data": [OrderSerializer(o).data for o in orders]})


class TrackOrderView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, order_number):
        order = (
            Order.objects.filter(order_number=order_number)
            .prefetch_related("items")
            .select_related("driver", "fulfillment_source")
            .first()
        )
        if not order:
            return Response({"error": {"message": "Order not found"}}, status=404)

        email_query = (request.query_params.get("email") or "").strip().lower()
        user = request.user if request.user.is_authenticated else None
        order_email = (order.email or "").strip().lower()

        if user:
            is_assigned_driver = False
            driver = Driver.objects.filter(user=user).first()
            if driver and order.driver_id == driver.id:
                is_assigned_driver = True
            owns = (
                order.customer_id == user.id
                or order_email == (user.email or "").strip().lower()
                or is_assigned_driver
            )
            if not owns:
                return Response(
                    {"error": {"message": "You do not have access to this order."}},
                    status=403,
                )
        else:
            if not email_query or email_query != order_email:
                return Response(
                    {
                        "error": {
                            "message": "Enter the email used at checkout, or sign in to track your order."
                        }
                    },
                    status=401,
                )

        return Response({"data": OrderSerializer(order).data, "meta": {}})


class DeliverySessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = (request.query_params.get("token") or "").strip()
        if not token:
            return Response({"error": {"message": "Missing token"}}, status=400)

        order = Order.objects.filter(delivery_share_token=token).first()
        if not order:
            return Response({"error": {"message": "Invalid delivery link"}}, status=404)
        if order.order_status != "delivering":
            return Response(
                {"error": {"message": "This order is not out for delivery yet."}},
                status=403,
            )

        return Response(
            {
                "data": {
                    "orderNumber": order.order_number,
                    "orderStatus": order.order_status,
                    "city": order.city,
                    "country": order.country,
                }
            }
        )


class ShareDriverLocationPublicView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = (request.data.get("token") or "").strip()
        try:
            latitude = float(request.data.get("latitude"))
            longitude = float(request.data.get("longitude"))
        except (TypeError, ValueError):
            return Response({"error": {"message": "Invalid coordinates"}}, status=400)

        order = Order.objects.filter(delivery_share_token=token).first()
        if not order:
            return Response({"error": {"message": "Invalid delivery link"}}, status=404)
        if order.order_status != "delivering":
            return Response(
                {"error": {"message": "This order is not out for delivery yet."}},
                status=403,
            )

        order.driver_latitude = latitude
        order.driver_longitude = longitude
        order.driver_location_updated_at = timezone.now()
        order.tracking_map_url = maps_url(latitude, longitude)
        order.save(
            update_fields=[
                "driver_latitude",
                "driver_longitude",
                "driver_location_updated_at",
                "tracking_map_url",
            ]
        )
        return Response({"data": {"ok": True}})


class DriverRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payload = request.data.get("data") or request.data
        if Driver.objects.filter(user=request.user).exists():
            driver = Driver.objects.get(user=request.user)
            return Response({"data": DriverSerializer(driver).data})

        full_name = (payload.get("fullName") or "").strip()
        phone = (payload.get("phone") or "").strip()
        vehicle_type = payload.get("vehicleType") or "motorcycle"
        if not full_name or not phone:
            return Response(
                {"error": {"message": "fullName and phone are required."}},
                status=400,
            )

        driver = Driver.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            vehicle_type=vehicle_type,
        )
        return Response({"data": DriverSerializer(driver).data}, status=201)


class DriverMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver = Driver.objects.filter(user=request.user).first()
        if not driver:
            return Response({"error": {"message": "Driver profile not found"}}, status=404)
        return Response({"data": DriverSerializer(driver).data})


class DriverMyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver = Driver.objects.filter(user=request.user).first()
        if not driver:
            return Response({"error": {"message": "Driver profile not found"}}, status=404)
        orders = (
            Order.objects.filter(driver=driver, order_status="delivering")
            .prefetch_related("items")
            .select_related("fulfillment_source")
        )
        return Response({"data": [OrderSerializer(o).data for o in orders]})


class DriverShareLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        driver = Driver.objects.filter(user=request.user).first()
        if not driver:
            return Response({"error": {"message": "Driver profile not found"}}, status=404)

        order_document_id = str(request.data.get("orderDocumentId") or "").strip()
        try:
            latitude = float(request.data.get("latitude"))
            longitude = float(request.data.get("longitude"))
        except (TypeError, ValueError):
            return Response({"error": {"message": "Invalid coordinates"}}, status=400)

        order = Order.objects.filter(document_id=order_document_id, driver=driver).first()
        if not order:
            return Response({"error": {"message": "Order not found"}}, status=404)

        now = timezone.now()
        order.driver_latitude = latitude
        order.driver_longitude = longitude
        order.driver_location_updated_at = now
        order.tracking_map_url = maps_url(latitude, longitude)
        order.save(
            update_fields=[
                "driver_latitude",
                "driver_longitude",
                "driver_location_updated_at",
                "tracking_map_url",
            ]
        )

        driver.current_latitude = latitude
        driver.current_longitude = longitude
        driver.last_location_at = now
        driver.save(update_fields=["current_latitude", "current_longitude", "last_location_at"])

        return Response({"data": {"ok": True}})


class NewsletterSubscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data.get("data") or request.data
        email = (payload.get("email") or "").strip().lower()
        if not email:
            return Response({"error": {"message": "Email is required."}}, status=400)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email, defaults={"is_active": True}
        )
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=["is_active"])

        return Response(
            {
                "data": {
                    "email": email,
                    "message": "Subscribed" if created else "Already subscribed",
                    "alreadySubscribed": not created,
                }
            }
        )


class ContactInquirySubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data.get("data") or request.data
        name = (payload.get("name") or "").strip()
        email = (payload.get("email") or "").strip()
        message = (payload.get("message") or "").strip()

        if not name or not email or not message:
            return Response(
                {"error": {"message": "Name, email and message are required."}},
                status=400,
            )

        inquiry_number = f"INQ-{int(time.time() * 1000)}"
        ContactInquiry.objects.create(
            inquiry_number=inquiry_number,
            name=name,
            email=email,
            message=message,
        )

        admin_email = getattr(settings, "ADMIN_NOTIFICATION_EMAIL", "") or ""
        if admin_email:
            send_mail(
                subject=f"Contact inquiry {inquiry_number}",
                message=f"From {name} <{email}>:\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )

        return Response(
            {
                "data": {
                    "inquiryNumber": inquiry_number,
                    "message": "Inquiry received",
                }
            },
            status=201,
        )
