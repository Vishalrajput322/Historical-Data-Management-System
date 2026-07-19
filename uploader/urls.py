from django.urls import path

from .views import (
    FutStkCSVUploadView,
    ImportJobStatusView,
)


urlpatterns = [
    path(
        "upload/",
        FutStkCSVUploadView.as_view(),
    ),

    path(
        "status/<int:job_id>/",
        ImportJobStatusView.as_view(),
    ),
]