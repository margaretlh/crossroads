from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from apps.sponsored_links_reporting.models import Site

class ShowSiteZones(LoginRequiredMixin, View):
    """
    Shows a list of sites belonging to the publisher.

    Args:
        user_id(int): Publisher ID.
        site_id(int): Site ID.

    Return:
        TemplateResponse
    """

    def get(
        self, request, user_id, site_id, template="sponsored-links/site-zones.html"
    ) -> TemplateResponse:

        user = User.objects.get(id=user_id)
        site = Site.objects.get(id=site_id)

        return TemplateResponse(
            request,
            template=template,
            context={
                "publisher_id": user_id,
                "site_id": site_id,
                "site_name": site.name,
                "publisher_name": user.username,
            },
        )
