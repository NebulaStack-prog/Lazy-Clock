import sys
from datetime import datetime
from math import cos, sin, radians

from PySide6.QtCore import Qt, QPoint, QPointF, QTimer, QSettings
from PySide6.QtGui import QColor, QPainter, QPen, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QSystemTrayIcon, QMenu, QDialog, QFormLayout,
    QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QSlider, QSpinBox,
    QColorDialog, QLabel, QDialogButtonBox,
)

DEFAULTS = {
    'size': 500, 'opacity': 100, 'smooth': True, 'top': False,
    'locked': False, 'hour_color': '#111111', 'minute_color': '#222222',
    'second_color': '#dd2222', 'hour_width': 12, 'minute_width': 8,
    'second_width': 2,
}


def bounded(value, default, low, high):
    try:
        return min(high, max(low, int(value)))
    except (ValueError, TypeError, OverflowError):
        return default


def as_bool(value):
    return str(value).lower() in ('true', '1', 'yes')


class Clock(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.drag = None
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle('Lazy Clock | NESTIMS')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.apply()

    def apply(self):
        cfg = self.controller.cfg
        visible = self.isVisible()
        pos = self.pos()
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if cfg['top']:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        if self.windowFlags() != flags:
            self.setWindowFlags(flags)
        self.setFixedSize(cfg['size'], cfg['size'])
        self.setWindowOpacity(cfg['opacity'] / 100)
        self.move(pos)
        self.controller.keep_on_screen(self)
        if visible:
            self.show()
        self.update_timer()
        self.update()

    def update_timer(self):
        self.timer.stop()
        if self.isVisible():
            self.timer.start(33 if self.controller.cfg['smooth'] else 200)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_timer()
        self.update()

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def paintEvent(self, event):
        cfg = self.controller.cfg
        now = datetime.now()
        sec = now.second + (now.microsecond / 1e6 if cfg['smooth'] else 0)
        minute = now.minute + sec / 60
        hour = now.hour % 12 + minute / 60
        center = QPointF(self.width() / 2, self.height() / 2)
        scale = self.width() / 700
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # A nearly transparent handle permits dragging at the centre on Windows.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 1))
        painter.drawEllipse(center, 18, 18)
        for name, angle, length in (
            ('hour', hour * 30, 140), ('minute', minute * 6, 200),
            ('second', sec * 6, 235),
        ):
            a = radians(angle - 90)
            pen = QPen(QColor(cfg[name + '_color']))
            pen.setWidthF(max(1.0, cfg[name + '_width'] * scale))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(center, QPointF(center.x() + cos(a) * length * scale,
                                             center.y() + sin(a) * length * scale))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(cfg['hour_color']))
        painter.drawEllipse(center, max(3, 8 * scale), max(3, 8 * scale))
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.controller.cfg['locked']:
            self.drag = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag = None
        self.controller.keep_on_screen(self)
        self.controller.save()

    def contextMenuEvent(self, event):
        self.controller.menu.popup(event.globalPos())

    def closeEvent(self, event):
        if self.controller.quitting:
            event.accept()
        else:
            event.ignore()
            self.controller.toggle_clock()


class SettingsDialog(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Lazy Clock настройки')
        self.setMinimumWidth(390)
        self.controls = {}
        self.colors = {}
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('NESTIMS / LAZY CLOCK 2.0'))
        form = QFormLayout()
        layout.addLayout(form)
        for key, label, lo, hi in (
            ('size', 'Размер окна, px', 180, 700),
            ('opacity', 'Непрозрачность, %', 20, 100),
            ('hour_width', 'Толщина часовой стрелки', 1, 24),
            ('minute_width', 'Толщина минутной стрелки', 1, 24),
            ('second_width', 'Толщина секундной стрелки', 1, 12),
        ):
            w = QSpinBox(); w.setRange(lo, hi)
            form.addRow(label, w); self.controls[key] = w
        for key, label in (('smooth', 'Плавное движение'), ('top', 'Поверх всех окон'),
                           ('locked', 'Блокировать перемещение')):
            w = QCheckBox(); form.addRow(label, w); self.controls[key] = w
        for key, label in (('hour_color', 'Часовая стрелка'), ('minute_color', 'Минутная стрелка'),
                           ('second_color', 'Секундная стрелка')):
            b = QPushButton(); b.clicked.connect(lambda checked=False, k=key: self.choose(k))
            form.addRow(label, b); self.colors[key] = b
        row = QHBoxLayout(); layout.addLayout(row)
        for title, mode in (('Для светлых обоев', 'light'), ('Для тёмных обоев', 'dark')):
            b = QPushButton(title); b.clicked.connect(lambda checked=False, m=mode: self.preset(m)); row.addWidget(b)
        reset = QPushButton('Сбросить настройки'); reset.clicked.connect(lambda: self.populate(DEFAULTS)); layout.addWidget(reset)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Apply)
        buttons.accepted.connect(self.accept_settings); buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        layout.addWidget(buttons)
        self.populate(controller.cfg)

    def set_color(self, key, color):
        button = self.colors[key]
        button.setText(color)
        button.setStyleSheet('border: 1px solid #888; border-left: 26px solid ' + color + '; padding: 4px;')

    def populate(self, cfg):
        for key, widget in self.controls.items():
            if isinstance(widget, QCheckBox): widget.setChecked(cfg[key])
            else: widget.setValue(cfg[key])
        for key in self.colors: self.set_color(key, cfg[key])

    def choose(self, key):
        color = QColorDialog.getColor(QColor(self.colors[key].text()), self)
        if color.isValid(): self.set_color(key, color.name())

    def preset(self, mode):
        colors = ('#eeeeee', '#bbbbbb', '#ff4444') if mode == 'dark' else ('#111111', '#222222', '#dd2222')
        for key, value in zip(self.colors, colors): self.set_color(key, value)

    def apply_settings(self):
        cfg = self.controller.cfg
        for key, widget in self.controls.items():
            cfg[key] = widget.isChecked() if isinstance(widget, QCheckBox) else widget.value()
        for key, button in self.colors.items(): cfg[key] = button.text()
        self.controller.apply()

    def accept_settings(self):
        self.apply_settings(); self.accept()


