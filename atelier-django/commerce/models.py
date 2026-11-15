import secrets
import uuid

from django.conf import settings
from django.db import models

from catalog.models import DocumentModel


class FulfillmentSource(DocumentModel):
    SOURCE_TYPES = (("store", "store"), ("warehouse", "warehouse"))

    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default="store")
    street_address = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    is_active = models.BooleanField(default=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    geohash = models.CharField(max_length=32, blank=True, default="")

    def __str__(self):
        return self.name


class Driver(DocumentModel):
    VEHICLE_TYPES = (
        ("bike", "bike"),
        ("motorcycle", "motorcycle"),
        ("car", "car"),
        ("van", "van"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="driver_profile", on_delete=models.CASCADE
    )
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default="motorcycle")
    is_active = models.BooleanField(default=True)
    current_latitude = models.FloatField(blank=True, null=True)
    current_longitude = models.FloatField(blank=True, null=True)
    last_location_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.full_name


class Order(DocumentModel):
    PAYMENT_METHODS = (("cash_on_delivery", "cash_on_delivery"),)
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("confirmed", "confirmed"),
        ("shipped", "shipped"),
        ("delivering", "delivering"),
        ("delivered", "delivered"),
        ("cancelled", "cancelled"),
    )

    order_number = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    street_address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=32)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=32, choices=PAYMENT_METHODS, default="cash_on_delivery")
    order_status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="pending")
    total = models.PositiveIntegerField(default=0)
    customer_id = models.IntegerField(blank=True, null=True, db_index=True)
    customer_username = models.CharField(max_length=150, blank=True, default="")
    driver = models.ForeignKey(
        Driver, related_name="orders", on_delete=models.SET_NULL, null=True, blank=True
    )
    fulfillment_source = models.ForeignKey(
        FulfillmentSource,
        related_name="orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tracking_map_url = models.URLField(blank=True, null=True)
    driver_latitude = models.FloatField(blank=True, null=True)
    driver_longitude = models.FloatField(blank=True, null=True)
    driver_location_updated_at = models.DateTimeField(blank=True, null=True)
    delivery_share_token = models.CharField(max_length=64, blank=True, default="", db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def ensure_delivery_share_token(self):
        if not self.delivery_share_token:
            self.delivery_share_token = secrets.token_urlsafe(24)
        return self.delivery_share_token


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_document_id = models.CharField(max_length=64, blank=True, default="")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=100, blank=True, default="")
    size = models.CharField(max_length=50, blank=True, default="")
    image_url = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        ordering = ["id"]


class ContactInquiry(DocumentModel):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("replied", "replied"),
        ("closed", "closed"),
    )

    inquiry_number = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    inquiry_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    admin_reply = models.TextField(blank=True, default="")
    replied_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "contact inquiries"
        ordering = ["-created_at"]

    def __str__(self):
        return self.inquiry_number


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email
