from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from apps.data.trafficguard.models import KeywordLists

class LoadKeywordLists(LoginRequiredMixin, View):
    """
    Loads a list of keyword lists that belong to a publisher.

    Args:
        user_id(int): Publisher ID.

    Return:
        JsonResponse: List of keyword lists.
    """

    def get(self, request, user_id: int) -> JsonResponse:
        keyword_lists = list(
            KeywordLists.objects.filter(
                crossroads_user=user_id,
                is_deleted=False
            )
            .order_by("name")
            .values("id", "name")
        )

        return JsonResponse(
            keyword_lists,
            safe=False,
        )
