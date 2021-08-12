from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

from PyQt5 import QtCore, QtGui, QtWidgets
import sys

import cv2 as cv
import numpy as np
from DB import Database
import os
from featureExtraction import FeatureExtraction

MainUI, _ = loadUiType('design.ui')

DB = Database()
featureExtraction = FeatureExtraction()


class Main(QMainWindow, MainUI):
    def __init__(self, parent=None):
        self.image = []
        # self.video
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.load_query_image)
        self.pushButton_6.clicked.connect(self.load_query_video)
        self.comboBox.addItem('Mean Color Algorithm')
        self.comboBox.addItem('Histogram Algorithm')
        self.comboBox.addItem('Color Layout Algorithm')
        self.pushButton_2.clicked.connect(self.initDB)
        self.pushButton_7.clicked.connect(self.init_video_DB)
        self.pushButton_3.clicked.connect(self.showResults)
        self.pushButton_8.clicked.connect(self.show_video_result)
        self.tabWidget.tabBar().setVisible(False)
        self.tabWidget.setCurrentIndex(0)
        self.pushButton_4.clicked.connect(self.handle_CBIR)
        self.pushButton_5.clicked.connect(self.handle_CBVR)

    def handle_CBIR(self):
        self.tabWidget.setCurrentIndex(0)

    def handle_CBVR(self):
        self.tabWidget.setCurrentIndex(1)

    def compareHist(self, HQ, HM):  # HM is histogram of the Model Image
        diff = cv.compareHist(HQ, HM, cv.HISTCMP_INTERSECT)
        sum = 0
        for i in HM:
            sum = sum + i
        return diff / sum

    def showResults(self):
        selector = self.comboBox.currentText()
        meanColor = featureExtraction.get_mean(self.image)
        matchedPaths = []
        if selector == 'Mean Color Algorithm':
            results = DB.mean_color_find2()
            for result in results:
                sim = self.calculate_distance(result['features'], meanColor)
                if sim > 90:
                    matchedPaths.append(result['path'])
            for path in matchedPaths:
                match = cv.imread('img/' + path)
                cv.imshow('res', match)
                cv.waitKey(0)
            cv.waitKey(0)
        elif selector == 'Histogram Algorithm':
            queryHist = featureExtraction.get_histogram(self.image)
            results = DB.histogram_find()
            matchedPaths = []
            for result in results:
                modelHist = np.float32(result['hist'])
                compare = self.compareHist(queryHist, modelHist)
                if compare > 0.3:
                    matchedPaths.append(result['path'])
                    print(result['path'])
            print('matched')
            print(matchedPaths)
            for path in matchedPaths:
                match = cv.imread('img/' + path)
                cv.imshow('res', match)
                cv.waitKey(0)
            cv.waitKey(0)
        elif selector == 'Color Layout Algorithm':
            matchedPaths = []
            queryHist = featureExtraction.get_color_layout(self.image)  # List of 4 Lists
            results = DB.colorLayout_find()
            print(results[0]["colorLayout"][0])

            for result in results:
                sum = 0
                for i in range(len(queryHist)):
                    modelHist = np.float32(result['colorLayout'][i])
                    sum = sum + self.compareHist(queryHist[i], modelHist)

                avg = sum / 4
                print(avg)
                if avg > 0.3:
                    matchedPaths.append(result['path'])
                print(len(matchedPaths))
            for path in matchedPaths:
                match = cv.imread('img/' + path)
                cv.imshow('res', match)
                cv.waitKey(0)
            cv.waitKey(0)
    def show_video_result(self):
        meanColor = []
        keyFrame = []
        keyFrames = []
        matchPaths = []
        while self.video.isOpened():
            ret, frame = self.video.read()
            if ret == False:
                break
            if len(keyFrame) == 0:
                keyFrame = frame
                keyFrames.append(keyFrame)
                meanColor.append(featureExtraction.get_mean(keyFrame))
            else:
                frameHist = featureExtraction.get_histogram(frame)
                keyFrameHist = featureExtraction.get_histogram(keyFrame)
                compare = self.compareHist(frameHist, keyFrameHist)
                # print(compare)
                if compare < 0.7:
                    keyFrame = frame
                    keyFrames.append(keyFrame)
                    meanColor.append(featureExtraction.get_mean(keyFrame))
                    # print('new')
            cv.imshow('frame', frame)
        print(meanColor)
        results = DB.mean_color_find_video()
        for result in results: #Loop of database videos
            match = False
            count = 0
            for keyFrameMean in meanColor: #loop of meanColor query video
                for modelMeanColor in result['features']:
                    match = False
                    sum = self.calculate_distance(modelMeanColor, keyFrameMean)
                    if sum > 90:
                        print('get')
                        count = count + 1
                        match = True
                        break
            print(len(keyFrames))
            compare = count / len(keyFrames)
            if compare > 0.9:
                matchPaths.append(result['path'])
        for path in matchPaths:
            print(path)
            # cv.waitKey(0)

    def load_query_image(self):
        img = QFileDialog.getOpenFileName(self, 'Open File')
        self.label.setPixmap(QtGui.QPixmap(img[0]))
        self.image = cv.imread(img[0])

    def load_query_video(self):
        video = QFileDialog.getOpenFileName(self, 'Open File')
        self.label.setPixmap(QtGui.QPixmap(video[0]))
        self.video = cv.VideoCapture(video[0])
        print(self.video)

    def initDB(self):
        path = "C:/Users/Mohamed Ramadan/PycharmProjects/multimedia/Github/img"  # Add images dataset full path
        DB.delete_all()
        path, dirs, images = next(os.walk(path))
        for imgPath in images:
            record = {
                "path": imgPath,
                "features": [],
            }
            img = cv.imread('img/' + imgPath)  # Read the image
            # 1- Mean Color Algorithm
            meanColor = featureExtraction.get_mean(img)
            record["features"].extend(meanColor)
            # 2- calculate the histogram
            histogram = featureExtraction.get_histogram(img)
            record["hist"] = histogram.tolist()
            # 3- Color layout Algorithm using histogram similarity
            colorLayout = featureExtraction.get_color_layout(img)
            colorLayoutList = []
            for quarter in colorLayout:
                colorLayoutList.append(quarter.tolist())
            record["colorLayout"] = colorLayoutList
            DB.insert(record)

    def init_video_DB(self):
        DB.destroy_videos_collection()
        path = "C:/Users/Mohamed Ramadan/PycharmProjects/multimedia/Github/vedios"  # Add videos dataset full path
        path, dirs, vedios = next(os.walk(path))
        for vedioPath in vedios:
            record = {
                "path": vedioPath,
            }
            meanColor = []
            cap = cv.VideoCapture('vedios/' + vedioPath)
            keyFrame = []
            keyFrames = []
            while cap.isOpened():
                ret, frame = cap.read()
                if ret == False:
                    break
                if len(keyFrame) == 0:
                    keyFrame = frame
                    keyFrames.append(keyFrame)
                    meanColor.append(featureExtraction.get_mean(keyFrame))
                else:
                    frameHist = featureExtraction.get_histogram(frame)
                    keyFrameHist = featureExtraction.get_histogram(keyFrame)
                    compare = self.compareHist(frameHist, keyFrameHist)
                    # print(compare)
                    if compare < 0.7:
                        keyFrame = frame
                        keyFrames.append(keyFrame)
                        meanColor.append(featureExtraction.get_mean(keyFrame))
                        # print('new')
                cv.imshow('frame', frame)
                print(len(keyFrames))
                print(meanColor)
                # cv.waitKey(0)
            record['features'] = meanColor
            DB.insert_video(record)
            # cv.waitKey(0)

    def calculate_distance(self, img1_mean, img2_mean):
        redMean = (img1_mean[0] + img2_mean[0])/2
        r = float(img1_mean[0]) - float(img2_mean[0])
        g = float(img1_mean[1]) - float(img2_mean[1])
        b = float(img1_mean[2]) - float(img2_mean[2])
        r_weight = 2 + redMean/256
        g_weight = 4.0
        b_weight = 2 + (255 - redMean)/256
        colorDistance = np.sqrt(r_weight*r*r + g_weight*g*g + b_weight*b*b)
        maxColorDis = 764.8339663572415
        similarity = round(((maxColorDis-colorDistance)/maxColorDis)*100)
        return similarity


def main():
    app = QApplication(sys.argv)
    window = Main()
    window.setWindowTitle('CBRS')
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
