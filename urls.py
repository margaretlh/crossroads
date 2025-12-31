from django.urls import path
from apps.sponsored_links.show_publishers import ShowPublishers
from apps.sponsored_links.load_publishers import LoadPublishers
from apps.sponsored_links.show_publisher_campaigns import ShowPublisherCampaigns
from apps.sponsored_links.load_publisher_campaigns import LoadPublisherCampaigns
from apps.sponsored_links.show_campaign import ShowCampaignManager
from apps.sponsored_links.load_campaign import LoadCampaign
from apps.sponsored_links.load_revenue_providers import LoadRevenueProviders
from apps.sponsored_links.show_publisher_sites import ShowPublisherSites
from apps.sponsored_links.load_publisher_sites import LoadPublisherSites
from apps.sponsored_links.show_site_zones import ShowSiteZones
from apps.sponsored_links.load_site_zones import LoadSiteZones
from apps.sponsored_links.load_templates import LoadTemplates
from apps.sponsored_links.load_template_sizes import LoadTemplateSizes
from apps.sponsored_links.load_template_html import LoadTemplateHtml
from apps.sponsored_links.load_owners import LoadOwners
from apps.sponsored_links.show_templates import ShowTemplates
from apps.sponsored_links.create_template import CreateTemplate
from apps.sponsored_links.update_template import UpdateTemplate
from apps.sponsored_links.delete_template import DeleteTemplate
from apps.sponsored_links.load_zone_ads import LoadZoneAds
from apps.sponsored_links.load_zone_ad_html import LoadZoneAdHtml
from apps.sponsored_links.clone_zone_ad import CloneZoneAd
from apps.sponsored_links.delete_zone_ad import DeleteZoneAd
from apps.sponsored_links.show_zone_ads import ShowZoneAds
from apps.sponsored_links.create_zone import CreateZone
from apps.sponsored_links.clone_zone import CloneZone
from apps.sponsored_links.delete_zone import DeleteZone
from apps.sponsored_links.edit_zone import EditZone
from apps.sponsored_links.load_zone_serving_code import LoadZoneServingCode
from apps.sponsored_links.load_keywords import LoadKeywords
from apps.sponsored_links.load_ad_data import LoadAdData
from apps.sponsored_links.update_keywords import UpdateKeywords
from apps.sponsored_links.load_publisher_revenue_domains import LoadPublisherRevenueDomains
from apps.sponsored_links.update_campaign import UpdateCampaign
from apps.sponsored_links.create_keyword_list import CreateKeywordList
from apps.sponsored_links.load_keyword_lists import LoadKeywordLists
from apps.sponsored_links.update_site_name import UpdateSiteName
from apps.sponsored_links.delete_site import DeleteSite
from apps.sponsored_links.load_sponsored_links_routing_domains import LoadSponsoredLinksRoutingDomains
from apps.sponsored_links.show_create_campaign import ShowCreateCampaign
from apps.sponsored_links.create_ad import CreateAd
from apps.sponsored_links.create_campaign import CreateCampaign
from apps.sponsored_links.load_publisher_routing_domains import LoadPublisherRoutingDomains

app_name = "sponsored_links"

