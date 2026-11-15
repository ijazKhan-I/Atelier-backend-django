from catalog.media import serialize_image
from catalog.serializers import ProductSerializer, iso

from .models import AboutPage, ContactPage, HomePage, ShopPage


def button(label, href, variant="primary"):
    return {"buttonLabel": label, "buttonHref": href, "variant": variant}


class HomePageSerializer:
    def __init__(self, instance: HomePage):
        self.instance = instance

    @property
    def data(self):
        p = self.instance
        return {
            "id": p.id,
            "documentId": str(p.document_id),
            "createdAt": iso(p.created_at),
            "updatedAt": iso(p.updated_at),
            "trendingHeading": p.trending_heading,
            "trendingDescription": p.trending_description,
            "hero": {
                "id": 1,
                "badge": p.hero_badge,
                "heading": p.hero_heading,
                "backgroundImage": serialize_image(p.hero_background, obj_id=1),
                "primaryButton": button(p.hero_primary_label, p.hero_primary_href, "primary"),
                "secondaryButton": button(p.hero_secondary_label, p.hero_secondary_href, "outline"),
            },
            "curationPrimary": {
                "id": 1,
                "label": p.curation_primary_label,
                "heading": p.curation_primary_heading,
                "description": p.curation_primary_description,
                "image": serialize_image(p.curation_primary_image, obj_id=1),
                "darkBackground": p.curation_primary_dark,
                "squareImage": p.curation_primary_square,
            },
            "curationSecondary": {
                "id": 2,
                "label": p.curation_secondary_label,
                "heading": p.curation_secondary_heading,
                "description": p.curation_secondary_description,
                "image": serialize_image(p.curation_secondary_image, obj_id=2),
                "darkBackground": p.curation_secondary_dark,
                "squareImage": p.curation_secondary_square,
            },
            "philosophy": {
                "id": 1,
                "label": p.philosophy_label,
                "quote": p.philosophy_quote,
                "description": p.philosophy_description,
                "linkLabel": p.philosophy_link_label,
                "linkUrl": p.philosophy_link_url,
                "image": serialize_image(p.philosophy_image, obj_id=1),
            },
            "newsletter": {
                "id": 1,
                "heading": p.newsletter_heading,
                "description": p.newsletter_description,
                "inputPlaceholder": p.newsletter_placeholder,
                "submitLabel": p.newsletter_submit,
            },
            "trendingProducts": ProductSerializer(p.trending_products.filter(is_published=True), many=True).data,
        }


class ShopPageSerializer:
    def __init__(self, instance: ShopPage):
        self.instance = instance

    @property
    def data(self):
        p = self.instance
        return {
            "id": p.id,
            "documentId": str(p.document_id),
            "createdAt": iso(p.created_at),
            "updatedAt": iso(p.updated_at),
            "hero": {
                "id": 1,
                "badge": p.hero_badge,
                "heading": p.hero_heading,
                "description": p.hero_description,
                "linkLabel": p.hero_link_label,
                "linkUrl": p.hero_link_url,
            },
        }


class AboutPageSerializer:
    def __init__(self, instance: AboutPage):
        self.instance = instance

    @property
    def data(self):
        p = self.instance
        return {
            "id": p.id,
            "documentId": str(p.document_id),
            "createdAt": iso(p.created_at),
            "updatedAt": iso(p.updated_at),
            "pillarsHeading": p.pillars_heading,
            "hero": {
                "id": 1,
                "title": p.hero_title,
                "subtitle": p.hero_subtitle,
                "backgroundImage": serialize_image(p.hero_background, obj_id=1),
            },
            "heritage": {
                "id": 1,
                "title": p.heritage_title,
                "paragraphOne": p.heritage_paragraph_one,
                "paragraphTwo": p.heritage_paragraph_two,
            },
            "process": {
                "id": 1,
                "label": p.process_label,
                "title": p.process_title,
                "description": p.process_description,
                "linkLabel": p.process_link_label,
                "linkUrl": p.process_link_url,
                "image": serialize_image(p.process_image, obj_id=1),
                "cardLabel": p.process_card_label,
                "cardQuote": p.process_card_quote,
            },
            "pillars": [
                {
                    "id": pillar.id,
                    "title": pillar.title,
                    "description": pillar.description,
                    "style": pillar.style,
                    "image": serialize_image(pillar.image, obj_id=pillar.id),
                }
                for pillar in p.pillars.all()
            ],
            "uniform": {
                "id": 1,
                "title": p.uniform_title,
                "description": p.uniform_description,
                "leftImage": serialize_image(p.uniform_left_image, obj_id=1),
                "rightImage": serialize_image(p.uniform_right_image, obj_id=2),
            },
        }


class ContactPageSerializer:
    def __init__(self, instance: ContactPage):
        self.instance = instance

    @property
    def data(self):
        p = self.instance
        return {
            "id": p.id,
            "documentId": str(p.document_id),
            "createdAt": iso(p.created_at),
            "updatedAt": iso(p.updated_at),
            "title": p.title,
            "description": p.description,
            "officeImage": serialize_image(p.office_image, obj_id=1),
            "locationsHeading": p.locations_heading,
            "form": {
                "id": 1,
                "nameLabel": p.form_name_label,
                "namePlaceholder": p.form_name_placeholder,
                "emailLabel": p.form_email_label,
                "emailPlaceholder": p.form_email_placeholder,
                "messageLabel": p.form_message_label,
                "messagePlaceholder": p.form_message_placeholder,
                "submitLabel": p.form_submit_label,
            },
            "directContact": {
                "id": 1,
                "directHeading": p.direct_heading,
                "email": p.direct_email,
                "phone": p.direct_phone,
                "socialsHeading": p.socials_heading,
            },
            "socialLinks": [
                {"id": s.id, "label": s.label, "url": s.url} for s in p.social_links.all()
            ],
            "locations": [
                {
                    "id": loc.id,
                    "city": loc.city,
                    "address": loc.address,
                    "country": loc.country,
                    "hoursLabel": loc.hours_label,
                    "hoursTime": loc.hours_time,
                }
                for loc in p.locations.all()
            ],
        }
