from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from apps.sponsored_links_reporting.models import (
    TrafficGuardCampaign,
    AdContainer,
    AdZone,
)
from django.db.models import Prefetch, Subquery
from apps.data.trafficguard.models import (
    RevenueDomains,
    RedirectionRules,
    RedirectionRuleRevenueDomains,
)

class LoadPublisherCampaigns(LoginRequiredMixin, View):
    """
    Loads a list of publisher sponsored links campaigns.

    Args:
        user_id(int): Publisher ID.

    Return:
        JsonResponse: List of campaigns.
    """

    def get(self, request, user_id: int) -> JsonResponse:

        zone_prefetch = Prefetch(
            "zone", queryset=AdZone.objects.select_related("site")
        )

        # Prefetch adcontainer with the zone prefetch
        ad_container_prefetch = Prefetch(
            "adcontainer_set", queryset=AdContainer.objects.prefetch_related(zone_prefetch)
        )

        # Fetch TrafficGuardCampaigns with the necessary related objects
        tg_campaigns = list(
            TrafficGuardCampaign.objects.filter(
                user_id=user_id,
                is_deleted=False,
                version=TrafficGuardCampaign.VERSION_1,
            )
            .prefetch_related(
                "categories", ad_container_prefetch
            )
            .order_by("name")
        )
        campaigns = []

        for campaign in tg_campaigns:

            category = campaign.categories.first()
            ad_containers = campaign.adcontainer_set.all()

            redirection_rules = RedirectionRules.objects.filter(campaign_id=campaign.id)

            # Step 2: Extract the revenue_domain_ids and filter RevenueDomains
            # Here we assume revenue_domain_ids are stored as comma-separated values in a text field
            revenue_domain_names = RevenueDomains.objects.filter(
                id__in=Subquery(
                    RedirectionRuleRevenueDomains.objects.filter(
                        redirection_rule__in=redirection_rules
                    ).values('revenue_domain_id')
                )
            ).values_list('name', flat=True)

            sites = ''
            zones = ''

            for container in ad_containers:
                sites = f"{sites} {container.zone.site.name}"
                zones = f"{zones} {container.zone.name}"

            for domain in revenue_domain_names:
                sites = f"{sites} {domain}"

            _campaign = {
                "id": campaign.id,
                "name": campaign.name,
                "routing_domain": campaign.routing_domain,
                "category": category.name if category else None,
                "site": sites,
                "zone": zones,
            }

            campaigns.append(_campaign)

        return JsonResponse(campaigns, safe=False)
