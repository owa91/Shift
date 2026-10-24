"""
Shift Browser — оболочка (PyQt6).

Плоский дизайн без контуров: только заливки, скругления и плавные анимации.
Здесь нет логики браузера — только интерфейс. Содержимое страницы (QtImage)
подключается через ShiftWindow.add_tab(viewport=...).

Публичный API окна ShiftWindow:
    сигналы:  navigateRequested(str), backRequested(), forwardRequested(),
              reloadRequested(), menuRequested(),
              tabChanged(int), tabClosed(int), tabCreated(int)
    методы:   add_tab(title, viewport=None, select=True) -> int
              close_tab(index), set_current_tab(index), set_tab_title(index, title)
              viewport(index) -> QWidget
              get_canvas_size(index=None) -> CanvasSize(width, height)
              set_image(image, index=None) / set_picture(...)
              set_url(url), set_loading(bool), set_progress(0..1)
              set_nav_enabled(back, forward)
              minimize_window(), toggle_maximize(), close_window()
              set_blur(on) -> bool, is_blur_enabled() -> bool

Запуск:  win = create_window()  # вернёт готовое окно;  run_app()  # цикл событий

Окно безрамочное: кнопки «свернуть / развернуть / закрыть» нарисованы справа
в ряду вкладок, пустое место ряда работает как заголовок (перетаскивание,
двойной клик — развернуть), размер меняется за любой край.
"""
from __future__ import annotations

import math
import sys

from PyQt6.QtCore import (QEasingCurve, QEvent, QPointF, QRectF, Qt, QTimer,
                          QVariantAnimation, pyqtSignal)
from PyQt6.QtGui import (QColor, QCursor, QFontMetrics, QImage, QKeySequence,
                         QPainter, QPainterPath, QPen, QPixmap, QRegion,
                         QShortcut)
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit,
                             QMainWindow, QSizePolicy, QStackedWidget,
                             QVBoxLayout, QWidget)

try:
    import skia
except Exception:
    skia = None

Curve = QEasingCurve.Type
Align = Qt.AlignmentFlag


# ────────────────────────────── Тема ──────────────────────────────
class Theme:
    BAR = QColor("#0F1115")          # фон ряда вкладок
    TOOLBAR = QColor("#1A1D24")      # панель инструментов = активная вкладка
    CONTENT = QColor("#0B0C0F")      # фон области страницы

    TAB_HOVER = QColor("#171A20")
    HOVER = QColor("#2A2E38")
    PRESS = QColor("#343947")

    FIELD = QColor("#0F1115")
    FIELD_HOVER = QColor("#13161B")
    FIELD_FOCUS = QColor("#252A36")

    TEXT = QColor("#E6E8EE")
    TEXT_DIM = QColor("#8A90A0")
    ICON = QColor("#9AA0B2")
    ICON_HI = QColor("#FFFFFF")

    ACCENT = QColor("#6C8CFF")
    ACCENT_HOVER = QColor("#839EFF")
    ACCENT_PRESS = QColor("#5A78E6")

    DANGER = QColor("#E5484D")       # кнопка «закрыть окно» при наведении
    DANGER_PRESS = QColor("#C93C41")

    TAB_H = 42
    TOOLBAR_H = 52
    RADIUS = 10
    WINDOW_RADIUS = 12               # скругление углов окна
    BAR_BLUR_ALPHA = 150             # прозрачность ряда вкладок (0–255), когда включено размытие


def mix(a: QColor, b: QColor, t: float) -> QColor:
    t = max(0.0, min(1.0, t))
    return QColor(
        int(a.red() + (b.red() - a.red()) * t),
        int(a.green() + (b.green() - a.green()) * t),
        int(a.blue() + (b.blue() - a.blue()) * t),
        int(a.alpha() + (b.alpha() - a.alpha()) * t),
    )


class Animated:
    """Миксин: плавно меняет числовой атрибут виджета (hover, active и т.д.)."""

    def animate(self, attr: str, target: float, ms: int = 180,
                curve: QEasingCurve.Type = Curve.OutCubic):
        store = self.__dict__.setdefault("_anims", {})
        old = store.get(attr)
        if old is not None:
            old.stop()
        a = QVariantAnimation(self)
        a.setStartValue(float(getattr(self, attr)))
        a.setEndValue(float(target))
        a.setDuration(ms)
        a.setEasingCurve(curve)

        def on_value(v):
            setattr(self, attr, float(v))
            self.update()

        a.valueChanged.connect(on_value)
        store[attr] = a
        a.start()
        return a


def corner_path(rect: QRectF, top: float = 0.0, bottom: float = 0.0) -> QPainterPath:
    """Контур прямоугольника, у которого скруглены только верхние (top) и/или
    нижние (bottom) углы. Радиус 0 — угол остаётся прямым."""
    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    path = QPainterPath()
    path.moveTo(x + top, y)
    path.lineTo(x + w - top, y)
    if top:
        path.arcTo(QRectF(x + w - 2 * top, y, 2 * top, 2 * top), 90, -90)
    path.lineTo(x + w, y + h - bottom)
    if bottom:
        path.arcTo(QRectF(x + w - 2 * bottom, y + h - 2 * bottom, 2 * bottom, 2 * bottom), 0, -90)
    path.lineTo(x + bottom, y + h)
    if bottom:
        path.arcTo(QRectF(x, y + h - 2 * bottom, 2 * bottom, 2 * bottom), 270, -90)
    path.lineTo(x, y + top)
    if top:
        path.arcTo(QRectF(x, y, 2 * top, 2 * top), 180, -90)
    path.closeSubpath()
    return path


class Surface(QWidget):
    """Залитый прямоугольник; при необходимости с закруглёнными верхними/нижними углами."""

    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self._color = color
        self._top = 0.0
        self._bottom = 0.0
        self._alpha: int | None = None   # None — цвет непрозрачный

    def set_radius(self, top: float = 0.0, bottom: float = 0.0):
        """Задаёт радиус скругления верхних и нижних углов (0 — прямые)."""
        self._top, self._bottom = float(top), float(bottom)
        self.update()

    def set_alpha(self, alpha: int | None):
        """Делает заливку полупрозрачной (alpha 0–255) — сквозь неё виден размытый фон.
        None возвращает обычную непрозрачную заливку."""
        self._alpha = alpha
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        color = QColor(self._color)
        if self._alpha is not None:
            color.setAlpha(self._alpha)
        if not (self._top or self._bottom):
            p.fillRect(self.rect(), color)
            return
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawPath(corner_path(QRectF(self.rect()), self._top, self._bottom))


