import os

from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QGridLayout,
    QAbstractItemView,
)

from worker import (
    UploadWorker,
    StatusWorker
)


class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        # ==================================================
        # WINDOW
        # ==================================================

        self.setWindowTitle(
            "HDMS | Historical Data Management System"
        )

        self.resize(
            1450,
            850
        )

        self.setMinimumSize(
            1100,
            700
        )

        # ==================================================
        # BACKEND URLS
        # ==================================================

        self.upload_url = (
            "http://10.203.6.124:8000/"
            "api/uploader/upload/futstk/"
        )

        self.opt_upload_url = (
            "http://10.203.6.124:8000/"
            "api/uploader/upload/optstk/"
        )

        self.status_url = (
            "http://10.203.6.124:8000/"
            "api/uploader/status/"
        )

        # ==================================================
        # DATA
        # ==================================================

        self.selected_files = []

        self.jobs = {}

        self.upload_workers = []

        self.status_workers = []

        # ==================================================
        # UI
        # ==================================================

        self.setup_ui()

        self.load_stylesheet()

    # ======================================================
    # LOAD QSS
    # ======================================================

    def load_stylesheet(self):

        qss_path = os.path.join(
            os.path.dirname(__file__),
            "style.qss"
        )

        try:

            with open(
                qss_path,
                "r",
                encoding="utf-8"
            ) as file:

                self.setStyleSheet(
                    file.read()
                )

        except FileNotFoundError:

            QMessageBox.critical(
                self,
                "Style Error",
                "style.qss file was not found."
            )

    # ======================================================
    # SETUP UI
    # ======================================================

    def setup_ui(self):

        # ==================================================
        # MAIN LAYOUT
        # ==================================================

        main_layout = QHBoxLayout()

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(0)

        # ==================================================
        # SIDEBAR
        # ==================================================

        sidebar = QFrame()

        sidebar.setObjectName(
            "sidebar"
        )

        sidebar.setFixedWidth(
            245
        )

        sidebar_layout = QVBoxLayout()

        sidebar_layout.setContentsMargins(
            22,
            28,
            22,
            24
        )

        sidebar_layout.setSpacing(
            12
        )

        # --------------------------------------------------
        # LOGO
        # --------------------------------------------------

        logo_layout = QHBoxLayout()

        logo_icon = QLabel(
            "H"
        )

        logo_icon.setObjectName(
            "logo_icon"
        )

        logo_icon.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        logo_icon.setFixedSize(
            44,
            44
        )

        logo_text_layout = QVBoxLayout()

        logo_text_layout.setSpacing(
            0
        )

        logo_title = QLabel(
            "HDMS"
        )

        logo_title.setObjectName(
            "logo_title"
        )

        logo_subtitle = QLabel(
            "DATA PLATFORM"
        )

        logo_subtitle.setObjectName(
            "logo_subtitle"
        )

        logo_text_layout.addWidget(
            logo_title
        )

        logo_text_layout.addWidget(
            logo_subtitle
        )

        logo_layout.addWidget(
            logo_icon
        )

        logo_layout.addSpacing(
            10
        )

        logo_layout.addLayout(
            logo_text_layout
        )

        sidebar_layout.addLayout(
            logo_layout
        )

        sidebar_layout.addSpacing(
            35
        )

        # --------------------------------------------------
        # NAVIGATION
        # --------------------------------------------------

        nav_title = QLabel(
            "WORKSPACE"
        )

        nav_title.setObjectName(
            "section_label"
        )

        sidebar_layout.addWidget(
            nav_title
        )

        self.dashboard_button = (
            self.create_nav_button(
                "◈   Dashboard",
                active=True
            )
        )

        self.upload_nav_button = (
            self.create_nav_button(
                "⇧   Data Upload"
            )
        )

        self.jobs_nav_button = (
            self.create_nav_button(
                "▤   Import Jobs"
            )
        )

        self.database_nav_button = (
            self.create_nav_button(
                "▦   Database"
            )
        )

        sidebar_layout.addWidget(
            self.dashboard_button
        )

        sidebar_layout.addWidget(
            self.upload_nav_button
        )

        sidebar_layout.addWidget(
            self.jobs_nav_button
        )

        sidebar_layout.addWidget(
            self.database_nav_button
        )

        sidebar_layout.addStretch()

        # --------------------------------------------------
        # SYSTEM STATUS
        # --------------------------------------------------

        system_frame = QFrame()

        system_frame.setObjectName(
            "system_frame"
        )

        system_layout = QVBoxLayout()

        system_layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        system_layout.setSpacing(
            7
        )

        system_title = QLabel(
            "SYSTEM STATUS"
        )

        system_title.setObjectName(
            "system_title"
        )

        status_row = QHBoxLayout()

        status_dot = QLabel(
            "●"
        )

        status_dot.setObjectName(
            "online_dot"
        )

        status_text = QLabel(
            "Backend Connected"
        )

        status_text.setObjectName(
            "system_status"
        )

        status_row.addWidget(
            status_dot
        )

        status_row.addWidget(
            status_text
        )

        status_row.addStretch()

        version = QLabel(
            "HDMS v1.0.0"
        )

        version.setObjectName(
            "version_label"
        )

        system_layout.addWidget(
            system_title
        )

        system_layout.addLayout(
            status_row
        )

        system_layout.addWidget(
            version
        )

        system_frame.setLayout(
            system_layout
        )

        sidebar_layout.addWidget(
            system_frame
        )

        sidebar.setLayout(
            sidebar_layout
        )

        # ==================================================
        # CONTENT
        # ==================================================

        content = QFrame()

        content.setObjectName(
            "content"
        )

        content_layout = QVBoxLayout()

        content_layout.setContentsMargins(
            34,
            30,
            34,
            30
        )

        content_layout.setSpacing(
            24
        )

        # ==================================================
        # TOP BAR
        # ==================================================

        top_bar = QHBoxLayout()

        heading_layout = QVBoxLayout()

        heading_layout.setSpacing(
            3
        )

        page_title = QLabel(
            "Data Operations"
        )

        page_title.setObjectName(
            "page_title"
        )

        page_subtitle = QLabel(
            "Centralized historical market data management"
        )

        page_subtitle.setObjectName(
            "page_subtitle"
        )

        heading_layout.addWidget(
            page_title
        )

        heading_layout.addWidget(
            page_subtitle
        )

        top_bar.addLayout(
            heading_layout
        )

        top_bar.addStretch()

        user_label = QLabel(
            "VR"
        )

        user_label.setObjectName(
            "user_avatar"
        )

        user_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        user_label.setFixedSize(
            42,
            42
        )

        user_name = QLabel(
            "Vishal Rajput"
        )

        user_name.setObjectName(
            "user_name"
        )

        top_bar.addWidget(
            user_label
        )

        top_bar.addSpacing(
            10
        )

        top_bar.addWidget(
            user_name
        )

        content_layout.addLayout(
            top_bar
        )

        # ==================================================
        # WELCOME CARD
        # ==================================================

        welcome_card = QFrame()

        welcome_card.setObjectName(
            "welcome_card"
        )

        welcome_layout = QHBoxLayout()

        welcome_layout.setContentsMargins(
            28,
            24,
            28,
            24
        )

        welcome_text_layout = QVBoxLayout()

        welcome_text_layout.setSpacing(
            7
        )

        welcome_label = QLabel(
            "WELCOME TO HDMS"
        )

        welcome_label.setObjectName(
            "welcome_label"
        )

        welcome_title = QLabel(
            "Welcome to HDMS by Vishal Rajput"
        )

        welcome_title.setObjectName(
            "welcome_title"
        )

        welcome_description = QLabel(
            "Your centralized platform for managing, "
            "processing, and organizing historical "
            "market data."
        )

        welcome_description.setObjectName(
            "welcome_description"
        )

        welcome_description.setWordWrap(
            True
        )

        welcome_text_layout.addWidget(
            welcome_label
        )

        welcome_text_layout.addWidget(
            welcome_title
        )

        welcome_text_layout.addWidget(
            welcome_description
        )

        welcome_layout.addLayout(
            welcome_text_layout
        )

        welcome_layout.addStretch()

        welcome_icon = QLabel(
            "◈"
        )

        welcome_icon.setObjectName(
            "welcome_icon"
        )

        welcome_icon.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        welcome_icon.setFixedSize(
            100,
            100
        )

        welcome_layout.addWidget(
            welcome_icon
        )

        welcome_card.setLayout(
            welcome_layout
        )

        content_layout.addWidget(
            welcome_card
        )

        # ==================================================
        # STAT CARDS
        # ==================================================

        stats_layout = QGridLayout()

        stats_layout.setSpacing(
            16
        )

        self.files_card = (
            self.create_stat_card(
                "SELECTED FILES",
                "0",
                "Ready for processing",
                "▤"
            )
        )

        self.jobs_card = (
            self.create_stat_card(
                "ACTIVE JOBS",
                "0",
                "Currently processing",
                "◉"
            )
        )

        self.completed_card = (
            self.create_stat_card(
                "COMPLETED",
                "0",
                "Successfully imported",
                "✓"
            )
        )

        self.progress_card = (
            self.create_stat_card(
                "OVERALL PROGRESS",
                "0%",
                "Upload pipeline",
                "↗"
            )
        )

        stats_layout.addWidget(
            self.files_card,
            0,
            0
        )

        stats_layout.addWidget(
            self.jobs_card,
            0,
            1
        )

        stats_layout.addWidget(
            self.completed_card,
            0,
            2
        )

        stats_layout.addWidget(
            self.progress_card,
            0,
            3
        )

        content_layout.addLayout(
            stats_layout
        )

        # ==================================================
        # IMPORT HEADER
        # ==================================================

        upload_header = QHBoxLayout()

        upload_title_layout = QVBoxLayout()

        upload_title_layout.setSpacing(
            3
        )

        upload_title = QLabel(
            "Import Data"
        )

        upload_title.setObjectName(
            "section_title"
        )

        upload_subtitle = QLabel(
            "Select historical CSV files to begin "
            "the ingestion pipeline"
        )

        upload_subtitle.setObjectName(
            "section_subtitle"
        )

        upload_title_layout.addWidget(
            upload_title
        )

        upload_title_layout.addWidget(
            upload_subtitle
        )

        upload_header.addLayout(
            upload_title_layout
        )

        upload_header.addStretch()

        self.select_button = QPushButton(
            "＋  Select CSV Files"
        )

        self.select_button.setObjectName(
            "primary_button"
        )

        self.select_button.clicked.connect(
            self.select_files
        )

        self.upload_button = QPushButton(
            "⇧  Start Import"
        )

        self.upload_button.setObjectName(
            "success_button"
        )

        self.upload_button.setEnabled(
            False
        )

        self.upload_button.clicked.connect(
            self.start_upload
        )

        self.clear_button = QPushButton(
            "Clear"
        )

        self.clear_button.setObjectName(
            "secondary_button"
        )

        self.clear_button.setEnabled(
            False
        )

        self.clear_button.clicked.connect(
            self.clear_files
        )

        upload_header.addWidget(
            self.select_button
        )

        upload_header.addWidget(
            self.upload_button
        )

        upload_header.addWidget(
            self.clear_button
        )

        content_layout.addLayout(
            upload_header
        )

        # ==================================================
        # PROGRESS PANEL
        # ==================================================

        progress_frame = QFrame()

        progress_frame.setObjectName(
            "progress_frame"
        )

        progress_layout = QVBoxLayout()

        progress_layout.setContentsMargins(
            20,
            16,
            20,
            16
        )

        progress_layout.setSpacing(
            10
        )

        progress_top = QHBoxLayout()

        self.status_label = QLabel(
            "Ready to import historical data"
        )

        self.status_label.setObjectName(
            "status_label"
        )

        self.overall_progress_label = QLabel(
            "0%"
        )

        self.overall_progress_label.setObjectName(
            "progress_percentage"
        )

        progress_top.addWidget(
            self.status_label
        )

        progress_top.addStretch()

        progress_top.addWidget(
            self.overall_progress_label
        )

        self.overall_progress = QProgressBar()

        self.overall_progress.setValue(
            0
        )

        self.overall_progress.setTextVisible(
            False
        )

        self.overall_progress.setFixedHeight(
            8
        )

        progress_layout.addLayout(
            progress_top
        )

        progress_layout.addWidget(
            self.overall_progress
        )

        progress_frame.setLayout(
            progress_layout
        )

        content_layout.addWidget(
            progress_frame
        )

        # ==================================================
        # TABLE
        # ==================================================

        table_frame = QFrame()

        table_frame.setObjectName(
            "table_frame"
        )

        table_layout = QVBoxLayout()

        table_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        table_header = QHBoxLayout()

        table_title = QLabel(
            "Import Queue"
        )

        table_title.setObjectName(
            "table_title"
        )

        self.file_count_label = QLabel(
            "0 files selected"
        )

        self.file_count_label.setObjectName(
            "file_count_label"
        )

        table_header.addWidget(
            table_title
        )

        table_header.addStretch()

        table_header.addWidget(
            self.file_count_label
        )

        self.table = QTableWidget()

        self.table.setColumnCount(
            5
        )

        self.table.setHorizontalHeaderLabels(
            [
                "FILE",
                "JOB ID",
                "STATUS",
                "ROWS PROCESSED",
                "PROGRESS"
            ]
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.setShowGrid(
            False
        )

        self.table.setMinimumHeight(
            230
        )

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )

        for i in range(
            1,
            5
        ):

            header.setSectionResizeMode(
                i,
                QHeaderView.ResizeMode.ResizeToContents
            )

        table_layout.addLayout(
            table_header
        )

        table_layout.addWidget(
            self.table
        )

        table_frame.setLayout(
            table_layout
        )

        content_layout.addWidget(
            table_frame
        )

        content.setLayout(
            content_layout
        )

        main_layout.addWidget(
            sidebar
        )

        main_layout.addWidget(
            content
        )

        self.setLayout(
            main_layout
        )

    # ======================================================
    # STAT CARD
    # ======================================================

    def create_stat_card(
        self,
        title,
        value,
        subtitle,
        icon
    ):

        card = QFrame()

        card.setObjectName(
            "stat_card"
        )

        layout = QHBoxLayout()

        layout.setContentsMargins(
            18,
            16,
            18,
            16
        )

        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            3
        )

        title_label = QLabel(
            title
        )

 
