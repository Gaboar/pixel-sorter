import sys, os
from threading import Timer
from PyQt6.QtCore import Qt
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
        self.move(450, 50)

        # MAIN layout
        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # label1
        label1 = QLabel('Image:')
        label1.setMaximumHeight(20)
        layout.addWidget(label1, 1, 1, 1, 1)

        # textbox1
        self.textbox1 = QLineEdit()
        layout.addWidget(self.textbox1, 1, 2, 1, 1)

        # button1
        button1 = QPushButton('Select file')
        button1.setFixedHeight(30)
        button1.clicked.connect(lambda: self.get_file_name(self.textbox1))
        layout.addWidget(button1, 1, 3, 1, 1)

        # label2
        label2 = QLabel('Mask min:')
        label2.setMaximumHeight(20)
        layout.addWidget(label2, 2, 1, 1, 1)

        # slider1
        self.slider1 = QSlider()
        self.slider1.setOrientation(Qt.Orientation.Horizontal)
        self.slider1.setRange(0, 255)
        self.slider1.valueChanged.connect(self.min_val_change)
        layout.addWidget(self.slider1, 2, 2, 1, 1)

        # label3
        self.label3 = QLabel('0')
        self.label3.setMaximumHeight(20)
        layout.addWidget(self.label3, 2, 3, 1, 1)

        # label4
        label4 = QLabel('Mask max:')
        label4.setMaximumHeight(20)
        layout.addWidget(label4, 3, 1, 1, 1)

        # slider2
        self.slider2 = QSlider()
        self.slider2.setOrientation(Qt.Orientation.Horizontal)
        self.slider2.setRange(0, 255)
        self.slider2.setValue(self.slider2.maximum())
        self.slider2.valueChanged.connect(self.max_val_change)
        layout.addWidget(self.slider2, 3, 2, 1, 1)

        # label5
        self.label5 = QLabel('255')
        self.label5.setMaximumHeight(20)
        layout.addWidget(self.label5, 3, 3, 1, 1)

        # label6
        label6 = QLabel('Direction:')
        label6.setMaximumHeight(20)
        layout.addWidget(label6, 4, 1, 1, 1)

        # dropdown
        self.dropdown = QComboBox()
        self.dropdown.addItems(['Right', 'Up', 'Left', 'Down'])
        layout.addWidget(self.dropdown, 4, 2, 1, 1)


        # label7
        label7 = QLabel('Custom mask:')
        label7.setMaximumHeight(20)
        layout.addWidget(label7, 5, 1, 1, 1)

        # textbox2
        self.textbox2 = QLineEdit()
        layout.addWidget(self.textbox2, 5, 2, 1, 1)

        # button2
        button2 = QPushButton('Select file')
        button2.setFixedHeight(30)
        button2.clicked.connect(lambda: self.get_file_name(self.textbox2))
        layout.addWidget(button2, 5, 3, 1, 1)


        # button3
        button3 = QPushButton('Run')
        button3.setFixedHeight(30)
        button3.clicked.connect(self.display_result)
        layout.addWidget(button3, 6, 1, 1, 3)

        # button4
        button4 = QPushButton('Save')
        button4.setFixedHeight(30)
        button4.clicked.connect(lambda: self.display_result(True))
        layout.addWidget(button4, 7, 1, 1, 3)

        # message
        self.message = QLabel()
        self.message.setMaximumHeight(20)
        layout.addWidget(self.message, 8, 1, 1, 3)

        # image
        self.image = QLabel()
        self.image.setFixedWidth(g_iWidth)
        self.image.setFixedHeight(g_iHeight)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image, 9, 1, 1, 3)


    def get_file_name(self, tb:QLineEdit):
        file_filter = 'Image (*.png *.jpg)'
        response = QFileDialog.getOpenFileName(
            parent= self,
            caption= 'Select file',
            directory= os.getcwd(),
            filter= file_filter,
        )
        tb.setText(response[0])
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
        self.label3.setText(f'{val}')
        if val > self.slider2.value():
            self.slider2.setValue(val)
        self.update_mask()

    def max_val_change(self, val:int):
        self.label5.setText(f'{val}')
        if val < self.slider1.value():
            self.slider1.setValue(val)
        self.update_mask()

    def update_mask(self):
        file1 = self.textbox1.text()
        file2 = self.textbox2.text()
        if (os.path.exists(file2)):
            gray = cv.imread(file2, cv.IMREAD_GRAYSCALE)
        elif (os.path.exists(file1)):
            gray = cv.imread(file1, cv.IMREAD_GRAYSCALE)
        else:
            self.display_text(self.message, 'Not a valid file')
            return
        mask = np.ndarray(gray.shape, gray.dtype)
        mask.fill(0)
        mask[(gray >= self.slider1.value()) & (gray <= self.slider2.value())] = 255
        image = QImage(mask.data, mask.shape[1], mask.shape[0], QImage.Format.Format_Grayscale8)
        map = QPixmap.fromImage(image)
        map = map.scaled(g_iWidth, g_iHeight, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image.setPixmap(map)

    def display_result(self, save:bool=False):
        file = self.textbox1.text()
        if (not os.path.exists(file)):
            self.display_text(self.message, 'Not a valid file')
            return
        img = cv.imread(file, cv.IMREAD_COLOR)
        mask = None
        file2 = self.textbox2.text()
        if (os.path.exists(file2)):
            mask = cv.imread(file2, cv.IMREAD_GRAYSCALE)
            mask = cv.resize(mask, (img.shape[0], img.shape[1]))
        img = process_imge(img, self.slider1.value(), self.slider2.value(), self.dropdown.currentIndex(), mask)
        image = QImage(img.data, img.shape[1], img.shape[0], QImage.Format.Format_RGB888).rgbSwapped()
        map = QPixmap.fromImage(image)
        map = map.scaled(g_iWidth, g_iHeight, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image.setPixmap(map)
        if save:
            fname, ext = file.split('.')
            cv.imwrite(f'{fname}_sorted.{ext}', img)
            self.display_text(self.message, 'Saved')
            return
        self.display_text(self.message, 'Done')

    def display_text(self, label:QLabel, s:str):
        label.setText(s)
        t = Timer(5, self.remove_text, [label])
        t.start()

    def remove_text(self, label:QLabel):
        label.setText('')

#
# PROCESSING
#

def process_imge(frame:cv.typing.MatLike, min:int, max:int, dir:int, mask:cv.typing.MatLike) -> cv.typing.MatLike:
    for i in range(dir):
        frame = cv.rotate(frame, cv.ROTATE_90_CLOCKWISE)
    if mask is not None:
        gray = mask.copy()
    else:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    mask = np.ndarray(gray.shape, gray.dtype)
    mask.fill(0)
    mask[(gray >= min) & (gray <= max)] = 255
    for row_index in range(len(mask)):
        index = 0
        buffer = np.array([0, 0, 0])
        reading = False
        start = 0
        for pixel_index in range(len(mask[row_index])):
            if mask[row_index][pixel_index] != 0:
                if not reading:
                    reading = True
                    buffer = frame[row_index][pixel_index]
                    start = index
                else:
                    buffer = np.vstack((buffer, frame[row_index][pixel_index]))
            elif reading and buffer.size > 3:
                reading = False
                gray_buffer = cv.cvtColor(buffer.reshape(1, buffer.size//3, 3), cv.COLOR_BGR2GRAY)
                sort = np.argsort(gray_buffer)
                buffer = buffer[sort]
                buffer = buffer.reshape(buffer.shape[1], 3)
                for i in range(len(buffer)):
                    frame[row_index][start+i] = buffer[i]
            else:
                reading = False
            index += 1
        if buffer.size > 3:
            gray_buffer = cv.cvtColor(buffer.reshape(1, buffer.size//3, 3), cv.COLOR_BGR2GRAY)
            sort = np.argsort(gray_buffer)
            buffer = buffer[sort]
            buffer = buffer.reshape(buffer.shape[1], 3)
            for i in range(len(buffer)):
                frame[row_index][start+i] = buffer[i]
    for i in range(dir):
        frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)
    return frame


window = MainWindow()

window.show()
app.exec()
