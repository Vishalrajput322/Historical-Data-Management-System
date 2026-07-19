from django.db import models


class FutStk(models.Model):
    symbol = models.CharField(max_length=50)
    fut = models.CharField(max_length=10)

    date = models.DateField()
    time = models.IntegerField()

    open = models.DecimalField(
        max_digits=15,
        decimal_places=4
    )

    high = models.DecimalField(
        max_digits=15,
        decimal_places=4
    )

    low = models.DecimalField(
        max_digits=15,
        decimal_places=4
    )

    close = models.DecimalField(
        max_digits=15,
        decimal_places=4
    )

    volume = models.BigIntegerField()
    oi = models.BigIntegerField()

    class Meta:
        db_table = 'futstk_table'

    def __str__(self):
        return f"{self.symbol}-{self.fut} {self.date} {self.time}"
    

class ImportJob(models.Model):

    class Status(models.TextChoices):

        QUEUED = "QUEUED", "Queued"

        PROCESSING = "PROCESSING", "Processing"

        COMPLETED = "COMPLETED", "Completed"

        FAILED = "FAILED", "Failed"


    filename = models.CharField(
        max_length=255
    )


    file_path = models.TextField()


    status = models.CharField(

        max_length=20,

        choices=Status.choices,

        default=Status.QUEUED

    )


    total_rows = models.BigIntegerField(

        default=0

    )


    processed_rows = models.BigIntegerField(

        default=0

    )


    error_message = models.TextField(

        blank=True,

        null=True

    )


    created_at = models.DateTimeField(

        auto_now_add=True

    )


    started_at = models.DateTimeField(

        blank=True,

        null=True

    )


    completed_at = models.DateTimeField(

        blank=True,

        null=True

    )


    class Meta:

        db_table = "import_jobs"


    def __str__(self):

        return (

            f"{self.filename} - "

            f"{self.status}"

        )