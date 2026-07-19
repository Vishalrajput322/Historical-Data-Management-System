import csv
from django.db.models import Min, Max
from django.db.models import Count
from django.http import StreamingHttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from uploader.models import FutStk


class Echo:

    def write(self, value):
        return value


class FutStkSymbolsView(APIView):

    def get(self, request):

        symbols = (
            FutStk.objects
            .values_list(
                "symbol",
                flat=True
            )
            .distinct()
            .order_by(
                "symbol"
            )
        )

        return Response({

            "symbols": list(symbols)

        })


class FutStkFuturesView(APIView):

    def get(self, request):

        symbol = request.query_params.get(
            "symbol"
        )

        if not symbol:

            return Response(

                {
                    "error": (
                        "symbol is required"
                    )
                },

                status=(
                    status.HTTP_400_BAD_REQUEST
                )

            )

        futures = (

            FutStk.objects

            .filter(

                symbol=symbol

            )

            .values_list(

                "fut",

                flat=True

            )

            .distinct()

            .order_by(

                "fut"

            )

        )

        return Response({

            "symbol": symbol,

            "futures": list(

                futures

            )

        })


class FutStkDateRangeView(APIView):

    def get(self, request):

        symbol = request.query_params.get(
            "symbol"
        )

        fut = request.query_params.get(
            "fut"
        )

        if not symbol:

            return Response(

                {
                    "error": (
                        "symbol is required"
                    )
                },

                status=(
                    status.HTTP_400_BAD_REQUEST
                )

            )

        if not fut:

            return Response(

                {
                    "error": (
                        "fut is required"
                    )
                },

                status=(
                    status.HTTP_400_BAD_REQUEST
                )

            )

        queryset = (

            FutStk.objects

            .filter(

                symbol=symbol,

                fut=fut

            )

        )

        if not queryset.exists():

            return Response(

                {

                    "error": (

                        "No data found"

                    )

                },

                status=(

                    status.HTTP_404_NOT_FOUND

                )

            )

        date_range = queryset.aggregate(

            min_date=Min(

                "date"

            ),

            max_date=Max(

                "date"

            )

        )

        return Response({

            "symbol": symbol,

            "fut": fut,

            "min_date": date_range[

                "min_date"

            ],

            "max_date": date_range[

                "max_date"

            ]

        })


class FutStkDownloadView(APIView):

    def get(self, request):

        symbol = request.query_params.get(
            "symbol"
        )

        fut = request.query_params.get(
            "fut"
        )

        start_date = request.query_params.get(
            "start_date"
        )

        end_date = request.query_params.get(
            "end_date"
        )

        if not symbol:

            return Response(

                {

                    "error": (

                        "symbol is required"

                    )

                },

                status=(

                    status.HTTP_400_BAD_REQUEST

                )

            )

        if not fut:

            return Response(

                {

                    "error": (

                        "fut is required"

                    )

                },

                status=(

                    status.HTTP_400_BAD_REQUEST

                )

            )

        if not start_date:

            return Response(

                {

                    "error": (

                        "start_date is required"

                    )

                },

                status=(

                    status.HTTP_400_BAD_REQUEST

                )

            )

        if not end_date:

            return Response(

                {

                    "error": (

                        "end_date is required"

                    )

                },

                status=(

                    status.HTTP_400_BAD_REQUEST

                )

            )

        queryset = (

            FutStk.objects

            .filter(

                symbol=symbol,

                fut=fut,

                date__range=(

                    start_date,

                    end_date

                )

            )

            .order_by(

                "date",

                "time"

            )

            .values(

                "symbol",

                "fut",

                "date",

                "time",

                "open",

                "high",

                "low",

                "close",

                "volume",

                "oi"

            )

        )

        pseudo_buffer = Echo()

        writer = csv.writer(

            pseudo_buffer

        )

        def csv_generator():

            yield writer.writerow([

                "Symbol",

                "Date",

                "Time",

                "open",

                "high",

                "low",

                "close",

                "volume",

                "OI"

            ])

            for row in queryset.iterator(

                chunk_size=10_000

            ):

                yield writer.writerow([

                    (

                        f"{row['symbol']}"

                        f"-"

                        f"{row['fut']}"

                    ),

                    row["date"],

                    row["time"],

                    row["open"],

                    row["high"],

                    row["low"],

                    row["close"],

                    row["volume"],

                    row["oi"]

                ])

        filename = (

            f"{symbol}-"

            f"{fut}-"

            f"{start_date}-"

            f"{end_date}.csv"

        )

        response = StreamingHttpResponse(

            csv_generator(),

            content_type="text/csv"

        )

        response[

            "Content-Disposition"

        ] = (

            f'attachment; filename="{filename}"'

        )

        return response
    

class FutStkMetadataView(APIView):

    def get(self, request):

        symbol = request.query_params.get(
            "symbol"
        )

        fut = request.query_params.get(
            "fut"
        )

        start_date = request.query_params.get(
            "start_date"
        )

        end_date = request.query_params.get(
            "end_date"
        )

        if not all([
            symbol,
            fut,
            start_date,
            end_date,
        ]):

            return Response(

                {
                    "error": (
                        "symbol, fut, start_date "
                        "and end_date are required"
                    )
                },

                status=(
                    status.HTTP_400_BAD_REQUEST
                )

            )

        queryset = (

            FutStk.objects

            .filter(

                symbol=symbol,

                fut=fut,

                date__range=(

                    start_date,

                    end_date

                )

            )

        )

        total_rows = (

            queryset.count()

        )

        return Response({

            "symbol": symbol,

            "fut": fut,

            "start_date": start_date,

            "end_date": end_date,

            "total_rows": total_rows,

        })