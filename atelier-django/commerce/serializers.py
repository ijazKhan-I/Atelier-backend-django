from catalog.serializers import iso

from .models import Driver, FulfillmentSource, Order, OrderItem


class FulfillmentSourceSerializer:
    def __init__(self, instance: FulfillmentSource):
        self.instance = instance

    @property
    def data(self):
        s = self.instance
        return {
            "documentId": str(s.document_id),
            "name": s.name,
            "sourceType": s.source_type,
            "streetAddress": s.street_address,
            "city": s.city,
            "country": s.country,
            "phone": s.phone,
            "isActive": s.is_active,
            "lat": s.lat,
            "lng": s.lng,
            "geohash": s.geohash or None,
            "location": {"lat": s.lat, "lng": s.lng} if s.lat is not None else None,
        }


class OrderItemSerializer:
    def __init__(self, instance: OrderItem):
        self.instance = instance

    @property
    def data(self):
        i = self.instance
        return {
            "id": i.id,
            "productName": i.product_name,
            "productDocumentId": i.product_document_id,
            "quantity": i.quantity,
            "unitPrice": i.unit_price,
            "color": i.color,
            "size": i.size,
            "imageUrl": i.image_url,
        }


class OrderSerializer:
    def __init__(self, instance: Order, *, public: bool = True):
        self.instance = instance
        self.public = public

    @property
    def data(self):
        o = self.instance
        payload = {
            "id": o.id,
            "documentId": str(o.document_id),
            "createdAt": iso(o.created_at),
            "updatedAt": iso(o.updated_at),
            "orderNumber": o.order_number,
            "firstName": o.first_name,
            "lastName": o.last_name,
            "email": o.email,
            "streetAddress": o.street_address,
            "postalCode": o.postal_code,
            "city": o.city,
            "country": o.country,
            "paymentMethod": o.payment_method,
            "orderStatus": o.order_status,
            "total": o.total,
            "customerId": o.customer_id,
            "customerUsername": o.customer_username,
            "trackingMapUrl": o.tracking_map_url,
            "driverLatitude": o.driver_latitude,
            "driverLongitude": o.driver_longitude,
            "driverLocationUpdatedAt": iso(o.driver_location_updated_at),
            "fulfillmentSource": (
                FulfillmentSourceSerializer(o.fulfillment_source).data
                if o.fulfillment_source_id
                else None
            ),
            "driver": (
                {
                    "documentId": str(o.driver.document_id),
                    "fullName": o.driver.full_name,
                    "phone": o.driver.phone,
                    "vehicleType": o.driver.vehicle_type,
                }
                if o.driver_id
                else None
            ),
            "items": [OrderItemSerializer(i).data for i in o.items.all()],
        }
        if not self.public:
            payload["deliveryShareToken"] = o.delivery_share_token
        return payload


class DriverSerializer:
    def __init__(self, instance: Driver):
        self.instance = instance

    @property
    def data(self):
        d = self.instance
        return {
            "documentId": str(d.document_id),
            "fullName": d.full_name,
            "phone": d.phone,
            "vehicleType": d.vehicle_type,
            "isActive": d.is_active,
            "currentLatitude": d.current_latitude,
            "currentLongitude": d.current_longitude,
            "lastLocationAt": iso(d.last_location_at),
        }
