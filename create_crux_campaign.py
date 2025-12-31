from datetime import datetime
from apps.data.trafficguard.models import Campaigns, Categories, RevenueDomains, RevenueProviders
from apps.sponsored_links_reporting.models import TrafficGuardCampaign
from apps.sponsored_links_reporting.models import Category
from apps.main_app.providers.trafficguard import create_domain, create_campaign, add_user_to_domain

class CreateCruxCampaign:

    def __init__(self, tg_campaign: dict, form_data: dict) -> None:
        """
        Dedicated class for spawning new Sponsored Links Campaigns.

        Args:
            tg_campaign (dict): The original trafficguard campaign.
            form_data (dict): The raw user form input.
        """
        self.tg_campaign = tg_campaign
        self.form_data = form_data
        self.revenue_provider_id = (
            RevenueProviders.objects.get(name="AIM Content SL Page").id
        )

    def open_campaign(self, article_path: str) -> None:
        """
        Creates a new Sponsored Links Campaign.
        """
        # We need to create a keyword list.
        category = Categories.objects.get(id=self.tg_campaign["category_ids"][0])

        self.create_revenue_domain(self.tg_campaign["crossroads_user_id"], article_path.strip())

        routing_domain = self.form_data["sponsored_links"]["routing_domain"]

        campaign = {
            "name": f"{self.form_data['name']}",
            "status": "active",
            "https": True,
            "start_date": datetime.today().strftime("%Y-%m-%d"),
            "no_cloaking": True,
            "category_ids": [category.id],
            "routing_domain": {
                "default_domain": routing_domain,
                "name": routing_domain,
                "is_https": 1,
                "status": "active",
            },
            "type": Campaigns.TYPE_CRUX_ARB_TYPE,
            "passthrough_parameters": self.form_data["passthrough_parameters"],
            "crossroads_user_id": self.tg_campaign["crossroads_user_id"],
            "redirection_rules": [
                {
                    "keyword_list_ids": [],
                    "status": "active",
                    "device_type": "",
                    "country_codes": "",
                    "status": "active",
                    "use_keyword_list": False,
                    "keyword_lists": [],
                    "revenue_domains": [
                        {
                            "name": article_path,
                            "percentage": 100,
                            "revenue_provider_id": self.revenue_provider_id,
                            "status": "active",
                            "is_https": True,
                        }
                    ],
                    "safe_domain": {
                        "name": self.form_data.get("safe_domain", "primeinfospot.com"),
                        "status": "active",
                    },
                }
            ],
        }

        response = create_campaign(campaign)

        response_json = response.json()

        if response_json["valid"]:
            _campaign = response_json["campaign"]
            return _campaign

    @staticmethod
    def create_tg_campaign(name: str, campaign: dict, category: Category) -> TrafficGuardCampaign:

        sponsored_links_campaign = TrafficGuardCampaign.objects.create(
            id=campaign["id"],
            name=name,
            user_id=campaign["crossroads_user_id"],
            routing_domain=campaign["traffic_source_urls"]["11"]
        )

        sponsored_links_campaign.categories.add(category)

        return sponsored_links_campaign

    def create_revenue_domain(self, user_id: int, crux_article_url: str = None):
        status, domain = create_domain(
            crux_article_url,
            self.revenue_provider_id,
            [user_id],
        )

        if status == "error":
            domain = RevenueDomains.objects.get(name=crux_article_url)

            if user_id not in domain.get_crossroad_user_ids():
                add_user_to_domain(domain.id, user_id)

            return domain.name

        return crux_article_url
