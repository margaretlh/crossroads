from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from apps.sponsored_links_reporting.models import Site, AdZone


class ShowZoneAds(LoginRequiredMixin, View):
    """
    Shows a list of ads belonging to the zone.

    Args:
        user_id(int): Publisher ID.
        site_id(int): Site ID.
        zone_id(int): AdZone ID.

    Return:
        TemplateResponse
    """

    def get(
        self, request, user_id, site_id, zone_id,template="sponsored-links/zone-ads.html"
    ) -> TemplateResponse:

        user = User.objects.get(id=user_id)
        site = Site.objects.get(id=site_id)
        zone = AdZone.objects.get(id=zone_id)

        return TemplateResponse(
            request,
            template=template,
            context={
                "publisher_id": user_id,
                "site_id": site_id,
                "site_name": site.name,
                "zone_id": zone_id,
                "zone_name": zone.name,
                "publisher_name": user.username,
            },
        )
