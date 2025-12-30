from django_tables2 import Column, tables

from django.utils.safestring import mark_safe

from apps.main_app.helpers import SummedColumn
from apps.whitelabel.models import WhiteLabelConfiguration


TABLE_CLASS = "paleblue"
LEFT_ALIGN = {"td": {"style": "text-align: left;"}, "th": {"style": "text-align: left;"} }

class WhiteLabelIndexTable(tables.Table):

    class Meta:
        attrs = {"class": TABLE_CLASS}
        model = WhiteLabelConfiguration
        fields = ("name", "active", "action")  # Use the actual field names from the model

    name = Column(attrs=LEFT_ALIGN)
    action = Column(visible=True, empty_values=(), attrs=LEFT_ALIGN)
    active = Column(visible=True, attrs=LEFT_ALIGN, verbose_name="Status")

    def render_name(self, record):
        html = '<a href="/whitelabel/{id}/reports/">{name}</a>'.format(name=record["name"], id=record["id"])
        return mark_safe(html)

    def render_action(self,record):
        html = '<a href="/whitelabel/{id}/">Settings</a>'.format(id=record["id"])
        return mark_safe(html)

    def render_active(self, record):
        status = "Active" if record["active"] else "Inactive"
        color = "green" if record["active"] else "red"
        html = f'<span style="color: {color};">{status}</span>'
        return mark_safe(html)

class WhiteLabelPublisherTable(tables.Table):
    class Meta:
        attrs = {"class": TABLE_CLASS}

    publisher__username = Column(attrs=LEFT_ALIGN, verbose_name="Username")
    bucket = Column(attrs=LEFT_ALIGN)
    action = Column(visible=True, empty_values=())

    def render_publisher__username(self, record):
        html = '<a href="/whitelabel/detail/{id}">{name}</a>'.format(name=record["publisher__username"], id=record["id"])
        return mark_safe(html)

    def render_action(self,record):
        html = '<a href="/impersonate/{id}">impersonate</a>'.format(id=record["publisher_id"])
        return mark_safe(html)

    def render_active(self, record):
        status = "Active" if record["active"] else "Inactive"
        color = "green" if record["active"] else "red"
        html = f'<span style="color: {color};">{status}</span>'
        return mark_safe(html)


class WhiteLabelAdminTable(tables.Table):
    class Meta:
        attrs = {"class": TABLE_CLASS}

    username = Column(attrs=LEFT_ALIGN, verbose_name="Username")

class WlShareRuleTable(tables.Table):

    class Meta:
        attrs = {"class": TABLE_CLASS}

    date_effective = Column(attrs=LEFT_ALIGN)
    percentage = Column()

    def render_percentage(self, value):
        return f"{value*100:.2f}%"

class WlPublisherReportTable(tables.Table):

    class Meta:
        attrs = {"class": TABLE_CLASS}

    username = Column(attrs=LEFT_ALIGN)
    bucket = Column(attrs=LEFT_ALIGN)
    total_visitors__sum = Column(verbose_name="Gross Visitors")
    tracked_visitors__sum = Column(verbose_name="Tracked Visitors")
    owner_rev = SummedColumn(footer_format_string="${0:.2f}", verbose_name="Partner Revenue")
    pub_client_rev = SummedColumn(footer_format_string="${0:.2f}", verbose_name="Publisher Revenue")
    diff = SummedColumn(footer_format_string="${0:.2f}", verbose_name="Partner Profit")

    @staticmethod
    def render_owner_rev(value):
        return f"${value:.2f}"

    @staticmethod
    def render_pub_client_rev(value):
        return f"${value:.2f}"

    @staticmethod
    def render_diff(value):
        return f"${value:.2f}"

    @staticmethod
    def render_username(record):
        html = '<a href="/impersonate/{id}">{username}</a>'.format(id=record["crossroads_user_id"],username=record["username"])
        return mark_safe(html)
