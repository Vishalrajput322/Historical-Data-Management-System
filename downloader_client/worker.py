import requests

from PyQt6.QtCore import QThread, pyqtSignal


class SymbolsWorker(QThread):

    success = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, url):

        super().__init__()

        self.url = url

    def run(self):

        try:

            response = requests.get(

                self.url,

                timeout=30

            )

            response.raise_for_status()

            data = response.json()

            self.success.emit(

                data.get(

                    "symbols",

                    []

                )

            )

        except Exception as error:

            self.error.emit(

                str(error)

            )


class FuturesWorker(QThread):

    success = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(

        self,

        url,

        symbol

    ):

        super().__init__()

        self.url = url

        self.symbol = symbol

    def run(self):

        try:

            response = requests.get(

                self.url,

                params={

                    "symbol": self.symbol

                },

                timeout=30

            )

            response.raise_for_status()

            data = response.json()

            self.success.emit(

                data.get(

                    "futures",

                    []

                )

            )

        except Exception as error:

            self.error.emit(

                str(error)

            )


class DateRangeWorker(QThread):

    success = pyqtSignal(dict)

    error = pyqtSignal(str)

    def __init__(

        self,

        url,

        symbol,

        fut

    ):

        super().__init__()

        self.url = url

        self.symbol = symbol

        self.fut = fut

    def run(self):

        try:

            response = requests.get(

                self.url,

                params={

                    "symbol": self.symbol,

                    "fut": self.fut

                },

                timeout=30

            )

            response.raise_for_status()

            data = response.json()

            self.success.emit(

                data

            )

        except Exception as error:

            self.error.emit(

                str(error)

            )


class MetadataWorker(QThread):

    success = pyqtSignal(dict)

    error = pyqtSignal(str)

    def __init__(

        self,

        url,

        params

    ):

        super().__init__()

        self.url = url

        self.params = params

    def run(self):

        try:

            response = requests.get(

                self.url,

                params=self.params,

                timeout=60

            )

            response.raise_for_status()

            data = response.json()

            self.success.emit(

                data

            )

        except Exception as error:

            self.error.emit(

                str(error)

            )


class DownloadWorker(QThread):

    progress = pyqtSignal(int)

    finished = pyqtSignal(str)

    error = pyqtSignal(str)

    def __init__(

        self,

        url,

        params,

        save_path

    ):

        super().__init__()

        self.url = url

        self.params = params

        self.save_path = save_path

        self.running = True

    def run(self):

        try:

            response = requests.get(

                self.url,

                params=self.params,

                stream=True,

                timeout=(

                    30,

                    300

                )

            )

            response.raise_for_status()

            total_size = int(

                response.headers.get(

                    "Content-Length",

                    0

                )

            )

            downloaded = 0

            with open(

                self.save_path,

                "wb"

            ) as file:

                for chunk in response.iter_content(

                    chunk_size=1024 * 1024

                ):

                    if not self.running:

                        return

                    if chunk:

                        file.write(

                            chunk

                        )

                        downloaded += len(

                            chunk

                        )

                        if total_size > 0:

                            percentage = int(

                                (

                                    downloaded

                                    / total_size

                                )

                                * 100

                            )

                            self.progress.emit(

                                percentage

                            )

            self.finished.emit(

                self.save_path

            )

        except Exception as error:

            self.error.emit(

                str(error)

            )

    def stop(self):

        self.running = False