# ────────────────────────────── Иконки ──────────────────────────────
def draw_icon(p: QPainter, kind: str, color: QColor, angle: float = 0.0):
    """Рисует глиф 36x36 с центром в (0, 0)."""
    pen = QPen(color, 1.9)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.save()
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    if kind in ("back", "forward"):
        if kind == "forward":
            p.scale(-1, 1)
        p.drawLine(QPointF(-6, 0), QPointF(7, 0))
        path = QPainterPath()
        path.moveTo(-1, -6)
        path.lineTo(-7, 0)
        path.lineTo(-1, 6)
        p.drawPath(path)

    elif kind == "reload":
        p.rotate(angle)
        r, start, span = 7.0, 50, 280
        p.drawArc(QRectF(-r, -r, 2 * r, 2 * r), start * 16, span * 16)
        end = math.radians(start + span)
        ex, ey = r * math.cos(end), -r * math.sin(end)
        tx, ty = -math.sin(end), -math.cos(end)
        nx, ny = -ty, tx
        tri = QPainterPath()
        tri.moveTo(ex + tx * 3.4, ey + ty * 3.4)
        tri.lineTo(ex - tx * 1.2 + nx * 3.4, ey - ty * 1.2 + ny * 3.4)
        tri.lineTo(ex - tx * 1.2 - nx * 3.4, ey - ty * 1.2 - ny * 3.4)
        tri.closeSubpath()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawPath(tri)

    elif kind == "plus":
        p.drawLine(QPointF(-6, 0), QPointF(6, 0))
        p.drawLine(QPointF(0, -6), QPointF(0, 6))

    elif kind == "close":
        p.drawLine(QPointF(-4, -4), QPointF(4, 4))
        p.drawLine(QPointF(-4, 4), QPointF(4, -4))

    elif kind == "minimize":
        p.drawLine(QPointF(-5, 0), QPointF(5, 0))

    elif kind == "maximize":
        p.drawRoundedRect(QRectF(-5, -5, 10, 10), 2, 2)

    elif kind == "restore":
        # два наложенных квадрата: передний целиком, задний — только видимый «уголок»
        p.drawRoundedRect(QRectF(-5, -2, 7, 7), 1.5, 1.5)
        back = QPainterPath()
        back.moveTo(-2, -2)
        back.lineTo(-2, -5)
        back.lineTo(5, -5)
        back.lineTo(5, 2)
        back.lineTo(2, 2)
        p.drawPath(back)

    elif kind == "menu":
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        for y in (-6, 0, 6):
            p.drawEllipse(QPointF(0, y), 1.7, 1.7)

    p.restore()


# ────────────────────────────── Кнопка ──────────────────────────────
class FlatButton(Animated, QWidget):
    """Плоская кнопка: иконка или текст. Hover/нажатие анимируются."""

    clicked = pyqtSignal()

    def __init__(self, kind: str = "", label: str = "", size: int = 36,
                 accent: bool = False, danger: bool = False,
                 width: int | None = None, parent=None):
        super().__init__(parent)
        self.kind, self.label, self.accent = kind, label, accent
        self.danger = danger     # красная подсветка (кнопка закрытия окна)
        self._hover = 0.0
        self._press = 0.0
        self._angle = 0.0
        self._spin: QVariantAnimation | None = None
        self._pressed = False

        if label:
            f = self.font()
            f.setPointSizeF(10)
            f.setWeight(f.Weight.DemiBold)
            self.setFont(f)
            w = QFontMetrics(f).horizontalAdvance(label) + 36
            self.setFixedSize(w, size)
        else:
            self.setFixedSize(width or size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    # --- вращение (для кнопки «перезагрузить» во время загрузки)
    def set_spinning(self, on: bool):
        """Включает/выключает вращение значка. Нужно для кнопки «перезагрузить»: крутится, пока идёт загрузка."""
        if on and self._spin is None:
            a = QVariantAnimation(self)
            a.setStartValue(0.0)
            a.setEndValue(360.0)
            a.setDuration(900)
            a.setLoopCount(-1)
            a.setEasingCurve(Curve.Linear)
            a.valueChanged.connect(self._on_spin)
            a.start()
            self._spin = a
        elif not on and self._spin is not None:
            self._spin.stop()
            self._spin = None
            self._angle = 0.0
            self.update()

    def _on_spin(self, v):
        self._angle = float(v)
        self.update()

    # --- события
    def enterEvent(self, e):
        self.animate("_hover", 1.0, 140)

    def leaveEvent(self, e):
        self._pressed = False
        self.animate("_hover", 0.0, 220)
        self.animate("_press", 0.0, 140)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.animate("_press", 1.0, 90)

    def mouseReleaseEvent(self, e):
        was = self._pressed
        self._pressed = False
        self.animate("_press", 0.0, 220, Curve.OutBack)
        if was and e.button() == Qt.MouseButton.LeftButton \
                and self.rect().contains(e.position().toPoint()):
            self.clicked.emit()

    # --- рисование
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.3)
        w, h = self.width(), self.height()
        p.translate(w / 2, h / 2)
        s = 1.0 - 0.08 * self._press
        p.scale(s, s)
        rect = QRectF(-w / 2, -h / 2, w, h)
        radius = min(h / 2, 18) if self.label else h / 2

        if self.accent:
            col = mix(Theme.ACCENT, Theme.ACCENT_HOVER, self._hover)
            col = mix(col, Theme.ACCENT_PRESS, self._press)
        elif self.danger:
            col = mix(Theme.DANGER, Theme.DANGER_PRESS, self._press)
            col.setAlphaF(max(self._hover, self._press))
        else:
            col = mix(Theme.HOVER, Theme.PRESS, self._press)
            col.setAlphaF(max(self._hover * 0.9, self._press))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(col)
        p.drawRoundedRect(rect, radius, radius)

        if self.label:
            p.setPen(QColor("#FFFFFF") if self.accent else Theme.TEXT)
            p.drawText(rect, Align.AlignCenter, self.label)
        else:
            ic = mix(Theme.ICON, Theme.ICON_HI, self._hover)
            draw_icon(p, self.kind, ic, self._angle)


# ────────────────────────────── Вкладка ──────────────────────────────
class TabButton(Animated, QWidget):
    activated = pyqtSignal(object)
    closeRequested = pyqtSignal(object)
    MAX_W = 230

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._hover = 0.0
        self._active = 0.0
        self._close_hover = 0.0
        self._size_anim: QVariantAnimation | None = None

        self.setFixedHeight(Theme.TAB_H)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(0)
        self.setMaximumWidth(0)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_title(self, t: str):
        self._title = t
        self.update()

    def set_active(self, on: bool):
        self.animate("_active", 1.0 if on else 0.0, 240, Curve.OutCubic)

    # --- анимация ширины (появление / закрытие)
    def _run_width(self, start, end, ms, curve, done=None):
        if self._size_anim is not None:
            self._size_anim.stop()
        a = QVariantAnimation(self)
        a.setStartValue(float(start))
        a.setEndValue(float(end))
        a.setDuration(ms)
        a.setEasingCurve(curve)
        a.valueChanged.connect(lambda v: self.setMaximumWidth(int(v)))
        if done:
            a.finished.connect(done)
        self._size_anim = a
        a.start()

    def grow(self):
        self._run_width(0, self.MAX_W, 260, Curve.OutCubic,
                        lambda: self.setMinimumWidth(64))

    def shrink(self, done):
        self.setMinimumWidth(0)
        self._run_width(max(self.width(), 1), 0, 200, Curve.InCubic, done)

    # --- геометрия
    def _close_rect(self) -> QRectF:
        return QRectF(self.width() - 32, (self.height() - 22) / 2, 22, 22)

    # --- события
    def enterEvent(self, e):
        self.animate("_hover", 1.0, 140)

    def leaveEvent(self, e):
        self.animate("_hover", 0.0, 220)
        self.animate("_close_hover", 0.0, 140)

    def mouseMoveEvent(self, e):
        over = self._close_rect().contains(e.position())
        target = 1.0 if over else 0.0
        if abs(self._close_hover - target) > 0.01 and (
                self.__dict__.get("_anims", {}).get("_close_hover") is None
                or self.__dict__["_anims"]["_close_hover"].endValue() != target):
            self.animate("_close_hover", target, 120)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.MiddleButton:
            self.closeRequested.emit(self)
        elif e.button() == Qt.MouseButton.LeftButton:
            if self.width() >= 90 and self._close_rect().contains(e.position()):
                self.closeRequested.emit(self)
            else:
                self.activated.emit(self)

    # --- рисование
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        if w <= 2:
            return
        p.setOpacity(min(1.0, w / 90))
        a, hv = self._active, self._hover

        top = 6 * (1 - a)
        bottom = (h - 6) + (6 + Theme.RADIUS) * a   # активная уходит вниз и «сливается» с панелью
        # без наведения неактивная вкладка прозрачна: под ней виден фон ряда (и размытие)
        hover_col = QColor(Theme.TAB_HOVER)
        hover_col.setAlphaF(hv)
        col = mix(hover_col, Theme.TOOLBAR, a)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(col)
        p.drawRoundedRect(QRectF(2, top, w - 4, bottom - top), Theme.RADIUS, Theme.RADIUS)

        # акцентная «пилюля» сверху активной вкладки
        if a > 0.01:
            pw = 20 * a
            p.setBrush(Theme.ACCENT)
            p.drawRoundedRect(QRectF((w - pw) / 2, 1.5, pw, 3), 1.5, 1.5)

        show_close = w >= 90
        right = w - 38 if show_close else w - 14
        p.setPen(mix(Theme.TEXT_DIM, Theme.TEXT, max(a, hv)))
        fm = QFontMetrics(self.font())
        text = fm.elidedText(self._title, Qt.TextElideMode.ElideRight, int(right - 16))
        p.drawText(QRectF(16, 0, right - 16, h), Align.AlignVCenter | Align.AlignLeft, text)

        if show_close:
            vis = max(hv, a * 0.75)
            r = self._close_rect()
            bg = QColor(Theme.PRESS)
            bg.setAlphaF(self._close_hover)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(bg)
            p.drawRoundedRect(r, 11, 11)
            p.save()
            p.translate(r.center())
            p.setOpacity(p.opacity() * vis)
            draw_icon(p, "close", mix(Theme.ICON, Theme.ICON_HI, self._close_hover))
            p.restore()


