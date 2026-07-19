from PyQt6.QtWidgets import (

    QWidget,

    QLabel,

    QComboBox,

    QPushButton,

    QDateEdit,

    QProgressBar,

    QVBoxLayout,

    QHBoxLayout,

    QFileDialog,

    QMessageBox,

)

from PyQt6.QtCore import QDate

from worker import (

    SymbolsWorker,

    FuturesWorker,

    DateRangeWorker,

    MetadataWorker,

    DownloadWorker,

)


class DownloaderWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(

            "HDMS Market Data Downloader"

        )

        self.resize(

            600,

            550

        )

        # ==========================================
        # API URLS
        # ==========================================

        self.base_url = (

            "http://10.203.6.124:8000"

        )

        self.symbols_url = (

            f"{self.base_url}"

            "/api/downloader/"

            "futstk/symbols/"

        )

        self.futures_url = (

            f"{self.base_url}"

            "/api/downloader/"

            "futstk/futures/"

        )

        self.date_range_url = (

            f"{self.base_url}"

            "/api/downloader/"

            "futstk/date-range/"

        )

        self.metadata_url = (

            f"{self.base_url}"

            "/api/downloader/"

            "futstk/metadata/"

        )

        self.download_url = (

            f"{self.base_url}"

            "/api/downloader/"

            "futstk/download/"

        )

        # ==========================================
        # WORKERS
        # ==========================================

        self.symbol_worker = None

        self.futures_worker = None

        self.date_range_worker = None

        self.metadata_worker = None

        self.download_worker = None

        # ==========================================
        # SYMBOL
        # ==========================================

        self.symbol_label = QLabel(

            "Symbol"

        )

        self.symbol_combo = QComboBox()

        self.symbol_combo.currentTextChanged.connect(

            self.symbol_changed

        )

        # ==========================================
        # FUTURE
        # ==========================================

        self.fut_label = QLabel(

            "Future"

        )

        self.fut_combo = QComboBox()

        self.fut_combo.setEnabled(

            False

        )

        self.fut_combo.currentTextChanged.connect(

            self.future_changed

        )

        # ==========================================
        # START DATE
        # ==========================================

        self.start_date_label = QLabel(

            "Start Date"

        )

        self.start_date = QDateEdit()

        self.start_date.setCalendarPopup(

            True

        )

        self.start_date.setEnabled(

            False

        )

        # ==========================================
        # END DATE
        # ==========================================

        self.end_date_label = QLabel(

            "End Date"

        )

        self.end_date = QDateEdit()

        self.end_date.setCalendarPopup(

            True

        )

        self.end_date.setEnabled(

            False

        )

        # ==========================================
        # ROW COUNT
        # ==========================================

        self.rows_label = QLabel(

            "Rows: -"

        )

        # ==========================================
        # DOWNLOAD BUTTON
        # ==========================================

        self.download_button = QPushButton(

            "Download CSV"

        )

        self.download_button.setEnabled(

            False

        )

        self.download_button.clicked.connect(

            self.start_download

        )

        # ==========================================
        # CANCEL BUTTON
        # ==========================================

        self.cancel_button = QPushButton(

            "Cancel"

        )

        self.cancel_button.setEnabled(

            False

        )

        self.cancel_button.clicked.connect(

            self.cancel_download

        )

        # ==========================================
        # PROGRESS
        # ==========================================

        self.progress_bar = QProgressBar()

        self.progress_bar.setValue(

            0

        )

        # ==========================================
        # STATUS
        # ==========================================

        self.status_label = QLabel(

            "Status: Loading symbols..."

        )

        # ==========================================
        # LAYOUT
        # ==========================================

        layout = QVBoxLayout()

        layout.addWidget(

            self.symbol_label

        )

        layout.addWidget(

            self.symbol_combo

        )

        layout.addWidget(

            self.fut_label

        )

        layout.addWidget(

            self.fut_combo

        )

        layout.addWidget(

            self.start_date_label

        )

        layout.addWidget(

            self.start_date

        )

        layout.addWidget(

            self.end_date_label

        )

        layout.addWidget(

            self.end_date

        )

        layout.addWidget(

            self.rows_label

        )

        buttons_layout = QHBoxLayout()

        buttons_layout.addWidget(

            self.download_button

        )

        buttons_layout.addWidget(

            self.cancel_button

        )

        layout.addLayout(

            buttons_layout

        )

        layout.addWidget(

            self.progress_bar

        )

        layout.addWidget(

            self.status_label

        )

        self.setLayout(

            layout

        )

        # ==========================================
        # LOAD SYMBOLS
        # ==========================================

        self.load_symbols()

    # ==================================================
    # LOAD SYMBOLS
    # ==================================================

    def load_symbols(self):

        self.symbol_worker = SymbolsWorker(

            self.symbols_url

        )

        self.symbol_worker.success.connect(

            self.symbols_loaded

        )

        self.symbol_worker.error.connect(

            self.show_error

        )

        self.symbol_worker.start()

    def symbols_loaded(

        self,

        symbols

    ):

        self.symbol_combo.clear()

        self.symbol_combo.addItems(

            symbols

        )

        self.status_label.setText(

            (

                f"Status: "

                f"{len(symbols)} symbols loaded"

            )

        )

    # ==================================================
    # SYMBOL CHANGED
    # ==================================================

    def symbol_changed(

        self,

        symbol

    ):

        if not symbol:

            return

        self.fut_combo.clear()

        self.fut_combo.setEnabled(

            False

        )

        self.start_date.setEnabled(

            False

        )

        self.end_date.setEnabled(

            False

        )

        self.download_button.setEnabled(

            False

        )

        self.rows_label.setText(

            "Rows: -"

        )

        self.status_label.setText(

            "Status: Loading futures..."

        )

        self.futures_worker = FuturesWorker(

            self.futures_url,

            symbol

        )

        self.futures_worker.success.connect(

            self.futures_loaded

        )

        self.futures_worker.error.connect(

            self.show_error

        )

        self.futures_worker.start()

    def futures_loaded(

        self,

        futures

    ):

        self.fut_combo.clear()

        self.fut_combo.addItems(

            futures

        )

        self.fut_combo.setEnabled(

            True

        )

        self.status_label.setText(

            "Status: Select future"

        )

    # ==================================================
    # FUTURE CHANGED
    # ==================================================

    def future_changed(

        self,

        fut

    ):

        symbol = (

            self.symbol_combo.currentText()

        )

        if not symbol or not fut:

            return

        self.status_label.setText(

            "Status: Loading date range..."

        )

        self.date_range_worker = DateRangeWorker(

            self.date_range_url,

            symbol,

            fut

        )

        self.date_range_worker.success.connect(

            self.date_range_loaded

        )

        self.date_range_worker.error.connect(

            self.show_error

        )

        self.date_range_worker.start()

    def date_range_loaded(

        self,

        data

    ):

        min_date = QDate.fromString(

            str(

                data["min_date"]

            ),

            "yyyy-MM-dd"

        )

        max_date = QDate.fromString(

            str(

                data["max_date"]

            ),

            "yyyy-MM-dd"

        )

        self.start_date.setMinimumDate(

            min_date

        )

        self.start_date.setMaximumDate(

            max_date

        )

        self.end_date.setMinimumDate(

            min_date

        )

        self.end_date.setMaximumDate(

            max_date

        )

        self.start_date.setDate(

            min_date

        )

        self.end_date.setDate(

            max_date

        )

        self.start_date.setEnabled(

            True

        )

        self.end_date.setEnabled(

            True

        )

        self.status_label.setText(

            "Status: Loading row count..."

        )

        self.load_metadata()

    # ==================================================
    # LOAD METADATA
    # ==================================================

    def load_metadata(

        self

    ):

        symbol = (

            self.symbol_combo.currentText()

        )

        fut = (

            self.fut_combo.currentText()

        )

        start_date = (

            self.start_date.date()

            .toString(

                "yyyy-MM-dd"

            )

        )

        end_date = (

            self.end_date.date()

            .toString(

                "yyyy-MM-dd"

            )

        )

        params = {

            "symbol": symbol,

            "fut": fut,

            "start_date": start_date,

            "end_date": end_date,

        }

        self.metadata_worker = MetadataWorker(

            self.metadata_url,

            params

        )

        self.metadata_worker.success.connect(

            self.metadata_loaded

        )

        self.metadata_worker.error.connect(

            self.show_error

        )

        self.metadata_worker.start()

    def metadata_loaded(

        self,

        data

    ):

        total_rows = data.get(

            "total_rows",

            0

        )

        self.rows_label.setText(

            (

                "Rows available: "

                f"{total_rows:,}"

            )

        )

        self.download_button.setEnabled(

            total_rows > 0

        )

        self.status_label.setText(

            "Status: Ready to download"

        )

    # ==================================================
    # DOWNLOAD
    # ==================================================

    def start_download(

        self

    ):

        symbol = (

            self.symbol_combo.currentText()

        )

        fut = (

            self.fut_combo.currentText()

        )

        start_date = (

            self.start_date.date()

            .toString(

                "yyyy-MM-dd"

            )

        )

        end_date = (

            self.end_date.date()

            .toString(

                "yyyy-MM-dd"

            )

        )

        if (

            self.start_date.date()

            > self.end_date.date()

        ):

            QMessageBox.warning(

                self,

                "Invalid Date Range",

                "Start date cannot be after end date."

            )

            return

        default_filename = (

            f"{symbol}-"

            f"{fut}-"

            f"{start_date}-"

            f"{end_date}.csv"

        )

        save_path, _ = (

            QFileDialog.getSaveFileName(

                self,

                "Save CSV",

                default_filename,

                "CSV Files (*.csv)"

            )

        )

        if not save_path:

            return

        params = {

            "symbol": symbol,

            "fut": fut,

            "start_date": start_date,

            "end_date": end_date,

        }

        self.download_worker = DownloadWorker(

            self.download_url,

            params,

            save_path

        )

        self.download_worker.progress.connect(

            self.progress_bar.setValue

        )

        self.download_worker.finished.connect(

            self.download_finished

        )

        self.download_worker.error.connect(

            self.show_error

        )

        self.download_button.setEnabled(

            False

        )

        self.cancel_button.setEnabled(

            True

        )

        self.progress_bar.setValue(

            0

        )

        self.status_label.setText(

            "Status: Downloading..."

        )

        self.download_worker.start()

    # ==================================================
    # DOWNLOAD FINISHED
    # ==================================================

    def download_finished(

        self,

        path

    ):

        self.download_button.setEnabled(

            True

        )

        self.cancel_button.setEnabled(

            False

        )

        self.progress_bar.setValue(

            100

        )

        self.status_label.setText(

            "Status: Download completed"

        )

        QMessageBox.information(

            self,

            "Download Complete",

            (

                "CSV downloaded successfully:\n\n"

                f"{path}"

            )

        )

    # ==================================================
    # CANCEL
    # ==================================================

    def cancel_download(

        self

    ):

        if self.download_worker:

            self.download_worker.stop()

            self.status_label.setText(

                "Status: Download cancelled"

            )

            self.download_button.setEnabled(

                True

            )

            self.cancel_button.setEnabled(

                False

            )

    # ==================================================
    # ERROR
    # ==================================================

    def show_error(

        self,

        error

    ):

        self.status_label.setText(

            "Status: Error"

        )

        QMessageBox.critical(

            self,

            "Error",

            str(

                error

            )

        )

    # ==================================================
    # CLOSE
    # ==================================================

    def closeEvent(

        self,

        event

    ):

        workers = [

            self.symbol_worker,

            self.futures_worker,

            self.date_range_worker,

            self.metadata_worker,

            self.download_worker,

        ]

        for worker in workers:

            if worker and worker.isRunning():

                if hasattr(

                    worker,

                    "stop"

                ):

                    worker.stop()

                worker.quit()

                worker.wait()

        event.accept()