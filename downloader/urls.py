from django.urls import path

from .views import (
    FutStkSymbolsView,
    FutStkFuturesView,
    FutStkDateRangeView,
    FutStkDownloadView,
    FutStkMetadataView
)


urlpatterns = [

    path(

        "futstk/symbols/",

        FutStkSymbolsView.as_view(),

        name="futstk-symbols"

    ),

    path(

        "futstk/futures/",

        FutStkFuturesView.as_view(),

        name="futstk-futures"

    ),

    path(

        "futstk/date-range/",

        FutStkDateRangeView.as_view(),

        name="futstk-date-range"

    ),

    path(

        "futstk/download/",

        FutStkDownloadView.as_view(),

        name="futstk-download"

    ),

    path(

    "futstk/metadata/",

    FutStkMetadataView.as_view(),

    name="futstk-metadata"

),

]