class TabBar(QWidget):
    currentChanged = pyqtSignal(int)
    tabCloseRequested = pyqtSignal(int)
    newTabRequested = pyqtSignal()
    titleDragRequested = pyqtSignal()     # потянули за пустое место — двигать окно
    titleDoubleClicked = pyqtSignal()     # двойной клик по пустому месту — развернуть/восстановить

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(Theme.TAB_H)
        self._tabs: list[TabButton] = []
        self._current: TabButton | None = None
        self._press_pos = None            # точка нажатия на пустом месте (для перетаскивания окна)

        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(8, 0, 8, 0)
        self._lay.setSpacing(2)
        self._new = FlatButton("plus", size=32)
        self._new.clicked.connect(self.newTabRequested)
        self._lay.addWidget(self._new, 0, Align.AlignVCenter)
        self._lay.addStretch(0)

    # --- пустое место ряда вкладок работает как заголовок окна
    def mousePressEvent(self, e):
        """Нажатие на пустое место: запоминаем точку, чтобы понять, потянут ли окно."""
        if e.button() == Qt.MouseButton.LeftButton:
            self._press_pos = e.position().toPoint()

    def mouseMoveEvent(self, e):
        """Мышь ушла от точки нажатия дальше порога (4 px) — просим окно начать перемещение.
        Двигаем не сразу при нажатии, иначе системное перемещение «съест» двойной клик."""
        if self._press_pos is not None and e.buttons() & Qt.MouseButton.LeftButton:
            if (e.position().toPoint() - self._press_pos).manhattanLength() > 4:
                self._press_pos = None
                self.titleDragRequested.emit()

    def mouseReleaseEvent(self, e):
        """Кнопку отпустили — перетаскивание не началось, сбрасываем точку."""
        self._press_pos = None

    def mouseDoubleClickEvent(self, e):
        """Двойной клик по пустому месту ряда вкладок — развернуть/восстановить окно."""
        if e.button() == Qt.MouseButton.LeftButton:
            self._press_pos = None
            self.titleDoubleClicked.emit()

    def count(self) -> int:
        """Сколько вкладок сейчас открыто."""
        return len(self._tabs)

    def current_index(self) -> int:
        """Индекс активной вкладки или -1, если вкладок нет."""
        return self._tabs.index(self._current) if self._current in self._tabs else -1

    def add_tab(self, title: str, select: bool = True) -> int:
        """Добавляет вкладку с анимацией появления и возвращает её индекс.
        select=True — сразу делает её активной."""
        tab = TabButton(title)
        tab.activated.connect(self._on_activated)
        tab.closeRequested.connect(self._on_close)
        self._lay.insertWidget(self._lay.indexOf(self._new), tab, 1)
        self._tabs.append(tab)
        tab.show()
        tab.grow()
        idx = len(self._tabs) - 1
        if select:
            self.set_current(idx)
        return idx

    def set_title(self, index: int, title: str):
        """Меняет заголовок вкладки по индексу (длинный текст обрезается с «…»)."""
        self._tabs[index].set_title(title)

    def set_current(self, index: int):
        """Делает вкладку активной (плавно подсвечивает её) и испускает currentChanged(index)."""
        if not 0 <= index < len(self._tabs):
            return
        tab = self._tabs[index]
        changed = tab is not self._current
        self._current = tab
        for t in self._tabs:
            t.set_active(t is tab)
        if changed:
            self.currentChanged.emit(index)

    def remove_tab(self, index: int):
        """Убирает вкладку с анимацией схлопывания. Если она была активной, активной станет соседняя."""
        tab = self._tabs.pop(index)
        was_current = tab is self._current

        def cleanup():
            self._lay.removeWidget(tab)
            tab.deleteLater()

        tab.shrink(cleanup)
        if was_current:
            self._current = None
            if self._tabs:
                self.set_current(min(index, len(self._tabs) - 1))

    def next_tab(self, step: int = 1):
        """Переключает активную вкладку на step шагов вперёд (отрицательное — назад), по кругу."""
        if self._tabs:
            self.set_current((self.current_index() + step) % len(self._tabs))

    def _on_activated(self, tab):
        self.set_current(self._tabs.index(tab))

    def _on_close(self, tab):
        if tab in self._tabs:
            self.tabCloseRequested.emit(self._tabs.index(tab))


# ────────────────────────── Адресная строка ──────────────────────────
class AddressBar(Animated, QWidget):
    submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hover = 0.0
        self._focus = 0.0
        self.setFixedHeight(36)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self.edit = QLineEdit(self)
        self.edit.setFrame(False)
        self.edit.setPlaceholderText("Введите адрес или поисковый запрос")
        self.edit.setStyleSheet(
            "QLineEdit{background:transparent;border:none;color:%s;"
            "selection-background-color:%s;font-size:13px;}"
            % (Theme.TEXT.name(), Theme.ACCENT_PRESS.name()))
        self.edit.installEventFilter(self)
        self.edit.returnPressed.connect(lambda: self.submitted.emit(self.edit.text().strip()))

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.addWidget(self.edit)

    def set_url(self, url: str):
        """Показывает адрес в поле ввода. Если пользователь сейчас печатает (поле в фокусе), текст не трогает."""
        if not self.edit.hasFocus():
            self.edit.setText(url)

    def focus_address(self):
        """Ставит курсор в адресную строку и выделяет весь текст (то же, что Ctrl+L)."""
        self.edit.setFocus()
        self.edit.selectAll()

    def eventFilter(self, obj, ev):
        if obj is self.edit:
            if ev.type() == QEvent.Type.FocusIn:
                self.animate("_focus", 1.0, 200)
                QTimer.singleShot(0, self.edit.selectAll)
            elif ev.type() == QEvent.Type.FocusOut:
                self.animate("_focus", 0.0, 260)
        return super().eventFilter(obj, ev)

    def enterEvent(self, e):
        self.animate("_hover", 1.0, 160)

    def leaveEvent(self, e):
        self.animate("_hover", 0.0, 220)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        col = mix(mix(Theme.FIELD, Theme.FIELD_HOVER, self._hover),
                  Theme.FIELD_FOCUS, self._focus)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(col)
        h = self.height()
        p.drawRoundedRect(QRectF(self.rect()), h / 2, h / 2)


