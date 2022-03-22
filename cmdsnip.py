import sys
import argparse
# from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtGui import QMouseEvent, QKeyEvent, QPaintEvent, QCursor, QPainter, QPen, QColor
from pynput.mouse import Controller

from PIL import ImageGrab
from screeninfo import get_monitors

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class SnipWidget(QMainWindow):
    isSnipping = False

    def __init__(self, imagePath="tmp.png", parent=None, ):
        super().__init__()
        # self.parent = parent
        self.imagePath = imagePath
        
        x, y, w, h = self.getMonitorInfo()
        self.setGeometry(x, y, w, h)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))

        self.begin = QPoint()
        self.end = QPoint()
        self.mouse = Controller()

        self.snip()

    def getMonitorInfo(self, ):
        # bboxes = np.array([[m.x, m.y, m.width, m.height] for m in monitors])
        # x, y, _, _ = bboxes.min(0)
        # w, h = bboxes[:, [0, 2]].sum(1).max(), bboxes[:, [1, 3]].sum(1).max()
        # self.setGeometry(x, y, w-x, h-y)
        monitors = get_monitors()
        # Monitor(x=3840, y=0, width=3840, height=2160, width_mm=1420, height_mm=800, name='HDMI-0', is_primary=False)
        # Monitor(x=0, y=0, width=3840, height=2160, width_mm=708, height_mm=399, name='DP-0', is_primary=True)
        # bboxes = [[m.x, m.y, m.width, m.height] for m in monitors]
        xs = [m.x for m in monitors]
        ys = [m.y for m in monitors]
        ws = [m.width for m in monitors]
        ws = [xi+wi for xi, wi in zip(xs, ws)]
        hs = [m.height for m in monitors]
        hs = [yi+hi for yi, hi in zip(ys, hs)]

        x, y, w, h = min(xs), min(ys), max(ws), max(hs)
        return x, y, w, h

    def snip(self):
        self.isSnipping = True
        self.show()

    def paintEvent(self, event: QPaintEvent):
        if self.isSnipping:
            brushColor = (0, 180, 255, 100)
            lw = 2
            opacity = 0.3
        else:
            brushColor = (255, 255, 255, 0)
            lw = 3
            opacity = 0

        self.setWindowOpacity(opacity)
        qp = QPainter(self)
        qp.setPen(QPen(QColor('black'), lw))
        qp.setBrush(QColor(*brushColor))
        qp.drawRect(QRect(self.begin, self.end))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            QApplication.restoreOverrideCursor()
            self.close()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        self.startPos = self.mouse.position

        self.begin = event.position().toPoint()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        self.end = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.isSnipping = False
        QApplication.restoreOverrideCursor()

        startPos = self.startPos
        endPos = self.mouse.position

        x1 = min(startPos[0], endPos[0])
        y1 = min(startPos[1], endPos[1])
        x2 = max(startPos[0], endPos[0])
        y2 = max(startPos[1], endPos[1])

        self.repaint()
        QApplication.processEvents()
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True)
        QApplication.processEvents()

        self.close()
        self.begin = QPoint()
        self.end = QPoint()
        img.save(self.imagePath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GUI arguments')
    parser.add_argument('-p', '--path', type=str, required=True, help='path to save image file')
    arguments = parser.parse_args()
    app = QApplication(sys.argv)
    mainwindow = SnipWidget(imagePath=arguments.path)
    sys.exit(app.exec())