class Controller:
    def __init__(self, app):
        self.app = app
        self.quitting = False
        self.settings = QSettings('NESTIMS', 'LazyClock')
        self.cfg = dict(DEFAULTS)
        for key, default in DEFAULTS.items():
            v = self.settings.value(key, default)
            if isinstance(default, bool): self.cfg[key] = as_bool(v)
            elif isinstance(default, int):
                lo, hi = {'size': (180, 700), 'opacity': (20, 100), 'hour_width': (1,24),
                          'minute_width': (1,24), 'second_width': (1,12)}[key]
                self.cfg[key] = bounded(v, default, lo, hi)
            else:
                color = QColor(str(v)); self.cfg[key] = color.name() if color.isValid() else default
        self.clock = Clock(self)
        pos = self.settings.value('position')
        if isinstance(pos, QPoint): self.clock.move(pos)
        else: self.center_clock()
        self.keep_on_screen(self.clock)
        self.menu = QMenu()
        self.toggle_action = self.menu.addAction('Показать / скрыть'); self.toggle_action.triggered.connect(self.toggle_clock)
        self.top_action = self.menu.addAction('Поверх всех окон'); self.top_action.setCheckable(True); self.top_action.setChecked(self.cfg['top']); self.top_action.toggled.connect(self.set_top)
        self.menu.addAction('Настройки', self.open_settings)
        self.menu.addAction('Вернуть в центр', self.recenter)
        self.menu.addSeparator(); self.menu.addAction('Выйти', self.quit)
        self.tray = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            pix = QPixmap(32,32); pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setBrush(QColor('#eeeeee')); p.setPen(Qt.PenStyle.NoPen); p.drawEllipse(2,2,28,28)
            p.setPen(QPen(QColor('#111111'),2)); p.drawLine(16,16,16,7); p.drawLine(16,16,23,19); p.end()
            self.tray = QSystemTrayIcon(QIcon(pix), self.clock)
            self.tray.setToolTip('Lazy Clock 1.1 / NESTIMS')
            self.tray.setContextMenu(self.menu); self.tray.activated.connect(self.tray_click); self.tray.show()
        else:
            self.toggle_action.setEnabled(False)
        self.clock.show()
        self.app.aboutToQuit.connect(self.save)

    def keep_on_screen(self, widget):
        screens = self.app.screens()
        if not screens: return
        # Keep the centre handle reachable even after a monitor is disconnected.
        center = widget.pos() + QPoint(widget.width()//2, widget.height()//2)
        if not any(s.availableGeometry().contains(center) for s in screens):
            g = self.app.primaryScreen().availableGeometry()
            widget.move(g.center() - QPoint(widget.width()//2, widget.height()//2))

    def center_clock(self):
        s = self.app.primaryScreen()
        if s: self.clock.move(s.availableGeometry().center() - QPoint(self.clock.width()//2,self.clock.height()//2))

    def recenter(self):
        self.center_clock(); self.clock.show(); self.save()

    def save(self):
        for key, value in self.cfg.items(): self.settings.setValue(key, value)
        self.settings.setValue('position', self.clock.pos()); self.settings.sync()

    def apply(self):
        self.clock.apply()
        self.top_action.blockSignals(True); self.top_action.setChecked(self.cfg['top']); self.top_action.blockSignals(False)
        self.save()

    def set_top(self, checked):
        self.cfg['top'] = checked; self.apply()

    def toggle_clock(self):
        if not self.tray: return
        if self.clock.isVisible(): self.clock.hide()
        else: self.keep_on_screen(self.clock); self.clock.show()

    def tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick: self.toggle_clock()

    def open_settings(self):
        SettingsDialog(self).exec()

    def quit(self):
        if self.quitting: return
        self.quitting = True; self.save()
        if self.tray: self.tray.hide()
        self.clock.close(); self.app.quit()


def main():
    app = QApplication(sys.argv); app.setQuitOnLastWindowClosed(False)
    controller = Controller(app)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