# ────────────────────────── Полоса загрузки ──────────────────────────
class ProgressLine(Animated, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(2)
        self._value = 0.0
        self._opacity = 0.0
        self._phase = 0.0
        self._indeterminate = False
        self._loop: QVariantAnimation | None = None
        self._gen = 0

    def _stop_loop(self):
        if self._loop is not None:
            self._loop.stop()
            self._loop = None

    def start(self):
        """Запускает полосу загрузки в режиме «прогресс неизвестен»: светлый отрезок бегает слева направо."""
        self._gen += 1
        self._stop_loop()
        self._indeterminate = True
        self._value = 0.0
        self.animate("_opacity", 1.0, 150)
        a = QVariantAnimation(self)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setDuration(1100)
        a.setLoopCount(-1)
        a.setEasingCurve(Curve.InOutSine)
        a.valueChanged.connect(self._on_phase)
        a.start()
        self._loop = a

    def _on_phase(self, v):
        self._phase = float(v)
        self.update()

    def set_progress(self, value: float):
        """Переключает полосу в режим точного прогресса и плавно доводит её до value (0..1)."""
        self._stop_loop()
        self._indeterminate = False
        self.animate("_opacity", 1.0, 120)
        self.animate("_value", max(0.0, min(1.0, value)), 350)

    def finish(self):
        """Доводит полосу до конца, затем плавно гасит её и сбрасывает в ноль."""
        self._gen += 1
        gen = self._gen
        self._stop_loop()
        self._indeterminate = False
        self.animate("_value", 1.0, 240)

        def fade():
            if gen == self._gen:
                self.animate("_opacity", 0.0, 300)

        def reset():
            if gen == self._gen:
                self._value = 0.0

        QTimer.singleShot(280, fade)
        QTimer.singleShot(700, reset)

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), Theme.CONTENT)
        if self._opacity <= 0.01:
            return
        p.setOpacity(self._opacity)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(Theme.ACCENT)
        w, h = self.width(), self.height()
        if self._indeterminate:
            seg = w * 0.3
            x = -seg + (w + seg) * self._phase
            p.drawRect(QRectF(x, 0, seg, h))
        else:
            p.drawRect(QRectF(0, 0, w * self._value, h))


# ────────────────────────── Область страницы ──────────────────────────
class Veil(QWidget):
    """Лёгкое затемнение, которое тает при смене вкладки."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._alpha = 0.0
        self._anim: QVariantAnimation | None = None
        self.hide()

    def flash(self):
        if self._anim is not None:
            self._anim.stop()
        a = QVariantAnimation(self)
        a.setStartValue(0.6)
        a.setEndValue(0.0)
        a.setDuration(280)
        a.setEasingCurve(Curve.OutCubic)
        a.valueChanged.connect(self._set)
        a.finished.connect(self.hide)
        self._anim = a
        self.setGeometry(self.parentWidget().rect())
        self.show()
        self.raise_()
        a.start()

    def _set(self, v):
        self._alpha = float(v)
        self.update()

    def paintEvent(self, _):
        c = QColor(Theme.CONTENT)
        c.setAlphaF(self._alpha)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        radius = getattr(self.parentWidget(), "bottom_radius", 0.0)
        p.drawPath(corner_path(QRectF(self.rect()), 0.0, radius))


class ContentStack(QStackedWidget):
    """Область страниц. Скругляет нижние углы окна: фон рисует с антиалиасингом,
    а у самих страниц (в том числе у QtImage) обрезает углы маской."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bottom_radius = 0.0
        self._veil = Veil(self)

    def set_bottom_radius(self, r: float):
        """Задаёт радиус скругления нижних углов (0 — прямые) и обновляет маски страниц."""
        self.bottom_radius = float(r)
        self._apply_masks()
        self.update()

    def addWidget(self, widget):
        """Добавляет страницу и сразу применяет к ней маску скругления."""
        index = super().addWidget(widget)
        self._apply_masks()
        return index

    def _apply_masks(self):
        """Обрезает нижние углы у всех страниц. Радиус маски на 1 px меньше, чтобы
        гладкий край рисовал фон стека, а не зубчатый край маски."""
        r = self.bottom_radius
        for i in range(self.count()):
            page = self.widget(i)
            if r > 0:
                path = corner_path(QRectF(self.rect()), 0.0, max(r - 1.0, 0.0))
                page.setMask(QRegion(path.toFillPolygon().toPolygon()))
            else:
                page.clearMask()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(Theme.CONTENT)
        p.drawPath(corner_path(QRectF(self.rect()), 0.0, self.bottom_radius))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._veil.setGeometry(self.rect())
        self._apply_masks()

    def flash(self):
        """Запускает короткое затемнение области страницы (при смене вкладки)."""
        self._veil.flash()


class CanvasSize(tuple):
    """Размер холста (width, height), поддерживающий как обращение по индексу/распаковку,
    так и атрибуты .width и .height."""

    def __new__(cls, width: int, height: int):
        return super().__new__(cls, (int(width), int(height)))

    @property
    def width(self) -> int:
        return self[0]

    @property
    def height(self) -> int:
        return self[1]

    def __repr__(self) -> str:
        return f"CanvasSize(width={self.width}, height={self.height})"


def _convert_to_qimage(image) -> QImage | None:
    """Преобразует входное изображение (QImage, QPixmap, skia.Picture, skia.Surface,
    skia.Image, numpy-массив, байты или путь к файлу) в объект QImage."""
    if image is None:
        return None
    if isinstance(image, QImage):
        return image
    if isinstance(image, QPixmap):
        return image.toImage()

    # Поддержка skia.Picture (векторный рисунок Skia)
    if skia is not None and isinstance(image, skia.Picture):
        w = max(1, int(image.cullRect().width()))
        h = max(1, int(image.cullRect().height()))
        surf = skia.Surface(w, h)
        if surf is not None:
            surf.getCanvas().drawPicture(image)
            image = surf.makeImageSnapshot()

    # Поддержка skia.Surface и skia.Image
    if hasattr(image, "makeImageSnapshot"):
        image = image.makeImageSnapshot()
    if hasattr(image, "imageInfo") and hasattr(image, "tobytes"):
        w = int(image.width())
        h = int(image.height())
        raw = image.tobytes()
        color_type = str(image.imageInfo().colorType())
        fmt = (QImage.Format.Format_ARGB32_Premultiplied
               if "BGRA" in color_type
               else QImage.Format.Format_RGBA8888_Premultiplied)
        return QImage(raw, w, h, 4 * w, fmt).copy()
    if hasattr(image, "encodeToData"):
        try:
            data = image.encodeToData()
            if data is not None:
                return QImage.fromData(bytes(data))
        except Exception:
            pass

    # Поддержка numpy ndarray
    if hasattr(image, "shape") and hasattr(image, "data"):
        try:
            h, w = image.shape[:2]
            channels = image.shape[2] if len(image.shape) > 2 else 1
            if channels == 4:
                return QImage(image.data, w, h, image.strides[0], QImage.Format.Format_RGBA8888).copy()
            elif channels == 3:
                return QImage(image.data, w, h, image.strides[0], QImage.Format.Format_RGB888).copy()
        except Exception:
            pass

    # Поддержка байтов (PNG, JPG, BMP и т.д.)
    if isinstance(image, (bytes, bytearray, memoryview)):
        img = QImage()
        if img.loadFromData(bytes(image)):
            return img
        return QImage.fromData(bytes(image))

    # Поддержка пути к файлу
    if isinstance(image, str):
        return QImage(image)

    return None


