from apps.data.trafficguard.models import RoutingDomains
from apps.data.models import UserProfile
from apps.admin._trafficguard.campaign_wizard.utils import (
    publisher_only_access,
)
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


class LoadPublisherRoutingDomains(LoginRequiredMixin, View):

    def get(self, request, user_id):
        """
        Returns a list of routing domains that belong to the Publisher.

        Args:
            user_id(int): The publisher ID.

        Return:
            JsonResponse: A list of routing domains.
        """

        publisher_profile = UserProfile.objects.get(owner=user_id)

        domains = RoutingDomains.objects.filter(
            Q(crossroads_user_ids="[{}]".format(publisher_profile.owner_id))
            | Q(crossroads_user_ids__contains=",{}]".format(publisher_profile.owner_id))
            | Q(crossroads_user_ids__contains=",{},".format(publisher_profile.owner_id))
            | Q(
                crossroads_user_ids__contains="[{},".format(publisher_profile.owner_id)
            ),
            is_deleted=False,
        )
        if (
            publisher_only_access(request.user)
            and publisher_profile.default_routing_domain_id
        ):
            domains = domains.filter(id=publisher_profile.default_routing_domain_id)
        rows = []
        for d in domains:
            if publisher_profile.owner_id in d.get_crossroads_user_ids():
                rows.append(
                    {
                        "id": d.id,
                        "name": d.name,
                        "default_domain": d.default_domain,
                        "https": d.is_https,
                    }
                )

        return JsonResponse(rows, safe=False)
