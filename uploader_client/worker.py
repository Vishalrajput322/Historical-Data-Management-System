import requests

from PyQt6.QtCore import QThread, pyqtSignal


class UploadWorker(QThread):

    upload_finished = pyqtSignal(dict)

    error = pyqtSignal(str)

    def __init__(
        self,
        file_path,
        upload_url
    ):

        super().__init__()

        self.file_path = file_path

        self.upload_url = upload_url

    def run(self):

        try:

            with open(

                self.file_path,

                "rb"

            ) as file:

                files = {

                    "file": (

                        self.file_path,

                        file,

                        "text/csv"

                    )

                }

                response = requests.post(

                    self.upload_url,

                    files=files,

                    timeout=300

                )

            if response.status_code not in (

                200,

                201

            ):

                self.error.emit(

                    response.text

                )

                return

            response_data = (

                response.json()

            )

            response_data["file_path"] = (

                self.file_path

            )

            self.upload_finished.emit(

                response_data

            )

        except Exception as error:

            self.error.emit(

                str(error)

            )


class StatusWorker(QThread):

    status_updated = pyqtSignal(dict)

    error = pyqtSignal(str)

    def __init__(

        self,

        job_id,

        status_url

    ):

        super().__init__()

        self.job_id = job_id

        self.status_url = status_url

        self.running = True

    def run(self):

        while self.running:

            try:

                url = (

                    f"{self.status_url}"

                    f"{self.job_id}/"

                )

                response = requests.get(

                    url,

                    timeout=10

                )

                if response.status_code != 200:

                    self.error.emit(

                        response.text

                    )

                    return

                data = (

                    response.json()

                )

                data["job_id"] = (

                    self.job_id

                )

                self.status_updated.emit(

                    data

                )

                if data["status"] in (

                    "COMPLETED",

                    "FAILED"

                ):

                    break

                self.sleep(1)

            except Exception as error:

                self.error.emit(

                    str(error)

                )

                return

    def stop(self):

        self.running = False