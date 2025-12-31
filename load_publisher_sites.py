from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from apps.sponsored_links_reporting.models import Site, AdZone
import pandas
from django.db.models import Count
from apps.main_app.helpers import df_to_list_dict

class LoadPublisherSites(LoginRequiredMixin, View):
    """
    Loads a list of sites that belong to a publisher.

    Args:
        user_id(int): Publisher ID.

    Return:
        JsonResponse: List of sites.
    """
    def get(self, request, user_id) -> JsonResponse:
        sites = pandas.DataFrame(
            data=list(
                Site.objects.filter(user_id=user_id, deleted=False)
                .values("id", "name")
                .order_by("name")
            ),
            columns=["id", "name"],
        )

        zones = pandas.DataFrame(data=list(AdZone.objects.exclude(site__deleted=True).values('site_id').annotate(zone_count=Count("id"))))
        zones.rename(columns={ "site_id": "id", "zone_count": "zones" }, inplace=True)

        dataframe = pandas.merge(sites, zones, on="id", how="left").fillna(0)

        return JsonResponse(
            df_to_list_dict(dataframe),
            safe=False,
        )