class QtImage(QWidget):
    """Область страницы браузера.
    Отображает холст страницы, отрисованный движком Alt (Skia).
    Использует разделяемый буфер памяти (Zero-Copy) для прямой отрисовки Skia в QImage без копирований.
    Полностью совместима с прозрачностью окна, системным размытием Windows (Blur)
    и скруглением углов."""

    def __init__(self, text: str = "", image: QImage | None = None, parent=None):
        super().__init__(parent)
        self._text = text
        self._image: QImage | None = None
        self._draw_callback = None

        # Разделяемый буфер (Zero-Copy) между Skia Surface и QImage
        self._buf_w: int = 0
        self._buf_h: int = 0
        self._buffer: bytearray | None = None
        self._surface = None
        self._qimage: QImage | None = None

        if image is not None:
            self.set_image(image)

    def _reallocate_buffer(self, w: int, h: int) -> None:
        """Перевыделяет разделяемый буфер пикселей только при изменении размеров виджета."""
        w = max(1, int(w))
        h = max(1, int(h))
        self._buf_w = w
        self._buf_h = h

        if skia is not None:
            self._buffer = bytearray(w * h * 4)
            info = skia.ImageInfo.Make(
                w, h,
                skia.ColorType.kBGRA_8888_ColorType,
                skia.AlphaType.kPremul_AlphaType,
            )
            self._surface = skia.Surface.MakeRasterDirect(info, self._buffer, w * 4)
            if self._surface is not None:
                c = Theme.CONTENT
                self._surface.getCanvas().clear(skia.Color(c.red(), c.green(), c.blue(), c.alpha()))
            self._qimage = QImage(
                self._buffer,
                w,
                h,
                w * 4,
                QImage.Format.Format_ARGB32_Premultiplied,
            )
        else:
            self._buffer = None
            self._surface = None
            self._qimage = None

    def get_canvas(self):
        """Возвращает Skia Canvas, привязанный напрямую к разделяемому буферу (Zero-Copy)."""
        w = self.width()
        h = self.height()
        if w <= 1 or h <= 1:
            if self.parentWidget() and self.parentWidget().width() > 1:
                w = self.parentWidget().width()
                h = self.parentWidget().height()
            elif self.window() and self.window().width() > 1:
                w = self.window().width()
                h = max(1, self.window().height() - (Theme.TAB_H + Theme.TOOLBAR_H + 2))
            else:
                w = 1280
                h = 700

        if self._surface is None or self._buf_w != w or self._buf_h != h:
            self._reallocate_buffer(w, h)

        if self._surface is not None:
            return self._surface.getCanvas()
        return None

    def render_done(self) -> None:
        """Сигнализирует о готовности кадра в буфере и запрашивает перерисовку виджета."""
        self.update()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        w = max(1, e.size().width())
        h = max(1, e.size().height())
        if w != self._buf_w or h != self._buf_h:
            self._reallocate_buffer(w, h)

    def paintEvent(self, _):
        p = QPainter(self)
        if self._draw_callback is not None and skia is not None:
            canvas = self.get_canvas()
            if canvas is not None:
                try:
                    c = Theme.CONTENT
                    canvas.clear(skia.Color(c.red(), c.green(), c.blue(), c.alpha()))
                    self._draw_callback(canvas)
                except Exception:
                    pass
            if self._qimage is not None and not self._qimage.isNull():
                p.drawImage(0, 0, self._qimage)
        elif self._image is not None and not self._image.isNull():
            p.drawImage(0, 0, self._image)
        elif self._qimage is not None and not self._qimage.isNull():
            p.drawImage(0, 0, self._qimage)
        elif self._text:
            p.fillRect(self.rect(), Theme.CONTENT)
            p.setPen(Theme.TEXT_DIM)
            p.drawText(self.rect(), Align.AlignCenter, self._text)

    def set_draw_callback(self, callback) -> None:
        self._draw_callback = callback
        self._image = None
        self.update()

    set_drawer = set_draw_callback
    set_render_callback = set_draw_callback

    def set_image(self, image) -> None:
        if image is None:
            return

        if skia is not None and isinstance(image, skia.Picture):
            canvas = self.get_canvas()
            if canvas is not None:
                c = Theme.CONTENT
                canvas.clear(skia.Color(c.red(), c.green(), c.blue(), c.alpha()))
                canvas.drawPicture(image)
                self._image = None
                self._draw_callback = None
                self.update()
                return

        self._image = _convert_to_qimage(image)
        self._draw_callback = None
        self.update()

    def set_picture(self, image) -> None:
        self.set_image(image)

    def set_drawing(self, image) -> None:
        self.set_image(image)

    def image(self) -> QImage | None:
        if self._image is not None:
            return self._image
        return self._qimage

    def get_canvas_size(self) -> CanvasSize:
        w = self.width()
        h = self.height()
        if w > 0 and h > 0:
            return CanvasSize(w, h)
        if self._buf_w > 0 and self._buf_h > 0:
            return CanvasSize(self._buf_w, self._buf_h)
        return CanvasSize(800, 600)

    canvas_size = get_canvas_size


# Обратная совместимость для существующего кода
PlaceholderPage = QtImage
ImagePage = QtImage
GLCanvas = QtImage
ShiftGL = QtImage


