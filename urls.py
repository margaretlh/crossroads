from django.urls import path

from apps.whitelabel import views


app_name = "whitelabel"

urlpatterns = [
    path("", views.WhiteLabelIndex.as_view()),
    path("<int:wl_id>/", views.WhiteLabelSettings.as_view()),

    path("detail/<int:wl_pub_id>/", views.WhiteLabelPubDetail.as_view()),
    path("<int:white_label_id>/associate-publisher/", views.AssociatePublisherWithWhiteLabel.as_view()),
    path("detail/<int:wl_pub_id>/delete/", views.RemovePubFromConfiguration.as_view()),

    path("<int:wl_id>/reports/", views.WhiteLabelPubReport.as_view()),
    path("store/", views.StoreWhiteLabelConfiguration.as_view()),
    path("<int:white_label_id>/load-settings/", views.LoadWhiteLabelSettings.as_view()),
    path("<int:white_label_id>/update-settings/", views.UpdateWhiteLabelSettings.as_view()),
    path("<int:white_label_id>/deactivate-settings/" , views.DeactivateWhiteLabelSettings.as_view()),

    path("<int:white_label_id>/add-admin/", views.AddAdminToWhiteLabel.as_view()),
    path("<int:white_label_id>/remove-all-admins/", views.RemoveAdminsFromWhiteLabel.as_view()),
]
