from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from apps.data.trafficguard.models import RevenueProviders

class LoadRevenueProviders(LoginRequiredMixin, View):
    """
    Loads a list of revenue providers.

    Return:
        JsonResponse: List of revenue providers.
    """

    def get(self, request) -> JsonResponse:

        return JsonResponse(
            list(
                RevenueProviders.objects.filter(is_deleted=False)
                .order_by("name")
                .values("id", "name")
            ),
            safe=False,
        )
