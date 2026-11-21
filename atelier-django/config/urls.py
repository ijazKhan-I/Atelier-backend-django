from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from accounts.views import LocalLoginView, LocalRegisterView
from catalog.views import CategoryListView, ProductDetailView, ProductListView
from cms.views import AboutPageView, ContactPageView, HomePageView, ShopPageView
from commerce.views import (
    ContactInquirySubmitView,
    CreateOrderView,
    DeliverySessionView,
    DriverMeView,
    DriverMyOrdersView,
    DriverRegisterView,
    DriverShareLocationView,
    MyOrdersView,
    NewsletterSubscribeView,
    ShareDriverLocationPublicView,
    TrackOrderView,
)
from mediafiles.views import serve_database_media, using_database_storage

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth (Strapi-compatible)
    path("api/auth/local", LocalLoginView.as_view()),
    path("api/auth/local/register", LocalRegisterView.as_view()),
    # CMS single types
    path("api/home-page", HomePageView.as_view()),
    path("api/shop-page", ShopPageView.as_view()),
    path("api/about", AboutPageView.as_view()),
    path("api/contact-page", ContactPageView.as_view()),
    # Catalog
    path("api/products", ProductListView.as_view()),
    path("api/products/<uuid:document_id>", ProductDetailView.as_view()),
    path("api/categories", CategoryListView.as_view()),
    # Orders
    path("api/orders", CreateOrderView.as_view()),
    path("api/orders/my-orders", MyOrdersView.as_view()),
    path("api/orders/track/<str:order_number>", TrackOrderView.as_view()),
    path("api/orders/delivery-session", DeliverySessionView.as_view()),
    path("api/orders/share-driver-location", ShareDriverLocationPublicView.as_view()),
    # Drivers
    path("api/drivers/register", DriverRegisterView.as_view()),
    path("api/drivers/me", DriverMeView.as_view()),
    path("api/drivers/my-orders", DriverMyOrdersView.as_view()),
    path("api/drivers/share-location", DriverShareLocationView.as_view()),
    # Forms
    path("api/newsletter-subscribers/subscribe", NewsletterSubscribeView.as_view()),
    path("api/contact-inquiries/submit", ContactInquirySubmitView.as_view()),
]

# Neon / DB-backed media must be served in production (DEBUG=False on Vercel).
if using_database_storage():
    urlpatterns += [
        path("uploads/<path:path>", serve_database_media),
    ]
elif settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
