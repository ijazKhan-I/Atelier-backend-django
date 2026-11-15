from rest_framework import serializers

from .media import serialize_image
from .models import Category, Product, ProductImage, ProductVariation


def iso(dt):
    return dt.isoformat().replace("+00:00", "Z") if dt else None


class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = ("id", "name", "code", "stock", "price", "size", "image")

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "code": instance.code,
            "stock": instance.stock,
            "price": instance.price,
            "size": instance.size,
            "image": serialize_image(instance.image, obj_id=instance.id),
        }


class CategoryBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "document_id", "name", "slug", "image")

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "documentId": str(instance.document_id),
            "createdAt": iso(instance.created_at),
            "updatedAt": iso(instance.updated_at),
            "publishedAt": iso(instance.created_at),
            "name": instance.name,
            "slug": instance.slug,
            "image": serialize_image(instance.image, obj_id=instance.id, document_id=str(instance.document_id)),
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance: Product):
        images = [
            serialize_image(img.image, obj_id=img.id)
            for img in instance.images.all()
            if img.image
        ]
        return {
            "id": instance.id,
            "documentId": str(instance.document_id),
            "description": instance.description,
            "createdAt": iso(instance.created_at),
            "updatedAt": iso(instance.updated_at),
            "publishedAt": iso(instance.published_at or instance.created_at),
            "name": instance.name,
            "price": instance.price,
            "shipping_info": instance.shipping_info,
            "return_policy": instance.return_policy,
            "artisan_notes": instance.artisan_notes,
            "productVariation": ProductVariationSerializer(instance.variations.all(), many=True).data,
            "image": images,
            "category": CategoryBriefSerializer(instance.category).data if instance.category else None,
        }


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    def to_representation(self, instance: Category):
        data = CategoryBriefSerializer(instance).data
        include_products = self.context.get("include_products", True)
        if include_products:
            products = instance.products.filter(is_published=True)
            data["products"] = ProductSerializer(products, many=True).data
        return data
