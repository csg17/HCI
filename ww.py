from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import sys, datetime, playsound
import argparse
import imutils
import time
import dlib
import cv2
import csv
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui


# 동영상을 보여주는 용도
class ShowVideo(QtCore.QObject):

  flag = 0
  camera = cv2.VideoCapture(0)
  smallcamera = cv2.VideoCapture('abc.mov')
      
  ret, image = camera.read()
  height, width = image.shape[:2]

# 사용자가 정의해주는 시그널.
  VideoSignal1 = QtCore.pyqtSignal(QtGui.QImage)
  VideoSignal2 = QtCore.pyqtSignal(QtGui.QImage)

  def __init__(self, parent = None):
    super(ShowVideo, self).__init__(parent)
    # self.setGeometry(150, 150, 650, 540)

  def startVideo(self):
    global image

    run_video = True
    while run_video:
      ret, image = self.camera.read()
      color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

      qt_image1 = QtGui.QImage(color_swapped_image.data, self.width, self.height, color_swapped_image.strides[0], QtGui.QImage.Format_RGB888)
      self.VideoSignal1.emit(qt_image1)

      qt_image2 = QtGui.QImage(color_swapped_image.data, self.width, self.height, color_swapped_image.strides[0], QtGui.QImage.Format_RGB888)
      self.VideoSignal2.emit(qt_image2)

      loop = QtCore.QEventLoop()
      QtCore.QTimer.singleShot(25, loop.quit) #25 ms
      loop.exec_()

    # @QtCore.pyqtSlot()
    # def canny(self):
    #     self.flag = 1 - self.flag

class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()

    def initUI(self):
        self.setWindowTitle('Zoom')

    # @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")

        self.image = image
        if image.size() != self.size():
            self.setFixedSize(image.size())
        self.update()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    thread = QtCore.QThread()
    thread.start()

    vid = ShowVideo()
    vid.moveToThread(thread)

    image_viewer1 = ImageViewer()
    image_viewer2 = ImageViewer()

    vid.VideoSignal1.connect(image_viewer1.setImage)
    vid.VideoSignal2.connect(image_viewer2.setImage)

    push_button1 = QtWidgets.QPushButton('Start')
    push_button2 = QtWidgets.QPushButton('Canny')
    # push_button1.clicked.connect(vid.startVideo)
    # push_button2.clicked.connect(vid.canny)

    #수평 박스를 하나 만들기. 
    vertical_layout = QtWidgets.QVBoxLayout()
    horizontal_layout = QtWidgets.QHBoxLayout()

    horizontal_layout.addWidget(image_viewer1)
    horizontal_layout.addWidget(image_viewer2)

    vertical_layout.addLayout(horizontal_layout)
    vertical_layout.addWidget(push_button1)
    vertical_layout.addWidget(push_button2)

    layout_widget = QtWidgets.QWidget()
    layout_widget.setLayout(vertical_layout)

    main_window = QtWidgets.QMainWindow()
    main_window.setCentralWidget(layout_widget)
    main_window.show()

    vid.startVideo()

    sys.exit(app.exec_())