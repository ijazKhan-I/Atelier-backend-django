from django.db import models

from catalog.models import DocumentModel, Product


class HomePage(DocumentModel):
    # Hero
    hero_badge = models.CharField(max_length=255, blank=True, default="Autumn / Winter 2024")
    hero_heading = models.CharField(max_length=255, blank=True, default="The Art of Stillness")
    hero_background = models.ImageField(upload_to="cms/home/", blank=True, null=True)
    hero_primary_label = models.CharField(max_length=100, default="Shop Now")
    hero_primary_href = models.CharField(max_length=255, default="/shop")
    hero_secondary_label = models.CharField(max_length=100, default="Discover More")
    hero_secondary_href = models.CharField(max_length=255, default="/about")

    # Curation primary
    curation_primary_label = models.CharField(max_length=100, default="Curation 01")
    curation_primary_heading = models.CharField(max_length=255, default="Structured Elegance")
    curation_primary_description = models.TextField(
        blank=True,
        default="Exploring the intersection of modern geometry and traditional tailoring techniques.",
    )
    curation_primary_image = models.ImageField(upload_to="cms/home/", blank=True, null=True)
    curation_primary_dark = models.BooleanField(default=False)
    curation_primary_square = models.BooleanField(default=False)

    # Curation secondary
    curation_secondary_label = models.CharField(max_length=100, default="Curation 02")
    curation_secondary_heading = models.CharField(max_length=255, default="The Minimalist Essential")
    curation_secondary_description = models.TextField(
        blank=True, default="Timeless pieces designed for the discerning individual."
    )
    curation_secondary_image = models.ImageField(upload_to="cms/home/", blank=True, null=True)
    curation_secondary_dark = models.BooleanField(default=True)
    curation_secondary_square = models.BooleanField(default=True)

    # Trending
    trending_heading = models.CharField(max_length=255, default="Trending Now")
    trending_description = models.TextField(
        blank=True, default="The season's most-coveted silhouettes."
    )
    trending_products = models.ManyToManyField(Product, blank=True, related_name="trending_on_home")

    # Philosophy
    philosophy_label = models.CharField(max_length=100, default="Our Philosophy")
    philosophy_quote = models.TextField(
        blank=True, default='"Beauty lies in the omission of the unnecessary."'
    )
    philosophy_description = models.TextField(
        blank=True,
        default=(
            "Every Atelier piece is a dialogue between heritage craftsmanship and the modern silhouette. "
            "We believe in clothes that tell a story without saying a word."
        ),
    )
    philosophy_link_label = models.CharField(max_length=100, default="The Atelier Journal")
    philosophy_link_url = models.CharField(max_length=255, default="/about")
    philosophy_image = models.ImageField(upload_to="cms/home/", blank=True, null=True)

    # Newsletter
    newsletter_heading = models.CharField(max_length=255, default="Join the Circle")
    newsletter_description = models.TextField(
        blank=True,
        default="Receive early access to seasonal lookbooks and private collection releases.",
    )
    newsletter_placeholder = models.CharField(max_length=100, default="EMAIL ADDRESS")
    newsletter_submit = models.CharField(max_length=100, default="Subscribe")

    class Meta:
        verbose_name = "Home page"
        verbose_name_plural = "Home page"

    def __str__(self):
        return "Home page"


class ShopPage(DocumentModel):
    hero_badge = models.CharField(max_length=255, blank=True, default="The Collection")
    hero_heading = models.TextField(blank=True, default="Shop the\nSeason")
    hero_description = models.TextField(blank=True, default="")
    hero_link_label = models.CharField(max_length=100, blank=True, default="")
    hero_link_url = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "Shop page"
        verbose_name_plural = "Shop page"

    def __str__(self):
        return "Shop page"


class AboutPage(DocumentModel):
    hero_title = models.CharField(max_length=255, default="About Atelier")
    hero_subtitle = models.TextField(blank=True, default="")
    hero_background = models.ImageField(upload_to="cms/about/", blank=True, null=True)

    heritage_title = models.CharField(max_length=255, default="Our Heritage")
    heritage_paragraph_one = models.TextField(blank=True, default="")
    heritage_paragraph_two = models.TextField(blank=True, default="")

    process_label = models.CharField(max_length=100, default="Process")
    process_title = models.CharField(max_length=255, default="")
    process_description = models.TextField(blank=True, default="")
    process_link_label = models.CharField(max_length=100, blank=True, default="")
    process_link_url = models.CharField(max_length=255, blank=True, default="")
    process_image = models.ImageField(upload_to="cms/about/", blank=True, null=True)
    process_card_label = models.CharField(max_length=100, blank=True, default="")
    process_card_quote = models.TextField(blank=True, default="")

    pillars_heading = models.CharField(max_length=255, blank=True, default="Pillars")

    uniform_title = models.CharField(max_length=255, blank=True, default="")
    uniform_description = models.TextField(blank=True, default="")
    uniform_left_image = models.ImageField(upload_to="cms/about/", blank=True, null=True)
    uniform_right_image = models.ImageField(upload_to="cms/about/", blank=True, null=True)

    class Meta:
        verbose_name = "About page"
        verbose_name_plural = "About page"

    def __str__(self):
        return "About page"


class AboutPillar(models.Model):
    STYLE_CHOICES = (("white", "white"), ("black", "black"), ("gray", "gray"))

    about_page = models.ForeignKey(AboutPage, related_name="pillars", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default="white")
    image = models.ImageField(upload_to="cms/about/pillars/", blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]


class ContactPage(DocumentModel):
    title = models.CharField(max_length=255, default="Contact")
    description = models.TextField(blank=True, default="")
    office_image = models.ImageField(upload_to="cms/contact/", blank=True, null=True)

    form_name_label = models.CharField(max_length=100, default="Name")
    form_name_placeholder = models.CharField(max_length=100, default="Your name")
    form_email_label = models.CharField(max_length=100, default="Email")
    form_email_placeholder = models.CharField(max_length=100, default="you@example.com")
    form_message_label = models.CharField(max_length=100, default="Message")
    form_message_placeholder = models.CharField(max_length=255, default="How can we help?")
    form_submit_label = models.CharField(max_length=100, default="Send")

    direct_heading = models.CharField(max_length=100, default="Direct")
    direct_email = models.EmailField(blank=True, default="hello@atelier.local")
    direct_phone = models.CharField(max_length=50, blank=True, default="")
    socials_heading = models.CharField(max_length=100, default="Social")

    locations_heading = models.CharField(max_length=100, blank=True, default="Locations")

    class Meta:
        verbose_name = "Contact page"
        verbose_name_plural = "Contact page"

    def __str__(self):
        return "Contact page"


class ContactSocialLink(models.Model):
    contact_page = models.ForeignKey(ContactPage, related_name="social_links", on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    url = models.URLField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]


class ContactStoreLocation(models.Model):
    contact_page = models.ForeignKey(ContactPage, related_name="locations", on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="")
    hours_label = models.CharField(max_length=100, blank=True, default="Hours")
    hours_time = models.CharField(max_length=100, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
