from django.contrib import admin

from django.urls import (
    include,
    path,
)


urlpatterns = [

    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/uploader/",
        include(
            "uploader.urls"
        ),
    ),

    path(
        "api/downloader/",
        include(
            "downloader.urls"
        ),
    ),

]