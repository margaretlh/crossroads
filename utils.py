"""This module contains the AdSpeed utilities."""


import base64
import collections
import hashlib
import logging
import textwrap  # string unident for serving code
import urllib
import xml.etree.ElementTree as ET

import requests
from rest_framework import status

from django.conf import settings

from apps.admin._trafficguard.tg_campaign import TgCampaign
from apps.sponsored_links_reporting.models import (
    Ad,
    AdContainer,
    AdspeedAccount,
    AdZone,
    Group,
    KeywordNew,
)
from apps.sponsored_links_reporting.renderer import render_ad_wrapper


LOGGER = logging.getLogger(__name__)


class CampaignFinalizationError(Exception):
    """
    Exception raised for errors that occur during the campaign finalization process.

    Attributes:
        message (str): Explanation of the error
        details (dict): Optional dictionary to hold additional details of the error
    """
    def __init__(self, message: str, details: dict | None = None):
        """Initiates the custom CampaignFinalizationError class."""
        super().__init__(message)
        self.message = message
        self.details = details if details is not None else {}

    def __str__(self):
        """
        Return the string representation of the error, which will include any additional details if provided.
        """
        if self.details:
            return f"{self.message} Details: {self.details}"
        return self.message


def create_zone(name: str, width: int, height: int, site_id: int) -> AdZone:
    """
    Creates a new AdZone and creates it within AdSpeed.

    Args:
        name (str): Name of the Zone
        width (int): Width of the Zone
        height (int): Height of the Zone
        site_id (int): The ID of the associated Site.

    Returns:
        AdZone: The newly created AdZone object, synced with AdSpeed.

    Raises:
        Exception: If the zone cannot be created on AdSpeed.
    """
    account = AdspeedAccount.objects.last()
    zone = AdZone.objects.create(
        name=name,
        width=width,
        height=height,
        site_id=site_id,
        account=account,
        synced=False
    )

    payload = {
        "key": zone.account.apikey,
        "method": "AS.Zones.create",
        "name": zone.name.replace("|", "_"),
    }

    payload["md5"] = checksum(payload, zone.account.secret)
    response = requests.post(settings.ADSPEED_URL, data=payload, timeout=180)
    if response.status_code != status.HTTP_200_OK:
        error_message = """Failed to reach AdSpeed API.
          Subsequent steps such as ad container and ads creation will not be executed."""
        raise CampaignFinalizationError(error_message)

    root = ET.fromstring(response.text)  # noqa: S314
    adspeed_zone = root.find("Zone")
    if adspeed_zone is not None:
        zone.provider_id = adspeed_zone.attrib["id"]
        zone.status = adspeed_zone.attrib["status"]
        zone.synced = True
        zone.save()
    else:
        error_message = """Failed to create AdZone.
                    Subsequent steps such as ad container and ads creation will not be executed."""
        raise CampaignFinalizationError(error_message)

    return zone


def edit_zone(zone_id: int, name: str) -> bool:
    """
    Updates a Zone within AdSpeed and Locally.

    Args:
        zone_id(int): AdZone ID.
        name(string): Zone Name.

    Return:
        Boolean
    """
    zone = AdZone.objects.get(id=zone_id)
    zone_name = name.replace("|", "_")
    payload = {
        "key": zone.account.apikey,
        "zone": zone.provider_id,
        "token": generate_token([zone.provider_id, zone.name]),
        "method": "AS.Zone.edit",
        "name": zone_name,
    }
    payload["sig"] = checksum(payload, zone.account.secret)
    response = requests.post(settings.ADSPEED_URL, data=payload, timeout=180)
    root = ET.fromstring(response.text)  # noqa: S314

    if root.tag != "Error":
        adspeed_zone = root.find("Zone")
        zone.status = adspeed_zone.attrib["status"]
        zone.name = zone_name
        zone.save()

        return True

    return False


def create_ad_container(  # noqa: PLR0913
    name: str,
    title: str,
    zone_id: int,
    template_id: int,
    keyword_ids: list,
    campaign_id: int | None = None
) -> tuple:
    """
    Creates a new AdContainer and links it with specified keywords, returning any keyword-related errors.

    Args:
        name (str): AdContainer name.
        title (str): AdContainer title.
        zone_id (int): AdZone ID.
        template_id (int): AdTemplate ID.
        keyword_ids (list): List of integers representing keyword IDs.
        campaign_id (int): Optional Campaign ID associated with this container.

    Returns:
        tuple: A tuple containing the AdContainer and a dictionary of errors.
    """
    ad_container = AdContainer.objects.create(
        name=name,
        title=title,
        zone_id=zone_id,
        template_id=template_id,
        tg_campaign_id=campaign_id,
    )
    errors = {}
    keywords = KeywordNew.objects.filter(id__in=keyword_ids)
    if keywords.count() != len(keyword_ids):
        errors["Keyword error"] = "One or more keyword IDs do not exist."

    for keyword in keywords:
        ad_container.keywords.add(keyword)

    ad_container.refresh_from_db()
    return ad_container, errors


