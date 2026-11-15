from django.db.models import Prefetch
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product
from .pagination import StrapiPagination
from .serializers import CategorySerializer, ProductSerializer


def product_queryset():
    return (
        Product.objects.filter(is_published=True)
        .select_related("category")
        .prefetch_related("images", "variations")
    )


def apply_strapi_sort(qs, request):
    sort = request.query_params.get("sort[0]") or request.query_params.get("sort") or "createdAt:desc"
    mapping = {
        "createdAt:desc": "-created_at",
        "createdAt:asc": "created_at",
        "price:asc": "price",
        "price:desc": "-price",
        "name:asc": "name",
        "name:desc": "-name",
    }
    return qs.order_by(mapping.get(sort, "-created_at"))


def apply_product_filters(qs, request):
    category_slug = request.query_params.get("filters[category][slug][$eq]")
    size = request.query_params.get("filters[productVariation][size][$eq]")
    color = request.query_params.get("filters[productVariation][name][$eq]")
    min_price = request.query_params.get("filters[price][$between][0]")
    max_price = request.query_params.get("filters[price][$between][1]")
    gte = request.query_params.get("filters[price][$gte]")
    lte = request.query_params.get("filters[price][$lte]")

    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if size:
        qs = qs.filter(variations__size__iexact=size)
    if color:
        qs = qs.filter(variations__name__iexact=color)
    if min_price is not None and max_price is not None:
        qs = qs.filter(price__gte=min_price, price__lte=max_price)
    if gte is not None:
        qs = qs.filter(price__gte=gte)
    if lte is not None:
        qs = qs.filter(price__lte=lte)

    return qs.distinct()


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = apply_strapi_sort(apply_product_filters(product_queryset(), request), request)
        paginator = StrapiPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = ProductSerializer(page, many=True).data
        return paginator.get_paginated_response(data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, document_id):
        try:
            product = product_queryset().get(document_id=document_id)
        except (Product.DoesNotExist, ValueError):
            return Response({"error": {"message": "Product not found"}}, status=404)
        return Response({"data": ProductSerializer(product).data, "meta": {}})


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Category.objects.all().prefetch_related(
            Prefetch("products", queryset=product_queryset())
        )
        slug = request.query_params.get("filters[slug][$eq]")
        if slug:
            qs = qs.filter(slug=slug)

        size = request.query_params.get("filters[products][productVariation][size][$eq]")
        color = request.query_params.get("filters[products][productVariation][name][$eq]")
        # Nested product filters applied in serializer via queryset prefetch already;
        # further filter products when needed:
        categories = list(qs)
        serializer = CategorySerializer(categories, many=True, context={"include_products": True})
        data = serializer.data

        if size or color:
            filtered = []
            for cat in data:
                products = cat.get("products") or []
                if size:
                    products = [
                        p
                        for p in products
                        if any(
                            (v.get("size") or "").lower() == size.lower()
                            for v in (p.get("productVariation") or [])
                        )
                    ]
                if color:
                    products = [
                        p
                        for p in products
                        if any(
                            (v.get("name") or "").lower() == color.lower()
                            for v in (p.get("productVariation") or [])
                        )
                    ]
                cat = {**cat, "products": products}
                filtered.append(cat)
            data = filtered

        return Response(
            {
                "data": data,
                "meta": {
                    "pagination": {
                        "page": 1,
                        "pageSize": len(data),
                        "pageCount": 1,
                        "total": len(data),
                    }
                },
            }
        )
