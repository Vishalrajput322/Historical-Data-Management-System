from django.core.management.base import BaseCommand

from uploader.importer import FutStkImporter


class Command(BaseCommand):

    help = "Import a queued CSV file"

    def add_arguments(self, parser):

        parser.add_argument(

            "job_id",

            type=int

        )

    def handle(

        self,

        *args,

        **options

    ):

        job_id = options["job_id"]

        self.stdout.write(

            f"Starting import job {job_id}"

        )

        importer = FutStkImporter(

            job_id

        )

        result = importer.run()

        self.stdout.write(

            self.style.SUCCESS(

                "\n"

                "Import completed successfully\n"

                "----------------------------\n"

                f"Rows: "

                f"{result['rows']:,}\n"

                f"Read time: "

                f"{result['read_time']:.3f} seconds\n"

                f"Transform time: "

                f"{result['transform_time']:.3f} seconds\n"

                f"Write time: "

                f"{result['write_time']:.3f} seconds\n"

                f"COPY time: "

                f"{result['copy_time']:.3f} seconds\n"

                f"Total time: "

                f"{result['total_time']:.3f} seconds"

            )

        )