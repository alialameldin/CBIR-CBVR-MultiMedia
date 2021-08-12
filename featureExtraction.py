import cv2 as cv
import imutils
import numpy as np
class FeatureExtraction:
    def __init__(self):
        self.bins = (8, 8, 4)

    def get_mean(self, image):
        img2_av_R = np.mean(image[:, :, 2])
        img2_av_G = np.mean(image[:, :, 1])
        img2_av_B = np.mean(image[:, :, 0])
        return [img2_av_R, img2_av_G, img2_av_B]

    def crop_vertical(self, img):
        width = img.shape[1]
        widthCutOff = width // 2
        leftImg = img[:, 0: widthCutOff]
        rightImg = img[:, widthCutOff:]
        return (leftImg, rightImg)

    def crop_horrizonal(self, img):
        height = img.shape[0]
        heightCutOff = height // 2
        upperImg = img[0: heightCutOff, :]
        lowerImg = img[heightCutOff:, :]
        return (upperImg, lowerImg)

    def crop_img(self, img, numOfCuts):
        (leftImg, rightImg) = self.crop_vertical(img)
        (firstQuarter, thirdQuarter) = self.crop_horrizonal(leftImg)
        (secondQuarter, forthQuarter) = self.crop_horrizonal(rightImg)
        return [firstQuarter, secondQuarter, thirdQuarter, forthQuarter]

    def get_color_layout(self, image):
        image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        features_vector = []
        layouts = self.crop_img(image, 0)
        for i in layouts:
            hist = self.histogram(i, None)
            features_vector.append(hist)
        return features_vector

    def get_color_layout2(self, image):
        features_vector = []
        layouts = self.crop_img(image, 0)
        for i in layouts:
            hist = self.get_mean(i)
            features_vector.append(hist)
        return features_vector

    def get_histogram(self, image):
        image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        return self.histogram(image, None)

    def histogram(self, image, mask=None):
        histogram = cv.calcHist([image], [0, 1, 2], mask, self.bins,
                                [0, 180, 0, 256, 0, 256])
        histogram = cv.normalize(histogram, histogram).flatten()
        return histogram

    def color_layout_mean_color(self,img):
        features_vector = []

        (h, w) = img.shape[:2]
        (X, Y) = (int(w * 0.5), int(h * 0.5))

        layouts = [
            (0, X, 0, Y),
            (X, w, 0, Y),
            (X, w, Y, h),
            (0, X, Y, h)

        ]

        for (startX, endX, startY, endY) in layouts:
            cornerMask = np.zeros(img.shape, dtype="uint8")
            cv.rectangle(cornerMask, (startX, startY), (endX, endY), (255,255,255), -1)
            segment = cv.bitwise_and(img, cornerMask)
            features_vector.append(self.calc_average_color(segment))

        return  features_vector



    def calc_average_color(self, img):
        # img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
        rows, cols, _ = img.shape
        color_percentage = []
        color_B = 0
        color_G = 0
        color_R = 0
        color_N = 0  # not r or g or b but gray

        for i in range(rows):
            for j in range(cols):
                k = img[i, j]
                if k[0] > k[1] and k[0] > k[2]:
                    color_B = color_B + 1
                    continue
                if k[1] > k[0] and k[1] > k[2]:
                    color_G = color_G + 1
                    continue
                if k[2] > k[0] and k[2] > k[1]:
                    color_R = color_R + 1
                    continue
        color_N = 1 -(color_R+color_G+color_B)


        pix_total = rows * cols
        color_percentage.append(float(color_B / pix_total))
        color_percentage.append(float(color_G / pix_total))
        color_percentage.append(float(color_R / pix_total))

        return color_percentage