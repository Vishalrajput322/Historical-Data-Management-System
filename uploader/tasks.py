from celery import shared_task

from .importer import FutStkImporter


@shared_task(

    bind=True,

    name="uploader.import_futstk_csv"

)

def import_futstk_csv(

    self,

    job_id

):

    importer = FutStkImporter(

        job_id

    )

    result = importer.run()

    return result