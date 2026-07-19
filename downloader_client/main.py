import sys

from PyQt6.QtWidgets import QApplication

from ui import DownloaderWindow


def main():

    app = QApplication(

        sys.argv

    )

    window = DownloaderWindow()

    window.show()

    sys.exit(

        app.exec()

    )


if __name__ == "__main__":

    main()
