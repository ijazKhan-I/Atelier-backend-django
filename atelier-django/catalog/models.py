import uuid

from django.db import models


class DocumentModel(models.Model):
    """Shared id + Strapi-compatible documentId."""

    document_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(DocumentModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(DocumentModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    price = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.SET_NULL, null=True, blank=True
    )
    shipping_info = models.JSONField(blank=True, null=True)
    return_policy = models.JSONField(blank=True, null=True)
    artisan_notes = models.JSONField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(blank=True, null=True)
    subscriber_announcement_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, related_name="variations", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="Color name, e.g. Red")
    code = models.CharField(max_length=50, blank=True, default="", help_text="Hex code")
    stock = models.IntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=50, blank=True, default="")
    image = models.ImageField(upload_to="variations/", blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} / {self.name} / {self.size}"
