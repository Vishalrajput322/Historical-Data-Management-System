from PyQt6.QtWidgets import (

    QWidget,

    QPushButton,

    QLabel,

    QProgressBar,

    QVBoxLayout,

    QFileDialog,

    QMessageBox,

    QTableWidget,

    QTableWidgetItem,

    QHeaderView,

)

from PyQt6.QtCore import Qt

from uploader_admin.worker import (

    UploadWorker,

    StatusWorker,

)


class MainWindow(QWidget):

    def __init__(

        self

    ):

        super().__init__()

        # ==========================================
        # WINDOW
        # ==========================================

        self.setWindowTitle(

            "HDMS CSV Uploader"

        )

        self.resize(

            900,

            600

        )

        # ==========================================
        # URLS
        # ==========================================

        self.upload_url = (

            "http://10.203.6.124:8000"

            "/api/uploader/upload/"

        )

        self.status_url = (

            "http://10.203.6.124:8000"

            "/api/uploader/status/"

        )

        # ==========================================
        # DATA
        # ==========================================

        self.selected_files = []

        self.jobs = {}

        self.upload_workers = []

        self.status_workers = []

        # ==========================================
        # SELECT BUTTON
        # ==========================================

        self.select_button = QPushButton(

            "Select CSV Files"

        )

        self.select_button.clicked.connect(

            self.select_files

        )

        # ==========================================
        # UPLOAD BUTTON
        # ==========================================

        self.upload_button = QPushButton(

            "Upload Selected Files"

        )

        self.upload_button.setEnabled(

            False

        )

        self.upload_button.clicked.connect(

            self.start_upload

        )

        # ==========================================
        # CLEAR BUTTON
        # ==========================================

        self.clear_button = QPushButton(

            "Clear"

        )

        self.clear_button.setEnabled(

            False

        )

        self.clear_button.clicked.connect(

            self.clear_files

        )

        # ==========================================
        # FILE COUNT
        # ==========================================

        self.file_count_label = QLabel(

            "Selected Files: 0"

        )

        # ==========================================
        # STATUS
        # ==========================================

        self.status_label = QLabel(

            "Status: Ready"

        )

        # ==========================================
        # OVERALL PROGRESS
        # ==========================================

        self.overall_progress_label = QLabel(

            "Overall Progress: 0 / 0"

        )

        self.overall_progress = QProgressBar()

        self.overall_progress.setValue(

            0

        )

        # ==========================================
        # TABLE
        # ==========================================

        self.table = QTableWidget()

        self.table.setColumnCount(

            5

        )

        self.table.setHorizontalHeaderLabels(

            [

                "File",

                "Job ID",

                "Status",

                "Rows",

                "Progress"

            ]

        )

        self.table.horizontalHeader().setSectionResizeMode(

            0,

            QHeaderView.ResizeMode.Stretch

        )

        self.table.horizontalHeader().setSectionResizeMode(

            1,

            QHeaderView.ResizeMode.ResizeToContents

        )

        self.table.horizontalHeader().setSectionResizeMode(

            2,

            QHeaderView.ResizeMode.ResizeToContents

        )

        self.table.horizontalHeader().setSectionResizeMode(

            3,

            QHeaderView.ResizeMode.ResizeToContents

        )

        self.table.horizontalHeader().setSectionResizeMode(

            4,

            QHeaderView.ResizeMode.ResizeToContents

        )

        # ==========================================
        # LAYOUT
        # ==========================================

        layout = QVBoxLayout()

        layout.setSpacing(

            12

        )

        layout.addWidget(

            self.select_button

        )

        layout.addWidget(

            self.file_count_label

        )

        layout.addWidget(

            self.upload_button

        )

        layout.addWidget(

            self.clear_button

        )

        layout.addWidget(

            self.status_label

        )

        layout.addWidget(

            self.overall_progress_label

        )

        layout.addWidget(

            self.overall_progress

        )

        layout.addWidget(

            self.table

        )

        self.setLayout(

            layout

        )

    # ==================================================
    # SELECT MULTIPLE FILES
    # ==================================================

    def select_files(

        self

    ):

        files, _ = (

            QFileDialog.getOpenFileNames(

                self,

                "Select CSV Files",

                "",

                "CSV Files (*.csv)"

            )

        )

        if not files:

            return

        self.selected_files = files

        self.file_count_label.setText(

            (

                f"Selected Files: "

                f"{len(files)}"

            )

        )

        self.upload_button.setEnabled(

            True

        )

        self.clear_button.setEnabled(

            True

        )

        self.status_label.setText(

            "Status: Files ready to upload"

        )

        self.create_file_table()

    # ==================================================
    # CREATE TABLE
    # ==================================================

    def create_file_table(

        self

    ):

        self.table.setRowCount(

            0

        )

        for file_path in self.selected_files:

            row = (

                self.table.rowCount()

            )

            self.table.insertRow(

                row

            )

            file_name = (

                file_path.split(

                    "/"

                )[-1]

            )

            self.table.setItem(

                row,

                0,

                QTableWidgetItem(

                    file_name

                )

            )

            self.table.setItem(

                row,

                1,

                QTableWidgetItem(

                    "-"

                )

            )

            self.table.setItem(

                row,

                2,

                QTableWidgetItem(

                    "READY"

                )

            )

            self.table.setItem(

                row,

                3,

                QTableWidgetItem(

                    "0 / 0"

                )

            )

            self.table.setItem(

                row,

                4,

                QTableWidgetItem(

                    "0%"

                )

            )

    # ==================================================
    # START UPLOAD
    # ==================================================

    def start_upload(

        self

    ):

        if not self.selected_files:

            return

        self.upload_button.setEnabled(

            False

        )

        self.select_button.setEnabled(

            False

        )

        self.clear_button.setEnabled(

            False

        )

        self.status_label.setText(

            "Status: Uploading files..."

        )

        self.jobs = {}

        self.upload_workers = []

        self.status_workers = []

        for index, file_path in enumerate(

            self.selected_files

        ):

            worker = UploadWorker(

                file_path,

                self.upload_url

            )

            worker.upload_finished.connect(

                lambda data, row=index:

                self.upload_finished(

                    data,

                    row

                )

            )

            worker.error.connect(

                lambda error, row=index:

                self.upload_error(

                    error,

                    row

                )

            )

            self.upload_workers.append(

                worker

            )

            worker.start()

    # ==================================================
    # SINGLE FILE UPLOAD FINISHED
    # ==================================================

    def upload_finished(

        self,

        response_data,

        row

    ):

        job_id = (

            response_data.get(

                "job_id"

            )

        )

        if not job_id:

            self.upload_error(

                "No job ID returned",

                row

            )

            return

        file_name = (

            self.table.item(

                row,

                0

            ).text()

        )

        self.jobs[job_id] = {

            "row": row,

            "file_name": file_name,

            "status": "QUEUED",

        }

        self.table.setItem(

            row,

            1,

            QTableWidgetItem(

                str(

                    job_id

                )

            )

        )

        self.table.setItem(

            row,

            2,

            QTableWidgetItem(

                "QUEUED"

            )

        )

        self.status_label.setText(

            (

                f"Status: "

                f"{len(self.jobs)} / "

                f"{len(self.selected_files)} "

                "files uploaded"

            )

        )

        self.start_status_monitor(

            job_id,

            row

        )

    # ==================================================
    # START STATUS MONITOR
    # ==================================================

    def start_status_monitor(

        self,

        job_id,

        row

    ):

        worker = StatusWorker(

            job_id,

            self.status_url

        )

        worker.status_updated.connect(

            self.status_updated

        )

        worker.error.connect(

            lambda error:

            self.status_error(

                error,

                row

            )

        )

        self.status_workers.append(

            worker

        )

        worker.start()

    # ==================================================
    # STATUS UPDATE
    # ==================================================

    def status_updated(

        self,

        data

    ):

        job_id = data.get(

            "job_id"

        )

        if job_id not in self.jobs:

            return

        row = (

            self.jobs[job_id]["row"]

        )

        status = data.get(

            "status",

            "UNKNOWN"

        )

        total_rows = data.get(

            "total_rows",

            0

        )

        processed_rows = data.get(

            "processed_rows",

            0

        )

        progress = data.get(

            "progress",

            0

        )

        self.jobs[job_id]["status"] = (

            status

        )

        self.table.setItem(

            row,

            2,

            QTableWidgetItem(

                status

            )

        )

        self.table.setItem(

            row,

            3,

            QTableWidgetItem(

                (

                    f"{processed_rows:,}"

                    " / "

                    f"{total_rows:,}"

                )

            )

        )

        self.table.setItem(

            row,

            4,

            QTableWidgetItem(

                f"{progress:.2f}%"

            )

        )

        self.update_overall_progress()

    # ==================================================
    # OVERALL PROGRESS
    # ==================================================

    def update_overall_progress(

        self

    ):

        total_files = (

            len(

                self.jobs

            )

        )

        completed_files = 0

        total_progress = 0

        for job in self.jobs.values():

            status = job["status"]

            if status == "COMPLETED":

                completed_files += 1

                total_progress += 100

            elif status == "PROCESSING":

                total_progress += 50

        if total_files == 0:

            return

        average_progress = (

            total_progress

            / total_files

        )

        self.overall_progress.setValue(

            int(

                average_progress

            )

        )

        self.overall_progress_label.setText(

            (

                f"Completed: "

                f"{completed_files} / "

                f"{total_files}"

                f" | Overall Progress: "

                f"{average_progress:.2f}%"

            )

        )

        if completed_files == total_files:

            self.status_label.setText(

                "Status: All imports completed successfully"

            )

            self.select_button.setEnabled(

                True

            )

            self.clear_button.setEnabled(

                True

            )

    # ==================================================
    # UPLOAD ERROR
    # ==================================================

    def upload_error(

        self,

        error,

        row

    ):

        self.table.setItem(

            row,

            2,

            QTableWidgetItem(

                "UPLOAD FAILED"

            )

        )

        self.status_label.setText(

            "Status: Upload error"

        )

        QMessageBox.critical(

            self,

            "Upload Error",

            str(

                error

            )

        )

    # ==================================================
    # STATUS ERROR
    # ==================================================

    def status_error(

        self,

        error,

        row

    ):

        self.table.setItem(

            row,

            2,

            QTableWidgetItem(

                "STATUS ERROR"

            )

        )

        QMessageBox.critical(

            self,

            "Status Error",

            str(

                error

            )

        )

    # ==================================================
    # CLEAR
    # ==================================================

    def clear_files(

        self

    ):

        self.selected_files = []

        self.jobs = {}

        self.table.setRowCount(

            0

        )

        self.file_count_label.setText(

            "Selected Files: 0"

        )

        self.overall_progress.setValue(

            0

        )

        self.overall_progress_label.setText(

            "Overall Progress: 0 / 0"

        )

        self.status_label.setText(

            "Status: Ready"

        )

        self.upload_button.setEnabled(

            False

        )

        self.clear_button.setEnabled(

            False

        )

    # ==================================================
    # CLOSE APPLICATION
    # ==================================================

    def closeEvent(

        self,

        event

    ):

        for worker in self.status_workers:

            worker.stop()

            worker.wait()

        for worker in self.upload_workers:

            worker.quit()

            worker.wait()

        event.accept()