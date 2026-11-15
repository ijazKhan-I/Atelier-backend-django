from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AboutPage, ContactPage, HomePage, ShopPage
from .serializers import (
    AboutPageSerializer,
    ContactPageSerializer,
    HomePageSerializer,
    ShopPageSerializer,
)


def single_or_404(model, serializer_cls):
    instance = model.objects.order_by("id").first()
    if not instance:
        return Response({"data": None, "meta": {}})
    return Response({"data": serializer_cls(instance).data, "meta": {}})


class HomePageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return single_or_404(HomePage, HomePageSerializer)


class ShopPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return single_or_404(ShopPage, ShopPageSerializer)


class AboutPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return single_or_404(AboutPage, AboutPageSerializer)


class ContactPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return single_or_404(ContactPage, ContactPageSerializer)
