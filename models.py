from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models


class WhiteLabelConfigurationAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

class WhiteLabelConfiguration(models.Model):
    admins = models.ManyToManyField(User)
    pay_difference_to = models.ForeignKey(User, null=True ,on_delete=models.SET_NULL, related_name="+")
    title = models.TextField()
    name = models.TextField()
    logo_icon = models.TextField()
    primary_color = models.CharField(max_length=7)
    secondary_color = models.CharField(max_length=7)
    text_color = models.CharField(max_length=7)
    active = models.BooleanField(default=True)
    deactivation_date = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return f"{self.title} - {self.name}"

    def is_wl_admin(self, user):
        return user.id in list(self.admins.values_list("id", flat=True))

class WLPublisherManager(models.Manager):
    def get_buckets_dict(self):
        return {t[0]: t[1] for t in WLPublisher.BUCKET_TYPES}

class WLPublisher(models.Model):
    BUCKET_3PH = 1
    BUCKET_O_AND_O = 2
    BUCKET_TYPES = (
        (BUCKET_3PH, "3PH"),
        (BUCKET_O_AND_O, "O&O"),
    )

    objects = WLPublisherManager()
    configuration = models.ForeignKey(WhiteLabelConfiguration, on_delete=models.CASCADE)
    publisher = models.ForeignKey(User, related_name="wl_publisher", on_delete=models.CASCADE)
    bucket = models.IntegerField(choices=BUCKET_TYPES, default=BUCKET_3PH)

    def delete(self):
        rule, _ = WLShareRule.objects.update_or_create(owner=self.publisher, date_effective=datetime.today().date(), defaults={
            "percentage":1.0
        })
        super(WLPublisher, self).delete()

class WLShareRule(models.Model):
    owner = models.ForeignKey(User, related_name="wl_rules", on_delete=models.CASCADE)
    date_effective = models.DateField()
    percentage = models.DecimalField(max_digits=10, decimal_places=3)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.owner.username} - {self.date_effective} - {self.percentage}"
