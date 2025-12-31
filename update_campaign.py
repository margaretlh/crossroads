import random
import string
from rest_framework.views import APIView
from django.http import JsonResponse
from apps.sponsored_links.serializers import UpdatedCampaignSerializer
from rest_framework import permissions, authentication
from apps.admin.views.taboola.permissions import IsDataAdmin
from apps.main_app.providers.trafficguard import update_campaign
from apps.data.trafficguard.models import RevenueDomains
from apps.admin._trafficguard.campaign_wizard.utils import (
    buy_domain,
    generate_keyword_list_name,
    setup_keyword_list_from_keyword_names
)
from django.contrib.auth.models import User
from apps.data.trafficguard.models import Categories


class UpdateCampaign(APIView):
    """
    Updates the campaign in TrafficGuard.

    Return:
        JsonResponse: Updated Campaign.
    """

    serializer_class = UpdatedCampaignSerializer
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsDataAdmin)

    def post(self, request) -> JsonResponse:

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            campaign = serializer.data
            publisher = User.objects.get(id=campaign["crossroads_user_id"])
            category = Categories.objects.get(id=campaign["category_ids"][0])

            for redirection_rule in campaign["redirection_rules"]:

                for list in redirection_rule["keyword_lists"]:
                    if "id" not in list:
                        keyword_list_id, _ = set_up_keyword_list(
                            list["keywords"], publisher, category, list["name"], random_suffix=True
                        )
                        list["id"] = keyword_list_id
                        redirection_rule["keyword_list_ids"].append(keyword_list_id)

                for revenue_domain in redirection_rule["revenue_domains"]:
                    # Check if this is a new revenue domain being added.
                    if "id" not in revenue_domain:
                        domain = RevenueDomains.objects.get(name=revenue_domain["name"])
                        if domain:
                            revenue_domain["id"] = domain.id
                            revenue_domain["is_https"] = True
                            revenue_domain["status"] = "active"
                        else:
                            # this is a new domain and needs to be registered.
                            register_new_domain(revenue_domain)

            response = update_campaign(serializer.data.get('id'), serializer.data).json()
            print(response)

        return JsonResponse(
            {},
            safe=False,
        )

def register_new_domain(domain, auth_user_id, publisher_id, category):
    buy_domain(
        registrar_id=domain["registrar_id"],
        domain_name=domain["name"],
        notify_user_id=auth_user_id,
        user_id=publisher_id,
        category_name=category,
        tpa_id=domain["tpa_id"],
        rev_provider_id=domain["revenue_provider_id"],
        tg_ssl=True,
        random_digit=str(random.randrange(100000, 100000000000000)),
        use_domain_parking=False,
        serp_pixel="",
        lander_pixel="",
        adclick_pixel="",
        use_imprinting=False,
        parking_contact_link_name=None,
        parking_contact_url=None,
        parking_domain_contact_info=None,
    )


def set_up_keyword_list(
    form_payload, publisher, category, keyword_list_name, random_suffix=None
):
    """
    Creates a new Keyword List over the TG API.

    Params:
        form_payload (dict): The user input.
        publisher (User): The crossroads user.
        category (Category): The campaign category.
        keyword_list_name: The chosen keyword list name.
        random_suffix (bool): Generates a random string suffix if True.

    Return:

        tuple: keyword list id and TG status.
    """
    name = keyword_list_name

    if random_suffix:
        suffix = random.choices(string.ascii_letters, k=2)
        name = f"{name}_{suffix}"

    keyword_list_id, keyword_list_status = setup_keyword_list_from_keyword_names(
        form_payload.get("keywords", ""),
        publisher.id,
        category.id,
        generate_keyword_list_name(publisher.username, name, category.name),
    )

    return keyword_list_id, keyword_list_status
