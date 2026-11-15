from django.contrib import admin

from .models import (
    AboutPage,
    AboutPillar,
    ContactPage,
    ContactSocialLink,
    ContactStoreLocation,
    HomePage,
    ShopPage,
)


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    filter_horizontal = ("trending_products",)


@admin.register(ShopPage)
class ShopPageAdmin(admin.ModelAdmin):
    pass


class AboutPillarInline(admin.TabularInline):
    model = AboutPillar
    extra = 0


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    inlines = [AboutPillarInline]


class ContactSocialInline(admin.TabularInline):
    model = ContactSocialLink
    extra = 0


class ContactLocationInline(admin.TabularInline):
    model = ContactStoreLocation
    extra = 0


@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):
    inlines = [ContactSocialInline, ContactLocationInline]