urlpatterns = [
    path(
        "publishers/",
        ShowPublishers.as_view(),
        name="sponsored-links-publishers",
    ),
    path(
        "load-publishers/",
        LoadPublishers.as_view(),
        name="sponsored-links-load-publishers",
    ),
    path(
        "publisher/<int:user_id>/campaigns/",
        ShowPublisherCampaigns.as_view(),
        name="sponsored-links-publisher-campaigns",
    ),
    path(
        "publisher/<int:user_id>/load-campaigns/",
        LoadPublisherCampaigns.as_view(),
        name="sponsored-links-load-publisher-campaigns",
    ),
    path(
        "publisher/<int:user_id>/campaigns/<int:campaign_id>/",
        ShowCampaignManager.as_view(),
        name="sponsored-links-show-campaign-manager",
    ),
    path(
        "campaigns/<int:campaign_id>/load/",
        LoadCampaign.as_view(),
        name="sponsored-links-load-campaign-manager",
    ),
    path(
        "revenue-providers/",
        LoadRevenueProviders.as_view(),
        name="sponsored-links-load-revenue-providers",
    ),
    path(
        "routing-domains/",
        LoadSponsoredLinksRoutingDomains.as_view(),
        name="sponsored-links-load-routing-domains",
    ),
    path(
        "publisher/<int:user_id>/sites/",
        ShowPublisherSites.as_view(),
        name="sponsored-links-publisher-sites",
    ),
    path(
        "publisher/<int:user_id>/load-sites/",
        LoadPublisherSites.as_view(),
        name="sponsored-links-load-publisher-sites",
    ),
    path(
        "publisher/<int:user_id>/sites/<int:site_id>/zones/",
        ShowSiteZones.as_view(),
        name="sponsored-links-site-zones",
    ),
    path(
        "publisher/<int:user_id>/sites/<int:site_id>/load-zones/",
        LoadSiteZones.as_view(),
        name="sponsored-links-site-zones",
    ),
    path(
        "publisher/<int:user_id>/sites/<int:site_id>/zones/<int:zone_id>/ads/",
        ShowZoneAds.as_view(),
        name="sponsored-links-site-zones",
    ),
    path(
        "publisher/<int:user_id>/sites/<int:site_id>/zones/<int:zone_id>/load-ads/",
        LoadZoneAds.as_view(),
        name="sponsored-links-site-zones",
    ),
    path("load-templates/", LoadTemplates.as_view(), name="sponsored-links-templates"),
    path(
        "load-template-sizes/",
        LoadTemplateSizes.as_view(),
        name="sponsored-links-templates",
    ),
    path(
        "create-template/", CreateTemplate.as_view(), name="sponsored-links-templates"
    ),
    path(
        "load-template-html/",
        LoadTemplateHtml.as_view(),
        name="sponsored-links-templates",
    ),
    path("load-owners/", LoadOwners.as_view(), name="sponsored-links-templates"),
    path(
        "update-template/", UpdateTemplate.as_view(), name="sponsored-links-templates"
    ),
    path(
        "delete-template/", DeleteTemplate.as_view(), name="sponsored-links-templates"
    ),
    path("templates/", ShowTemplates.as_view(), name="sponsored-links-templates"),
    path(
        "publisher/<int:user_id>/load-revenue-domains/",
        LoadPublisherRevenueDomains.as_view(),
        name="sponsored-links-load-revenue-domains",
    ),
    path(
        "update-campaign/",
        UpdateCampaign.as_view(),
        name="sponsored-links-update-campaign",
    ),
    path(
        "create-keyword-list/",
        CreateKeywordList.as_view(),
        name="sponsored-links-create-keyword-list",
    ),
    path(
        "publisher/<int:user_id>/load-keyword-lists/",
        LoadKeywordLists.as_view(),
        name="sponsored-links-load-publisher-keyword-lists",
    ),
    path("update-site-name/", UpdateSiteName.as_view(), name="sponsored-links-update-site"),
    path("delete-site/", DeleteSite.as_view(), name="sponsored-links-delete-site"),
    path(
        "load-zone-ad-html/", LoadZoneAdHtml.as_view(), name="sponsored-links-zone-ads"
    ),
    path("delete-zone-ad/", DeleteZoneAd.as_view(), name="sponsored-links-delete-ad"),
    path("clone-zone-ad/", CloneZoneAd.as_view(), name="sponsored-links-clone-zone-ad"),
    path(
        "load-zone-serving-code/",
        LoadZoneServingCode.as_view(),
        name="sponsored-links-load-zone-serving-code",
    ),
    path("delete-zone/", DeleteZone.as_view(), name="sponsored-links-delete-zone"),
    path("clone-zone/", CloneZone.as_view(), name="sponsored-links-clone-zones"),
    path("edit-zone/", EditZone.as_view(), name="sponsored-links-edit-zone"),
    path("create-zone/", CreateZone.as_view(), name="sponsored-links-create-zone"),
    path(
        "load-keywords/", LoadKeywords.as_view(), name="sponsored-links-load-keywords"
    ),
    path("load-ad-data/", LoadAdData.as_view(), name="sponsored-links-manager"),
    path(
        "update-keywords/",
        UpdateKeywords.as_view(),
        name="sponsored-links-update-keywords",
    ),
    path(
        "publishers/<int:user_id>/campaign/",
        ShowCreateCampaign.as_view(),
        name="sponsored-links-keywords",
    ),
    path(
        "publishers/<int:user_id>/create-campaign/",
        CreateCampaign.as_view(),
        name="sponsored-links-create-campaign",
    ),
    path(
        "publishers/<int:user_id>/routing-domains/",
        LoadPublisherRoutingDomains.as_view(),
        name="sponsored-links-routing-domains",
    ),
    path(
        "create-ad/",
        CreateAd.as_view(),
        name="sponsored-links-create-ad",
    ),
]
