from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from apps.data.trafficguard.models import RevenueDomains

class LoadPublisherRevenueDomains(LoginRequiredMixin, View):
    """
    Loads a list of revenue domains that belong to a publisher.

    Args:
        user_id(int): Publisher ID.

    Return:
        JsonResponse: List of revenue domains.
    """

    def get(self, request, user_id) -> JsonResponse:
        domains = list(
            RevenueDomains.objects.filter(
                is_deleted=False, name__icontains=request.GET.get("search", "")
            )
            .filter(crossroads_user_ids__regex=r"(\[|,){}(\]|,)".format(user_id))
            .exclude(crossroads_user_ids=None)
            .exclude(crossroads_user_ids="[]")
            .values("name", "revenue_provider_id", "id")
            .order_by("name")
        )

        return JsonResponse(
            domains,
            safe=False,
        )
