import sys
import signal
from math import sin, cos, radians
from datetime import datetime

from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import (QColor, QPainter, QPen, QAction, QIcon, QPixmap)
from PySide6.QtWidgets import (QApplication, QWidget, QSystemTrayIcon, QMenu, QMainWindow)

class ClockWidget(QWidget):

    def __init__(self, always_on_top=False):
        super().__init__()

        self.setFixedSize(700, 700)

        flags = Qt.FramelessWindowHint | Qt.Tool

        if always_on_top:
            flags |= Qt.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.dragPos = QPoint()

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000 // 60)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2

        now = datetime.now()
        sec = now.second + now.microsecond / 1000000
        minute = now.minute + sec / 60
        hour = (now.hour % 12) + minute / 60

        self.draw_hand(painter, cx, cy, hour * 30, 140, 12, QColor("#111111"))
        self.draw_hand(painter, cx, cy, minute * 6, 200, 8, QColor("#222222"))
        self.draw_hand(painter, cx, cy, sec * 6, 235, 2, QColor("#d22"))

        painter.setBrush(QColor("black"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(int(cx), int(cy)), 8, 8)

    def draw_hand(self, painter, cx, cy, angle, length, width, color):
        angle -= 90
        x = cx + cos(radians(angle)) * length
        y = cy + sin(radians(angle)) * length

        pen = QPen(color)
        pen.setWidth(width)
        pen.setCapStyle(Qt.RoundCap)

        painter.setPen(pen)
        painter.drawLine(int(cx), int(cy), int(x), int(y))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Запоминаем глобальную позицию мыши
            self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # Используем глобальную позицию для перемещения
            new_pos = event.globalPosition().toPoint()
            self.move(self.pos() + new_pos - self.dragPos)
            self.dragPos = new_pos


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.clock_widget = ClockWidget(always_on_top=False)

        self.create_tray_icon()

        self.clock_widget.show()

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        self.quit_app()

    def create_tray_icon(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setBrush(QColor("#3498db"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()

        icon = QIcon(pixmap)

        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(icon)

        menu = QMenu()

        show_action = QAction("Показать/скрыть часы", self)
        show_action.triggered.connect(self.toggle_clock)
        menu.addAction(show_action)

        top_action = QAction("Поверх всех окон", self)
        top_action.setCheckable(True)
        top_action.triggered.connect(self.toggle_top)
        menu.addAction(top_action)

        menu.addSeparator()

        quit_action = QAction("Выйти", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()
        self.tray.setToolTip("Часы на рабочем столе")

        self.tray.activated.connect(self.tray_clicked)

    def tray_clicked(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_clock()

    def toggle_clock(self):
        if self.clock_widget.isVisible():
            self.clock_widget.hide()
            self.tray.setToolTip("Часы скрыты (двойной клик для показа)")
        else:
            self.clock_widget.show()
            self.tray.setToolTip("Часы на рабочем столе")

    def toggle_top(self, checked):
        if checked:
            self.clock_widget.setWindowFlags(
                self.clock_widget.windowFlags() | Qt.WindowStaysOnTopHint
            )
        else:
            self.clock_widget.setWindowFlags(
                self.clock_widget.windowFlags() & ~Qt.WindowStaysOnTopHint
            )
        self.clock_widget.show()

    def quit_app(self):
        print("Завершение работы...")
        if hasattr(self, 'tray'):
            self.tray.hide()
        if hasattr(self, 'clock_widget'):
            self.clock_widget.close()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    window.hide()

    app.aboutToQuit.connect(window.quit_app)

    sys.exit(app.exec())
