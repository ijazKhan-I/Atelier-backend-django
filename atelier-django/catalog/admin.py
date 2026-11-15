from django.contrib import admin

from .models import Category, Product, ProductImage, ProductVariation


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "document_id")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "is_published", "document_id")
    list_filter = ("is_published", "category")
    search_fields = ("name", "description")
    inlines = [ProductImageInline, ProductVariationInline]
    autocomplete_fields = ("category",)
