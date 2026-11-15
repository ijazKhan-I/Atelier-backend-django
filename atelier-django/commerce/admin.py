from django.contrib import admin

from .models import (
    ContactInquiry,
    Driver,
    FulfillmentSource,
    NewsletterSubscriber,
    Order,
    OrderItem,
)
from .stock import restore_stock


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "email", "order_status", "total", "created_at")
    list_filter = ("order_status", "payment_method")
    search_fields = ("order_number", "email", "first_name", "last_name")
    inlines = [OrderItemInline]
    readonly_fields = ("document_id", "delivery_share_token", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = Order.objects.filter(pk=obj.pk).values_list("order_status", flat=True).first()

        if obj.order_status == "delivering":
            obj.ensure_delivery_share_token()

        super().save_model(request, obj, form, change)

        if change and previous_status != "cancelled" and obj.order_status == "cancelled":
            items = [
                {
                    "productDocumentId": i.product_document_id,
                    "quantity": i.quantity,
                    "color": i.color,
                    "size": i.size,
                }
                for i in obj.items.all()
            ]
            restore_stock(items)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "vehicle_type", "is_active", "user")
    search_fields = ("full_name", "phone", "user__username")


@admin.register(FulfillmentSource)
class FulfillmentSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "source_type", "city", "is_active")


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("inquiry_number", "name", "email", "inquiry_status", "created_at")
    list_filter = ("inquiry_status",)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    search_fields = ("email",)