def create_ads(ad_container: AdContainer, iterations: int, campaign: TgCampaign) -> None:
    """
    Creates ad iterations and attempts to sync them with AdSpeed.

    Args:
        ad_container (AdContainer): The container to which ads belong.
        iterations (int): Number of ads to create.
        campaign (TgCampaign): The associated campaign.

    Raises:
        Exception: If there is an issue with ad creation or syncing.
    """

    def raise_campaign_error(message: str) -> None:
        """Raises a CampaignFinalizationError with the given message."""
        raise CampaignFinalizationError(message)

    errors = []
    ads = ad_container.create_ads(iterations, campaign)
    for ad in ads:
        try:
            ad.synced = False
            ad.save()
            template = ad.container.template

            html = base64.b64encode(bytes(render_ad_wrapper(ad), "utf-8")).decode("utf-8")
            payload = {
                "key": ad.container.zone.account.apikey,
                "method": "AS.Ads.createHTML",
                "name": str(ad.id),
                "htmlbase64": html,
                "width": template.width,
                "height": template.height,
            }
            payload["md5"] = checksum(payload, ad.container.zone.account.secret)
            response = requests.post(settings.ADSPEED_URL, data=payload, timeout=180)
            root = ET.fromstring(response.text)  # noqa: S314

            if root.tag == "Error":
                error_message = root.find("Message").text if root.find("Message") else "Unknown error"
                exception_message = f"Error publishing ad to AdSpeed: {error_message}"
                raise_campaign_error(exception_message)

            adresp = root.find("Ad")
            ad.provider_id = adresp.attrib["id"]
            ad.status = adresp.attrib["status"]
            ad.synced = True
            ad.save()

            # Additional ad linking operations
            link_ad_to_zone(ad.id)
            group = Group.get_available_or_create_new()
            group.link_ad(ad)

        except CampaignFinalizationError as ex:
            # Collect error messages for each ad
            errors.append(str(ex))
            continue

    if errors:
        raise CampaignFinalizationError("Failed to create or sync one or more ads: " + "; ".join(errors))


def checksum(payload: dict, secret: str) -> str:
    """
    Generates and MD5 Checksum.

    Args:
        payload(dict): Raw payload.
        secret(str): Secret phrase.

    Return:
        Str
    """
    m = hashlib.md5()  # noqa: S324
    raw_string = secret + get_raw_string(payload)
    m.update(raw_string.encode("utf-8"))
    return m.hexdigest()


def get_raw_string(payload: dict) -> str:
    """
    Parses a dictionary into a string.

    Args:
        payload(dict): Raw payload.

    Return:
        Str
    """
    payload_ordered = collections.OrderedDict(sorted(payload.items()))
    raw_string = ""
    for k, v in payload_ordered.items():
        raw_string += k + "=" + urllib.parse.quote_plus(str(v)) + "&"

    return raw_string[:-1]



def link_ad_to_zone(ad_id: int) -> bool:
    """
    Links an Ad to an AdZone.

    Args:
        ad_id(int): Ad ID.

    Return:
        Boolean
    """
    ad = Ad.objects.get(id=ad_id)
    token = generate_token(
        [
            ad.provider_id,
            str(ad.id),
            ad.container.zone.provider_id,
            ad.container.zone.name,
        ]
    )
    payload = {
        "key": ad.container.zone.account.apikey,
        "method": "AS.Ad.linkToZone",
        "ad": ad.provider_id,
        "zone": ad.container.zone.provider_id,
        "token": token,
    }
    response = requests.get(
        settings.ADSPEED_URL
        + "?"
        + get_raw_string(payload)
        + "&md5="
        + checksum(payload, ad.container.zone.account.secret),
        timeout=180,
    )
    root = ET.fromstring(response.text)  # noqa: S314
    is_confirmed = root.find("Confirmation")

    ad.synced = True
    ad.linked = True
    ad.save()

    if is_confirmed:
        LOGGER.error("Error linking ad to zone: %s", response.text)
        return True

    return False


def generate_token(str_list: list) -> str:
    """
    Generates an MD5 Hash.

    Args:
        str_list(list): List of strings.

    Return:
        String
    """
    md5_hasher = hashlib.md5()  # noqa: S324
    raw_string = "".join(map(str, str_list))
    md5_hasher.update(raw_string.encode("utf-8"))

    return md5_hasher.hexdigest()


def get_ad_serving_code(ad: Ad) -> str:
    """
    Retrieves AdSpeed Serving Code for a given Ad.

    Args:
        ad(Ad): Ad

    Return:
        String: serving code.
    """
    payload = {
        "key": ad.container.zone.account.apikey,
        "method": "AS.Ad.getAdTag",
        "ad": ad.provider_id,
        "token": generate_token([ad.provider_id, str(ad.id)]),
        "width": ad.container.template.width,
        "height": ad.container.template.height,
        "format": "javascript",
    }
    response = requests.get(
        settings.ADSPEED_URL
        + "?"
        + get_raw_string(payload)
        + "&md5="
        + checksum(payload, ad.container.zone.account.secret),
        timeout=180,
    )
    root = ET.fromstring(response.text)  # noqa: S314
    html = root.find("Ad").find("ServingCode").text  # TODO exception handling!
    # remove empty lines and unident serving code
    return clean_ad_tag(html)


def clean_ad_tag(tag: str) -> str:
    """
    Santizes an Ad Tag.

    Args:
        tag (str): Tag String.

    Return:
        String
    """
    return "".join(
        [
            string
            for string in textwrap.dedent(
                tag.replace("ad.php", "qc.php")
                .replace(r"AdSpeed.com", "")
                .replace("sl.aveimedia.com", "sl.crossroads.ai")
                .replace("http://", "https://")
            ).splitlines(keepends=True)
            if string.strip("\r\n")
        ]
    )
