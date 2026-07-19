import os
import time
import tempfile

import polars as pl

from django.db import connection
from django.utils import timezone

from .models import ImportJob


class FutStkImporter:

    def __init__(self, job_id):

        self.job = ImportJob.objects.get(
            id=job_id
        )

    def run(self):

        start_time = time.perf_counter()

        temp_file_path = None

        try:

            # ==================================================
            # STEP 1: MARK JOB AS PROCESSING
            # ==================================================

            self.job.status = (
                ImportJob.Status.PROCESSING
            )

            self.job.started_at = (
                timezone.now()
            )

            self.job.save(

                update_fields=[

                    "status",

                    "started_at",

                ]

            )

            # ==================================================
            # STEP 2: READ CSV WITH POLARS
            # ==================================================

            read_start = time.perf_counter()

            df = pl.read_csv(

                self.job.file_path,

                schema_overrides={

                    "Symbol": pl.String,

                    "Date": pl.Date,

                    "Time": pl.Int32,

                    "open": pl.Float64,

                    "high": pl.Float64,

                    "low": pl.Float64,

                    "close": pl.Float64,

                    "volume": pl.Int64,

                    "OI": pl.Int64,

                },

            )

            read_time = (

                time.perf_counter()

                - read_start

            )

            total_rows = df.height

            self.job.total_rows = (

                total_rows

            )

            self.job.save(

                update_fields=[

                    "total_rows"

                ]

            )

            # ==================================================
            # STEP 3: TRANSFORM DATA WITH POLARS
            # ==================================================

            transform_start = (

                time.perf_counter()

            )

            df = (

                df

                .with_columns(

                    pl.col("Symbol")

                    .str.extract(

                        r"^(.*)-([^-]+)$",

                        group_index=1

                    )

                    .alias("symbol"),

                    pl.col("Symbol")

                    .str.extract(

                        r"^(.*)-([^-]+)$",

                        group_index=2

                    )

                    .alias("fut"),

                )

                .rename(

                    {

                        "Date": "date",

                        "Time": "time",

                        "OI": "oi",

                    }

                )

                .select(

                    [

                        "symbol",

                        "fut",

                        "date",

                        "time",

                        "open",

                        "high",

                        "low",

                        "close",

                        "volume",

                        "oi",

                    ]

                )

            )

            transform_time = (

                time.perf_counter()

                - transform_start

            )

            # ==================================================
            # STEP 4: WRITE TRANSFORMED CSV
            # ==================================================

            write_start = (

                time.perf_counter()

            )

            temp_file = (

                tempfile.NamedTemporaryFile(

                    mode="w",

                    suffix=".csv",

                    delete=False,

                    newline="",

                    encoding="utf-8",

                )

            )

            temp_file_path = (

                temp_file.name

            )

            temp_file.close()

            df.write_csv(

                temp_file_path

            )

            write_time = (

                time.perf_counter()

                - write_start

            )

            # ==================================================
            # STEP 5: POSTGRESQL COPY
            # ==================================================

            copy_start = (

                time.perf_counter()

            )

            with connection.cursor() as cursor:

                copy_sql = """

                    COPY futstk_table (

                        symbol,

                        fut,

                        date,

                        time,

                        open,

                        high,

                        low,

                        close,

                        volume,

                        oi

                    )

                    FROM STDIN

                    WITH (

                        FORMAT CSV,

                        HEADER TRUE

                    )

                """

                with cursor.copy(

                    copy_sql

                ) as copy:

                    with open(

                        temp_file_path,

                        "rb"

                    ) as csv_file:

                        while True:

                            chunk = (

                                csv_file.read(

                                    1024 * 1024

                                )

                            )

                            if not chunk:

                                break

                            copy.write(

                                chunk

                            )

            copy_time = (

                time.perf_counter()

                - copy_start

            )

            # ==================================================
            # STEP 6: MARK JOB AS COMPLETED
            # ==================================================

            self.job.processed_rows = (

                total_rows

            )

            self.job.status = (

                ImportJob.Status.COMPLETED

            )

            self.job.completed_at = (

                timezone.now()

            )

            self.job.save(

                update_fields=[

                    "processed_rows",

                    "status",

                    "completed_at",

                ]

            )

            # ==================================================
            # TOTAL TIME
            # ==================================================

            total_time = (

                time.perf_counter()

                - start_time

            )

            return {

                "success": True,

                "rows": total_rows,

                "read_time": round(

                    read_time,

                    3

                ),

                "transform_time": round(

                    transform_time,

                    3

                ),

                "write_time": round(

                    write_time,

                    3

                ),

                "copy_time": round(

                    copy_time,

                    3

                ),

                "total_time": round(

                    total_time,

                    3

                ),

            }

        except Exception as error:

            # ==================================================
            # MARK JOB AS FAILED
            # ==================================================

            self.job.status = (

                ImportJob.Status.FAILED

            )

            self.job.error_message = (

                str(error)

            )

            self.job.completed_at = (

                timezone.now()

            )

            self.job.save(

                update_fields=[

                    "status",

                    "error_message",

                    "completed_at",

                ]

            )

            raise

        finally:

            # ==================================================
            # DELETE TEMPORARY FILE
            # ==================================================

            if (

                temp_file_path

                and os.path.exists(

                    temp_file_path

                )

            ):

                os.remove(

                    temp_file_path

                )