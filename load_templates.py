from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import Template


class LoadTemplates(LoginRequiredMixin, View):
    """
    Loads a list of templates related to the user.

    Return:
        JsonResponse: List of sites.
    """
    def get(self, request) -> JsonResponse:
        templates = list(Template.objects
                 .annotate(owner_name=F("owner__username"), created_by_name=F("created_by__username"))
                 .values("id", "name", "filename", "path", "width", "height", "links", "private", "owner_name",
                         "created_by_name", "created", "deleted", "snippet", "snippet_variables")
                         )

        return JsonResponse(templates, safe=False)
