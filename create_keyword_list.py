import random
import string
from rest_framework.views import APIView
from django.http import JsonResponse
from apps.sponsored_links.serializers import NewKeywordList
from rest_framework import permissions, authentication
from apps.admin.views.taboola.permissions import IsDataAdmin
from django.contrib.auth.models import User
from apps.data.trafficguard.models import Categories
from apps.admin._trafficguard.campaign_wizard.utils import (
    generate_keyword_list_name,
    setup_keyword_list_from_keyword_names,
)
from apps.main_app.providers.trafficguard import get_keyword_list

class CreateKeywordList(APIView):
    """
    Creates a new Keyword List.

    Return:
        JsonResponse: Keyword List.
    """

    serializer_class = NewKeywordList
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsDataAdmin)

    def post(self, request) -> JsonResponse:

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            publisher = User.objects.get(id=serializer.data["user_id"])
            category = Categories.objects.get(id=serializer.data["category_id"])
            keyword_list_id = set_up_keyword_list(
                serializer.data["keywords"], publisher, category, serializer.data["name"]
            )

            return JsonResponse(
                get_keyword_list(keyword_list_id).get("keyword_list"),
                safe=False,
            )

        return JsonResponse(
            serializer.errors,
            safe=False,
            status=422
        )


def set_up_keyword_list(
    keywords, publisher, category, keyword_list_name, random_suffix=None
):
    """
    Creates a new Keyword List over the TG API.

    Params:
        keywords (string): keywords.
        publisher (User): The crossroads user.
        category (Category): The campaign category.
        keyword_list_name: The chosen keyword list name.
        random_suffix (bool): Generates a random string suffix if True.

    Return:
        integer: keyword list id
    """
    name = keyword_list_name

    if random_suffix:
        suffix = random.choices(string.ascii_letters, k=2)
        name = f"{name}_{suffix}"

    keyword_list_id, _ = setup_keyword_list_from_keyword_names(
        keywords,
        publisher.id,
        category.id,
        generate_keyword_list_name(publisher.username, name, category.name),
    )

    return keyword_list_id
