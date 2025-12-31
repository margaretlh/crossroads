"""This module contains the Sponsored Links Domains loading class."""

from rest_framework.request import HttpRequest

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.data.trafficguard.models import RoutingDomains


class LoadSponsoredLinksRoutingDomains(LoginRequiredMixin, View):
    """
    Loads a list of routing domains for sponsored links campaigns.

    Return:
        JsonResponse: List of routing domains.
    """

    def get(self, request: HttpRequest) -> JsonResponse:  # noqa: ARG002
        """Returns the available RoutingDomain objects."""
        domains = list(
            RoutingDomains.objects.filter(
                is_deleted=False,
                name__in=["spls.crossroads.ai"],
            )
            .values("name", "id", "default_domain", "is_https")
            .order_by("name")
        )

        return JsonResponse(
            domains,
            safe=False,
        )
