# uploader/views.py

import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ImportJob
from .serializers import CSVUploadSerializer
from .tasks import import_futstk_csv


class FutStkCSVUploadView(APIView):
    """
    Handles CSV file upload, saves it to MEDIA_ROOT/uploads,
    creates an ImportJob, and queues a Celery task.
    """

    def post(self, request):
        serializer = CSVUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data["file"]

        # Ensure upload directory exists
        upload_directory = settings.MEDIA_ROOT / "uploads"
        os.makedirs(upload_directory, exist_ok=True)

        # Save file to disk
        file_path = upload_directory / uploaded_file.name
        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Create ImportJob record
        import_job = ImportJob.objects.create(
            filename=uploaded_file.name,
            file_path=str(file_path),
            status=ImportJob.Status.QUEUED
        )

        # Queue Celery task
        import_futstk_csv.delay(import_job.id)

        return Response(
            {
                "message": "File uploaded and import queued successfully",
                "job_id": import_job.id,
                "filename": import_job.filename,
                "status": import_job.status,
            },
            status=status.HTTP_201_CREATED
        )


class ImportJobStatusView(APIView):
    """
    Retrieve the status and progress of an ImportJob by ID.
    """

    def get(self, request, job_id):
        try:
            job = ImportJob.objects.get(id=job_id)
        except ImportJob.DoesNotExist:
            return Response(
                {"error": "Import job not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        progress = (
            (job.processed_rows / job.total_rows * 100)
            if job.total_rows > 0 else 0
        )

        return Response(
            {
                "job_id": job.id,
                "filename": job.filename,
                "status": job.status,
                "total_rows": job.total_rows,
                "processed_rows": job.processed_rows,
                "progress": round(progress, 2),
                "error_message": job.error_message,
            },
            status=status.HTTP_200_OK
        )