# ────────────────────────────── Окно ──────────────────────────────
def enable_window_blur(widget: QWidget, enable: bool = True) -> bool:
    """Включает (enable=True) или выключает размытие фона позади окна.

    Размываются только прозрачные/полупрозрачные пиксели окна, поэтому blur виден
    ровно там, где мы рисуем полупрозрачную заливку (ряд вкладок).
    Qt сам размытия не умеет, нужен вызов системы:
      • Windows 10/11 — SetWindowCompositionAttribute (+ системное скругление на Win11);
      • остальные ОС — возвращает False, интерфейс остаётся непрозрачным.
    Возвращает True, если система приняла запрос."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [("AccentState", ctypes.c_int), ("AccentFlags", ctypes.c_int),
                        ("GradientColor", ctypes.c_uint), ("AnimationId", ctypes.c_int)]

        class WINCOMPATTRDATA(ctypes.Structure):
            _fields_ = [("Attribute", ctypes.c_int), ("Data", ctypes.c_void_p),
                        ("SizeOfData", ctypes.c_size_t)]

        hwnd = ctypes.c_void_p(int(widget.winId()))
        accent = ACCENT_POLICY(3 if enable else 0, 0, 0, 0)   # 3 = BLURBEHIND, 0 = выкл.
        data = WINCOMPATTRDATA(19, ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p),
                               ctypes.sizeof(accent))        # 19 = WCA_ACCENT_POLICY
        func = ctypes.windll.user32.SetWindowCompositionAttribute
        func.argtypes = [ctypes.c_void_p, ctypes.POINTER(WINCOMPATTRDATA)]
        func.restype = ctypes.c_int
        ok = bool(func(hwnd, ctypes.byref(data)))
        if ok and enable:
            # Windows 11: системное скругление углов, чтобы размытие не торчало за углами
            pref = ctypes.c_int(2)                            # DWMWCP_ROUND
            try:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 33, ctypes.byref(pref), ctypes.sizeof(pref))
            except Exception:
                pass
        return ok
    except Exception:
        return False


def set_native_corners(widget: QWidget, rounded: bool) -> None:
    """Windows 11: включает/выключает системное скругление углов окна.
    В развёрнутом режиме его нужно выключать, иначе система продолжит скруглять
    углы у окна, прижатого к краям экрана. На других ОС ничего не делает."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        hwnd = ctypes.c_void_p(int(widget.winId()))
        pref = ctypes.c_int(2 if rounded else 1)     # 2 = DWMWCP_ROUND, 1 = DWMWCP_DONOTROUND
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 33, ctypes.byref(pref), ctypes.sizeof(pref))   # 33 = DWMWA_WINDOW_CORNER_PREFERENCE
    except Exception:
        pass


