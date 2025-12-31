from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from apps.sponsored_links_reporting.models import AdContainer, AdZone
import pandas
from django.db.models import Count
from apps.main_app.helpers import df_to_list_dict


class LoadSiteZones(LoginRequiredMixin, View):
    """
    Loads a list of zones that belong to a site.

    Args:
        user_id(int): Publisher ID.
        site_id(int): Site ID.

    Return:
        JsonResponse: List of zones.
    """

    def get(self, request, user_id, site_id) -> JsonResponse:

        zones = list(
                AdZone.objects.filter(site_id=site_id).order_by("name")
            )

        zone_ids = [zone.id for zone in zones]

        zones = [{
            "id": zone.id,
            "name": zone.name,
            "status": zone.status,
            "size": f"{zone.width}x{zone.height}",
            "width": zone.width,
            "height": zone.height,
            "optimize_ads": zone.optimize_ads,
            "optimize_after_clicks": zone.optimize_after_clicks,
            "optimize_go_back_days": zone.optimize_go_back_days,
            "optimize_min_waiting_days": zone.optimize_min_waiting_days,
            "optimize_ad_level": zone.optimize_ad_level,
            "snippet_code": zone.snippet_code
        } for zone in zones]

        zones = pandas.DataFrame(
            data=zones,
            columns=["id", "name", "status", "size","width","height","optimize_ads",
                     "optimize_after_clicks", "optimize_go_back_days", "optimize_min_waiting_days",
                     "optimize_ad_level", "snippet_code"],
        )

        ad_containers = pandas.DataFrame(
            data=list(
                AdContainer.objects.values("zone_id").annotate(ad_count=Count("id"))
            ),
            columns=["zone_id", "ad_count"],
        )

        ad_containers.rename(columns={ "zone_id": "id", "ad_count": "ads" }, inplace=True)

        dataframe = pandas.merge(zones, ad_containers, on="id", how="left").fillna('0')

        return JsonResponse(
            df_to_list_dict(dataframe),
            safe=False,
        )
