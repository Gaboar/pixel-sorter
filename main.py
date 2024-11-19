import sys, os
from threading import Timer
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QFileDialog
from PyQt6.QtWidgets import QPushButton, QLineEdit, QLabel, QSlider, QComboBox
import cv2 as cv
import numpy as np

#
# GUI
#

g_iWidth = 854
g_iHeight = 480

app = QApplication(sys.argv)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pixel sort')
        #self.setFixedSize(QSize(400, 300))

        # MAIN layout
        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # textbox
        self.textbox = QLineEdit()
        layout.addWidget(self.textbox, 1, 1, 1, 2)

        # button1
        button1 = QPushButton('Select file')
        button1.setFixedHeight(30)
        button1.clicked.connect(self.getFileName)
        layout.addWidget(button1, 1, 3, 1, 1)

        # label1
        label1 = QLabel('Min:')
        label1.setMaximumHeight(20)
        layout.addWidget(label1, 2, 1, 1, 1)

        # slider1
        self.slider1 = QSlider()
        self.slider1.setOrientation(Qt.Orientation.Horizontal)
        self.slider1.setRange(0, 255)
        self.slider1.valueChanged.connect(self.min_val_change)
        layout.addWidget(self.slider1, 2, 2, 1, 1)

        # label2
        self.label2 = QLabel('0')
        self.label2.setMaximumHeight(20)
        layout.addWidget(self.label2, 2, 3, 1, 1)

        # label3
        label3 = QLabel('Max:')
        label3.setMaximumHeight(20)
        layout.addWidget(label3, 3, 1, 1, 1)

        # slider2
        self.slider2 = QSlider()
        self.slider2.setOrientation(Qt.Orientation.Horizontal)
        self.slider2.setRange(0, 255)
        self.slider2.setValue(self.slider2.maximum())
        self.slider2.valueChanged.connect(self.max_val_change)
        layout.addWidget(self.slider2, 3, 2, 1, 1)

        # label4
        self.label4 = QLabel('255')
        self.label4.setMaximumHeight(20)
        layout.addWidget(self.label4, 3, 3, 1, 1)

        # dropdown
        self.dropdown = QComboBox()
        self.dropdown.addItems(['Right', 'Up', 'Left', 'Down'])
        layout.addWidget(self.dropdown, 4, 1, 1, 3)

        # button2
        button2 = QPushButton('Run')
        button2.setFixedHeight(30)
        button2.clicked.connect(self.display_result)
        layout.addWidget(button2, 5, 1, 1, 3)

        # button3
        button3 = QPushButton('Save')
        button3.setFixedHeight(30)
        button3.clicked.connect(self.save_result)
        layout.addWidget(button3, 6, 1, 1, 3)

        # message
        self.message = QLabel()
        self.message.setMaximumHeight(20)
        layout.addWidget(self.message, 7, 1, 1, 3)

        # image
        self.image = QLabel()
        self.image.setFixedWidth(g_iWidth)
        self.image.setFixedHeight(g_iHeight)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image, 8, 1, 1, 3)


    def getFileName(self):
        file_filter = 'Image (*.png *.jpg)'
        response = QFileDialog.getOpenFileName(
            parent= self,
            caption= 'Select file',
            directory= os.getcwd(),
            filter= file_filter,
        )
        self.textbox.setText(response[0])
        if (os.path.exists(response[0])):
            try:
                map = QPixmap(response[0])
                map = map.scaled(g_iWidth, g_iHeight, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image.setPixmap(map)
                return
            except:
                pass
        self.display_text(self.message, 'Not a valid file')
    
    def min_val_change(self, val:int):
        self.label2.setText(f'{val}')
        if val > self.slider2.value():
            self.slider2.setValue(val)

    def max_val_change(self, val:int):
        self.label4.setText(f'{val}')
        if val < self.slider1.value():
            self.slider1.setValue(val)

    def display_result(self):
        file = self.textbox.text()
        if (not os.path.exists(file)):
            self.display_text(self.message, 'Not a valid file')
            return
        img = cv.imread(file, cv.IMREAD_COLOR)
        img = process_imge(img, self.slider1.value(), self.slider2.value(), self.dropdown.currentIndex())
        image = QImage(img.data, img.shape[1], img.shape[0], QImage.Format.Format_RGB888).rgbSwapped()
        map = QPixmap.fromImage(image)
        map = map.scaled(g_iWidth, g_iHeight, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image.setPixmap(map)

    def save_result(self):
        file = self.textbox.text()
        if (not os.path.exists(file)):
            self.display_text(self.message, 'Not a valid file')
            return
        img = cv.imread(file, cv.IMREAD_COLOR)
        img = process_imge(img, self.slider1.value(), self.slider2.value(), self.dropdown.currentIndex())
        fname, ext = file.split('.')
        cv.imwrite(f'{fname}_sorted.{ext}', img)
        self.display_text(self.message, 'Saved')

    def display_text(self, label:QLabel, s:str):
        label.setText(s)
        t = Timer(5, self.remove_text, [label])
        t.start()

    def remove_text(self, label:QLabel):
        label.setText('')

#
# PROCESSING
#

# detect
def process_imge(frame:cv.typing.MatLike, min:int, max:int, dir) -> cv.typing.MatLike:
    for i in range(dir):
        frame = cv.rotate(frame, cv.ROTATE_90_CLOCKWISE)
    o = frame.copy()
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    mask = np.ndarray(gray.shape, gray.dtype)
    mask.fill(0)
    mask[(gray >= min) & (gray <= max)] = 255
    frame[mask == 0] = [0, 0, 0]
    for row in frame:
        index = 0
        buffer = np.array([0, 0, 0])
        reading = False
        start = 0
        for pixel in row:
            if 0 + pixel[0] + pixel[1] + pixel[2] != 0:
                if not reading:
                    reading = True
                    buffer = pixel
                    start = index
                else:
                    buffer = np.vstack((buffer, pixel))
            elif reading and buffer.size > 3:
                reading = False
                gray_buffer = cv.cvtColor(buffer.reshape(1, buffer.size//3, 3), cv.COLOR_BGR2GRAY)
                sort = np.argsort(gray_buffer)
                buffer = buffer[sort]
                buffer = buffer.reshape(buffer.shape[1], 3)
                for i in range(len(buffer)):
                    row[start+i] = buffer[i]
            index += 1
        if buffer.size > 3:
            gray_buffer = cv.cvtColor(buffer.reshape(1, buffer.size//3, 3), cv.COLOR_BGR2GRAY)
            sort = np.argsort(gray_buffer)
            buffer = buffer[sort]
            buffer = buffer.reshape(buffer.shape[1], 3)
            for i in range(len(buffer)):
                row[start+i] = buffer[i]
    frame[mask == 0] = o[mask == 0]
    for i in range(dir):
        frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)
    return frame


window = MainWindow()

window.show()
app.exec()