class ShiftWindow(QMainWindow):
    navigateRequested = pyqtSignal(str)
    backRequested = pyqtSignal()
    forwardRequested = pyqtSignal()
    reloadRequested = pyqtSignal()
    menuRequested = pyqtSignal()
    tabChanged = pyqtSignal(int)
    tabClosed = pyqtSignal(int)
    tabCreated = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        global _active_window
        _active_window = self
        self.setWindowTitle("Shift")
        # убираем системную рамку: заголовок и кнопки теперь рисуем сами
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        # прозрачный фон окна: за скруглёнными углами виден рабочий стол
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._radius = float(Theme.WINDOW_RADIUS)   # текущий радиус скругления окна
        self._blur = False                          # включено ли размытие под вкладками
        self._radius_key = None                     # что применено в последний раз (радиус, системное скругление)
        self._edge_cursor = False        # сейчас показан курсор «потянуть за край»
        self.resize(1280, 800)
        self.setMinimumSize(640, 400)

        root = QWidget()
        col = QVBoxLayout(root)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        self.setCentralWidget(root)

        # ряд вкладок + кнопки управления окном справа
        self._tabs_row = tabs_row = Surface(Theme.BAR)
        tl = QHBoxLayout(tabs_row)
        tl.setContentsMargins(0, 0, 8, 0)
        tl.setSpacing(2)
        self.tabs = TabBar()
        tl.addWidget(self.tabs, 1)
        tl.addSpacing(6)
        self.btn_min = FlatButton("minimize", size=30, width=42)
        self.btn_max = FlatButton("maximize", size=30, width=42)
        self.btn_close = FlatButton("close", size=30, width=42, danger=True)
        for b in (self.btn_min, self.btn_max, self.btn_close):
            tl.addWidget(b, 0, Align.AlignVCenter)
        col.addWidget(tabs_row)

        # панель инструментов
        toolbar = Surface(Theme.TOOLBAR)
        toolbar.setFixedHeight(Theme.TOOLBAR_H)
        hl = QHBoxLayout(toolbar)
        hl.setContentsMargins(10, 0, 10, 0)
        hl.setSpacing(4)
        self.btn_back = FlatButton("back")
        self.btn_forward = FlatButton("forward")
        self.btn_reload = FlatButton("reload")
        self.address = AddressBar()
        self.btn_menu = FlatButton("menu")
        for b in (self.btn_back, self.btn_forward, self.btn_reload):
            hl.addWidget(b)
        hl.addSpacing(6)
        hl.addWidget(self.address, 1)
        hl.addSpacing(6)
        hl.addWidget(self.btn_menu)
        col.addWidget(toolbar)

        # полоса загрузки + страница
        self.progress = ProgressLine()
        col.addWidget(self.progress)
        self.stack = ContentStack()
        col.addWidget(self.stack, 1)

        # связи
        self.btn_back.clicked.connect(self.backRequested)
        self.btn_forward.clicked.connect(self.forwardRequested)
        self.btn_reload.clicked.connect(self.reloadRequested)
        self.btn_menu.clicked.connect(self.menuRequested)
        self.btn_min.clicked.connect(self.minimize_window)
        self.btn_max.clicked.connect(self.toggle_maximize)
        self.btn_close.clicked.connect(self.close_window)
        self.tabs.titleDragRequested.connect(self.start_move)
        self.tabs.titleDoubleClicked.connect(self.toggle_maximize)
        QApplication.instance().installEventFilter(self)   # ловим мышь у краёв для ресайза
        self.address.submitted.connect(self.navigateRequested)
        self.tabs.newTabRequested.connect(lambda: self.add_tab())
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._on_current_changed)
        self.set_nav_enabled(False, False)
        self._apply_window_radius()

        # горячие клавиши
        def sc(keys, fn):
            QShortcut(QKeySequence(keys), self, activated=fn)

        sc("Ctrl+T", lambda: self.add_tab())
        sc("Ctrl+W", lambda: self.close_tab(self.tabs.current_index()))
        sc("Ctrl+L", self.address.focus_address)
        sc("Ctrl+Tab", lambda: self.tabs.next_tab(1))
        sc("Ctrl+Shift+Tab", lambda: self.tabs.next_tab(-1))
        sc("F5", self.reloadRequested.emit)

    # --- управление окном
    def minimize_window(self):
        """«Скрыть»: сворачивает окно в панель задач."""
        self.showMinimized()

    def toggle_maximize(self):
        """«Развернуть / восстановить»: если окно развёрнуто — возвращает прежний размер,
        иначе разворачивает на весь экран (без перекрытия панели задач)."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def close_window(self):
        """«Закрыть»: закрывает окно целиком (вместе со всеми вкладками)."""
        self.close()

    def start_move(self):
        """Передаёт перетаскивание окна системе: работают привязка к краям экрана,
        разворот при перетаскивании к верху и «отрыв» развёрнутого окна."""
        handle = self.windowHandle()
        if handle is not None:
            handle.startSystemMove()

    def _edges_at(self, gpos) -> Qt.Edge:
        """По глобальной точке мыши определяет, у каких краёв окна она находится
        (полоса 6 px). В развёрнутом режиме краёв нет — ресайз отключён."""
        none = Qt.Edge(0)
        if self.isMaximized() or self.isFullScreen():
            return none
        r = self.frameGeometry()
        grip = 6
        edges = none
        if gpos.x() - r.left() < grip:
            edges |= Qt.Edge.LeftEdge
        elif r.right() - gpos.x() < grip:
            edges |= Qt.Edge.RightEdge
        if gpos.y() - r.top() < grip:
            edges |= Qt.Edge.TopEdge
        elif r.bottom() - gpos.y() < grip:
            edges |= Qt.Edge.BottomEdge
        return edges

    def _update_edge_cursor(self, edges: Qt.Edge):
        """Показывает курсор изменения размера (↔ ↕ ⤡ ⤢) у края окна и возвращает
        обычный, когда мышь отошла от края."""
        L, R, T, B = (Qt.Edge.LeftEdge, Qt.Edge.RightEdge,
                      Qt.Edge.TopEdge, Qt.Edge.BottomEdge)
        shape = None
        if edges in (L | T, R | B):
            shape = Qt.CursorShape.SizeFDiagCursor
        elif edges in (R | T, L | B):
            shape = Qt.CursorShape.SizeBDiagCursor
        elif edges & (L | R):
            shape = Qt.CursorShape.SizeHorCursor
        elif edges & (T | B):
            shape = Qt.CursorShape.SizeVerCursor

        if shape is not None:
            if self._edge_cursor:
                QApplication.changeOverrideCursor(QCursor(shape))
            else:
                QApplication.setOverrideCursor(QCursor(shape))
                self._edge_cursor = True
        elif self._edge_cursor:
            QApplication.restoreOverrideCursor()
            self._edge_cursor = False

    def eventFilter(self, obj, ev):
        """Следит за мышью во всех виджетах окна: у края меняет курсор, а нажатие
        левой кнопки у края запускает системное изменение размера."""
        t = ev.type()
        if t in (QEvent.Type.MouseMove, QEvent.Type.MouseButtonPress) \
                and isinstance(obj, QWidget) and obj.window() is self:
            edges = self._edges_at(ev.globalPosition().toPoint())
            if t == QEvent.Type.MouseButtonPress:
                if edges and ev.button() == Qt.MouseButton.LeftButton \
                        and self.windowHandle() is not None:
                    self.windowHandle().startSystemResize(edges)
                    return True
            elif not ev.buttons():
                self._update_edge_cursor(edges)
        elif t == QEvent.Type.Leave and obj is self:
            self._update_edge_cursor(Qt.Edge(0))
        return super().eventFilter(obj, ev)

    def _apply_window_radius(self):
        """Скругляет углы окна (Theme.WINDOW_RADIUS). В развёрнутом и полноэкранном
        режиме углы прямые, чтобы окно прилегало к краям экрана."""
        flat = self.isMaximized() or self.isFullScreen()
        r = 0.0 if flat else self._radius
        native = self._blur and not flat
        if (r, native) == self._radius_key:      # ничего не изменилось — не перерисовываем
            return
        self._radius_key = (r, native)
        self._tabs_row.set_radius(top=r)
        self.stack.set_bottom_radius(r)
        set_native_corners(self, native)

    def set_blur(self, on: bool = True) -> bool:
        """Включает/выключает размытие фона под рядом вкладок.
        При включении ряд вкладок становится полупрозрачным (Theme.BAR_BLUR_ALPHA),
        и сквозь него виден размытый рабочий стол. Если ОС размытие не поддерживает,
        ряд остаётся обычным непрозрачным. Возвращает True, если размытие включено."""
        ok = enable_window_blur(self, on) if on else False
        if not on:
            enable_window_blur(self, False)
        self._blur = ok
        self._radius_key = None                  # заставить пересчитать скругление
        self._tabs_row.set_alpha(Theme.BAR_BLUR_ALPHA if ok else None)
        # на Windows 11 углы скругляет система — радиус у неё 8 px, подстраиваемся
        self._radius = 8.0 if (ok and sys.platform == "win32") else float(Theme.WINDOW_RADIUS)
        self._apply_window_radius()
        return ok

    def is_blur_enabled(self) -> bool:
        """Включено ли сейчас размытие под рядом вкладок."""
        return self._blur

    def resizeEvent(self, e):
        """Страховка: при любом изменении размера заново проверяет, развёрнуто ли окно.
        На некоторых ОС событие о смене состояния приходит с опозданием, и скругление
        иначе оставалось бы у развёрнутого окна."""
        super().resizeEvent(e)
        if hasattr(self, "stack"):
            self._apply_window_radius()

    def changeEvent(self, e):
        """При смене состояния окна переключает значок средней кнопки
        («квадрат» ⇄ «два квадрата») и включает/выключает скругление углов."""
        if e.type() == QEvent.Type.WindowStateChange and hasattr(self, "btn_max"):
            self.btn_max.kind = "restore" if self.isMaximized() else "maximize"
            self.btn_max.update()
            self._apply_window_radius()
        super().changeEvent(e)

    def closeEvent(self, e):
        """Перед закрытием снимает перехват мыши и возвращает обычный курсор."""
        QApplication.instance().removeEventFilter(self)
        self._update_edge_cursor(Qt.Edge(0))
        super().closeEvent(e)

    # --- вкладки
    def add_tab(self, title: str = "Новая вкладка", viewport: QWidget | None = None,
                select: bool = True) -> int:
        """Создаёт вкладку и возвращает её индекс.
        title — заголовок; viewport — виджет страницы (QtImage),
        если не задан, создаётся QtImage; select — сразу переключиться на вкладку.
        Испускает tabCreated(index)."""
        page = viewport or QtImage(title)
        self.stack.addWidget(page)
        idx = self.tabs.add_tab(title, select)
        self.tabCreated.emit(idx)
        return idx

    def get_canvas_size(self, index: int | None = None) -> CanvasSize:
        """Возвращает размер холста (области страницы) в пикселях: CanvasSize(width, height).
        Если index указан, возвращает размер конкретной вкладки, иначе — текущей/активной."""
        if not self.isVisible() and self.centralWidget() is not None:
            self.centralWidget().resize(self.size())
            if self.centralWidget().layout() is not None:
                self.centralWidget().layout().activate()

        page = None
        if index is not None and 0 <= index < self.stack.count():
            page = self.stack.widget(index)
        else:
            page = self.stack.currentWidget()

        if page is not None and page.width() > 0 and page.height() > 0:
            return CanvasSize(page.width(), page.height())

        if hasattr(self, "stack") and self.stack.width() > 0 and self.stack.height() > 0:
            return CanvasSize(self.stack.width(), self.stack.height())

        h_offset = Theme.TAB_H + Theme.TOOLBAR_H + 2
        w = max(1, self.width())
        h = max(1, self.height() - h_offset)
        return CanvasSize(w, h)

    canvas_size = get_canvas_size

    def set_image(self, image, index: int | None = None) -> None:
        """Задаёт рисунок холста для вкладки (по умолчанию текущей активной).
        Принимает QImage, QPixmap, skia.Surface, skia.Image, numpy ndarray, bytes или путь к файлу."""
        widget = None
        if index is not None and 0 <= index < self.stack.count():
            widget = self.stack.widget(index)
        else:
            widget = self.stack.currentWidget()

        if widget is not None:
            if hasattr(widget, "set_image"):
                widget.set_image(image)
            elif hasattr(widget, "set_picture"):
                widget.set_picture(image)

    def set_picture(self, image, index: int | None = None) -> None:
        """Задаёт рисунок холста (алиас для set_image)."""
        self.set_image(image, index)

    def set_drawing(self, image, index: int | None = None) -> None:
        """Задаёт рисунок холста (алиас для set_image)."""
        self.set_image(image, index)

    def set_drawer(self, callback, index: int | None = None) -> None:
        """Задаёт функцию прямой отрисовки на GPU-холсте Skia: callback(canvas)."""
        widget = None
        if index is not None and 0 <= index < self.stack.count():
            widget = self.stack.widget(index)
        else:
            widget = self.stack.currentWidget()

        if widget is not None:
            if hasattr(widget, "set_draw_callback"):
                widget.set_draw_callback(callback)
            elif hasattr(widget, "set_drawer"):
                widget.set_drawer(callback)

    set_draw_callback = set_drawer

    def get_canvas(self, index: int | None = None):
        """Возвращает Skia Canvas для прямой Zero-Copy отрисовки во вкладке."""
        widget = None
        if index is not None and 0 <= index < self.stack.count():
            widget = self.stack.widget(index)
        else:
            widget = self.stack.currentWidget()

        if widget is not None and hasattr(widget, "get_canvas"):
            return widget.get_canvas()
        return None

    def render_done(self, index: int | None = None) -> None:
        """Уведомляет окно, что отрисовка во вкладку завершена, и обновляет виджет."""
        widget = None
        if index is not None and 0 <= index < self.stack.count():
            widget = self.stack.widget(index)
        else:
            widget = self.stack.currentWidget()

        if widget is not None and hasattr(widget, "render_done"):
            widget.render_done()
        elif widget is not None:
            widget.update()

    def close_tab(self, index: int):
        """Закрывает вкладку и удаляет её страницу. Последняя вкладка закрывает всё окно.
        Испускает tabClosed(index) — по сигналу можно освободить Lua-runtime этой вкладки."""
        if not 0 <= index < self.tabs.count():
            return
        if self.tabs.count() == 1:
            self.close()
            return
        page = self.stack.widget(index)
        self.stack.removeWidget(page)
        page.deleteLater()
        self.tabs.remove_tab(index)
        self.tabClosed.emit(index)

    def current_tab(self) -> int:
        """Возвращает индекс текущей активной вкладки или -1, если вкладок нет."""
        return self.tabs.current_index()

    current_index = current_tab

    def set_current_tab(self, index: int):
        """Переключается на вкладку по индексу (с анимацией и затемнением страницы). Испускает tabChanged(index)."""
        self.tabs.set_current(index)

    def set_tab_title(self, index: int, title: str):
        """Меняет заголовок вкладки по индексу, например, когда страница сообщила свой title."""
        self.tabs.set_title(index, title)

    def viewport(self, index: int) -> QWidget:
        """Возвращает виджет страницы указанной вкладки (то, что передали в add_tab)."""
        return self.stack.widget(index)

    def _on_current_changed(self, index: int):
        """Показывает страницу выбранной вкладки, запускает затемнение и испускает tabChanged."""
        self.stack.setCurrentIndex(index)
        self.stack.flash()
        self.tabChanged.emit(index)

    # --- состояние интерфейса
    def set_url(self, url: str):
        """Выводит адрес текущей страницы в адресной строке. Не мешает, если пользователь сейчас печатает."""
        self.address.set_url(url)

    def set_nav_enabled(self, back: bool, forward: bool):
        """Включает/выключает кнопки «назад» и «вперёд». Выключенные становятся тусклыми и не нажимаются."""
        self.btn_back.setEnabled(back)
        self.btn_forward.setEnabled(forward)

    def set_loading(self, on: bool):
        """on=True: началась загрузка — значок перезагрузки вращается, под панелью бежит полоса.
        on=False: загрузка завершена — полоса доезжает до конца и гаснет, вращение останавливается."""
        self.btn_reload.set_spinning(on)
        if on:
            self.progress.start()
        else:
            self.progress.finish()

    def set_progress(self, value: float):
        """Показывает точный прогресс загрузки (0.0–1.0) вместо бегущей полосы. Можно вызывать много раз."""
        self.progress.set_progress(value)


# ────────────────────────────── Демо и модуль ──────────────────────────────
_app: QApplication | None = None     # держим ссылку, иначе Python удалит приложение
_active_window: ShiftWindow | None = None


def get_canvas_size(index: int | None = None, window: ShiftWindow | None = None) -> CanvasSize:
    """Возвращает размер холста (области страницы) в пикселях: CanvasSize(width, height).
    Использует переданное окно либо последнее активное/созданное окно."""
    win = window or _active_window
    if win is not None:
        return win.get_canvas_size(index)
    return CanvasSize(800, 600)


canvas_size = get_canvas_size
get_page_size = get_canvas_size


def get_canvas(index: int | None = None, window: ShiftWindow | None = None):
    """Возвращает Skia Canvas вкладки для прямой Zero-Copy отрисовки без копирования памяти."""
    win = window or _active_window
    if win is not None:
        return win.get_canvas(index)
    return None


def render_done(index: int | None = None, window: ShiftWindow | None = None) -> None:
    """Уведомляет о завершении отрисовки кадра в разделяемый буфер."""
    win = window or _active_window
    if win is not None:
        win.render_done(index)


def set_image(image, index: int | None = None, window: ShiftWindow | None = None) -> None:
    """Задаёт рисунок холста для вкладки (по умолчанию текущей) в окне браузера.
    Принимает QImage, QPixmap, skia.Surface, skia.Image, numpy ndarray, bytes или путь к файлу."""
    win = window or _active_window
    if win is not None:
        win.set_image(image, index)


set_picture = set_image
set_drawing = set_image
set_canvas_image = set_image


def set_drawer(callback, index: int | None = None, window: ShiftWindow | None = None) -> None:
    """Задаёт функцию прямой GPU-отрисовки холста вкладки: callback(canvas)."""
    win = window or _active_window
    if win is not None:
        win.set_drawer(callback, index)


set_draw_callback = set_drawer


def current_tab(window: ShiftWindow | None = None) -> int:
    """Возвращает индекс текущей активной вкладки или -1."""
    win = window or _active_window
    return win.current_tab() if win is not None else -1


current_index = current_tab


def create_window(title: str = "Shift", size: tuple[int, int] = (1280, 800),
                  blur: bool = True, show: bool = True) -> ShiftWindow:
    """Запускает интерфейс и возвращает готовое окно ShiftWindow.

    • создаёт QApplication, если его ещё нет (повторный вызов использует существующий);
    • ставит стиль Fusion и размер шрифта;
    • blur=True — пытается включить размытие под рядом вкладок (см. ShiftWindow.set_blur);
    • show=True — сразу показывает окно.
    Цикл событий здесь НЕ запускается: либо вызови run_app(), либо подключай свой
    (например, qasync). Приложение доступно через QApplication.instance()."""
    global _app, _active_window
    _app = QApplication.instance() or QApplication(sys.argv)
    _app.setStyle("Fusion")
    font = _app.font()
    font.setPointSizeF(10)
    _app.setFont(font)

    win = ShiftWindow()
    _active_window = win
    win.setWindowTitle(title)
    win.resize(*size)
    win.set_blur(blur)
    if show:
        win.show()
    return win


def run_app() -> int:
    """Запускает цикл событий Qt и ждёт закрытия окна. Возвращает код выхода.
    Если используешь qasync, эту функцию не вызывай — цикл запускает qasync."""
    app = QApplication.instance()
    return app.exec() if app is not None else 1


def main():
    w = create_window(show=False)
    w.add_tab("Добро пожаловать")
    w.add_tab("shift://example")
    w.set_current_tab(0)
    w.set_nav_enabled(True, False)

    def fake_load(url: str):
        w.set_loading(True)
        QTimer.singleShot(700, lambda: w.set_progress(0.6))
        QTimer.singleShot(1300, lambda: w.set_progress(0.9))
        QTimer.singleShot(1700, lambda: w.set_loading(False))
        w.set_tab_title(w.tabs.current_index(), url)
        w.set_url(url)

    w.navigateRequested.connect(fake_load)
    w.reloadRequested.connect(lambda: fake_load(w.address.edit.text() or "shift://home"))
    w.show()
    sys.exit(run_app())


if __name__ == "__main__":
    main()