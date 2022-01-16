import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit
)
from imageviewer import ImageViewer

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Camera Calibration OpenCV")
        self.initUI()
        self.prepare_data()
    
    def initUI(self):
        button = [None] * 2
        self.word_textbox = QLineEdit("OPENCV")
        button[0] = QPushButton("1. Show Words on Board", self)
        button[0].clicked.connect(self.show_on_board)
        button[1] = QPushButton("2. Show Words Vertically", self)
        button[1].clicked.connect(self.show_vertically)

        vbox = QVBoxLayout()
        vbox.addWidget(self.word_textbox)
        vbox.addWidget(button[0])
        vbox.addWidget(button[1])
        vbox.addStretch(1)
        self.setLayout(vbox)

    def prepare_data(self):
        """
        Take reference from https://opencv24-python-tutorials.readthedocs.io/en/latest/
        py_tutorials/py_calib3d/py_calibration/py_calibration.html
        """
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)
        
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(7,10,0)
        x, y = 11, 8
        objp = np.zeros((y * x, 3), np.float32)
        objp[:,:2] = np.mgrid[0:x, 0:y].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        objpoints = []          # 3d point in real world space
        self.imgpoints = []    # 2d points in image plane.

        self.orig_imgs = []
        paths = [f"chessboards/{i}.bmp" for i in range(1, 6)]
        for path in paths:
            img = cv2.imread(path)
            self.orig_imgs.append(img)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, (x, y), None)
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            objpoints.append(objp)
            self.imgpoints.append(corners)

        ret, self.mtx, self.dist, self.rvecs, self.tvecs = \
        cv2.calibrateCamera(objpoints, self.imgpoints, gray.shape[::-1], None, None)

    def draw_word(self, fs, img_id, text):
        origpts = [(7, 5), (4, 5), (1, 5), (7, 2), (4, 2), (1, 2)]
        img = self.orig_imgs[img_id].copy()
        for i in range(len(text)):
            ch = fs.getNode(text[i]).mat()
            for line in ch:
                x_start = origpts[i][0] + line[0][0]
                y_start = origpts[i][1] + line[0][1]
                x_end = origpts[i][0] + line[1][0]
                y_end = origpts[i][1] + line[1][1]
                start = [x_start, y_start, line[0][2]]
                end = [x_end, y_end, line[1][2]]
                pts3d = np.float32([start, end]).reshape(-1, 3)
                pts2d, jac = cv2.projectPoints(pts3d, self.rvecs[img_id], self.tvecs[img_id], self.mtx, self.dist)
                start = tuple(pts2d[0].ravel())
                end = tuple(pts2d[1].ravel())
                img = cv2.line(img, start, end, (0, 0, 255), 15)
        return img

    def show_on_board(self):
        fs = cv2.FileStorage(f"words_lib/alphabet_lib_onboard.txt", cv2.FILE_STORAGE_READ)
        word_imgs = []
        for i in range(5):
            img = self.draw_word(fs, i, self.word_textbox.text())
            word_imgs.append(img)

        self.imgviewer = ImageViewer(word_imgs, 1000)
        self.imgviewer.show()

    def show_vertically(self):
        fs = cv2.FileStorage(f"words_lib/alphabet_lib_vertical.txt", cv2.FILE_STORAGE_READ)
        word_imgs = []
        for i in range(5):
            img = self.draw_word(fs, i, self.word_textbox.text())
            word_imgs.append(img)

        self.imgviewer = ImageViewer(word_imgs, 1000)
        self.imgviewer.show()

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()