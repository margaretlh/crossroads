from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from apps.sponsored_links_reporting.models import AdContainer, Ad
import pandas
from django.db.models import Count
from apps.main_app.helpers import df_to_list_dict


class LoadZoneAds(LoginRequiredMixin, View):
    """
    Loads a list of zones that belong to a site.

    Args:
        user_id(int): Publisher ID.
        site_id(int): Site ID.
        zone_id(int): AdZone ID.

    Return:
        JsonResponse: List of AdZones.
    """

    def get(self, request, user_id, site_id, zone_id) -> JsonResponse:

        ad_containers = AdContainer.objects.filter(zone_id=zone_id)
        ad_containers = [
            {
                "id": container.id,
                "name": container.name,
                "title": container.title,
                "zone_id": container.zone.id
            }
            for container in ad_containers
        ]
        container_ids = [container['id'] for container in ad_containers]

        ads = pandas.DataFrame(
            data=list(
                Ad.objects.filter(container_id__in=container_ids)
                .values("container_id")
                .annotate(ad_count=Count("id"))
            ),
            columns=["container_id", "ad_count"],
        )

        ads.rename(columns={ "container_id": "id", "ad_count": "ads" }, inplace=True)

        ad_containers = pandas.DataFrame(
            data=ad_containers,
            columns=["id", "name", "title", "keywords", "zone_id"],
        )

        dataframe = pandas.merge(ad_containers, ads, on="id", how="left").fillna(0)

        return JsonResponse(
            df_to_list_dict(dataframe),
            safe=False,
        )
