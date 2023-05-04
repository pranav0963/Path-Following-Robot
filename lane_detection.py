'''
# Author List:      RIG-NITC
# Theme:            Self Driving Car
# Filename:         lane_detection.py
# Functions:        thresholding, drawPoints, getHistogram
# Global variables: None
'''

import cv2
import numpy as np


def thresholding(img):
    '''
    Purpose:
    ---
    Thresholding the image to get the black track
    
    Input Arguments:
    ---
    `img` :  [ array ]
        The image to be thresholded
    Returns:
    `mask` : [ array ]
        The thresholded mask image
    ---
    Example call:
    ---
    mask = thresholding(img)
    '''

    # print("thresholding")
    imgHsv = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV)
    lowerWhite = np.array([0, 0, 0])
    upperWhite = np.array([179, 87, 255])
    mask = cv2.inRange(img, lowerWhite, upperWhite)
    
    return mask

def drawPoints( img, points):
    '''
    Purpose:
    ---
    mark the points on the image as circles
    ---
    Input Arguments:
    `img` : [ array ]
        The image to be marked
    `points` : [ array ]
        The points to be marked
    Returns:
    ---
    `img` : [ array ]
        The image with the points marked
    Example call:
    ---
    img = drawPoints(img, points)
    '''
    for x in range(4):
        cv2.circle(img, (int(points[x][0]), int(points[x][1])), 15, (0, 0, 255), cv2.FILLED)
    return img


def getHistogram(img, minPer=0.5, display=False, region=1):
    '''
    Purpose:
    ---
    Get the histogram of the image
    
    Input Arguments:
    ---
    `img` : [ array ]
        The image to get the histogram of
    `minPer` : [ float ]
        The minimum percentage of the white region to be considered to be the white track
        eg : 255 is considered as perfect track and 0 is not considered as track
            if minPer = 0.8 then 255*0.8 = 204 
            all the regions with value less than 204 will not be considered as track
    `display` : [ bool ]
        Whether or not to visualize the histogram of the image
    `region` : [ int ]
        The region of the image to be considered for the histogram calculation
    Returns:
    `averageCurveValue` : [ integer ]
        The average value of the track center
    `histogram` : [ array ]
        The histogram of the image
    ---
    Example call:
    ---
    imageTrackCenter, histogram = getHistogram(img , minPer=0.5, display=True, region=1)
    laneCenter = getHistogram(img , minPer=0.8, display=False, region=4)
    '''
    
    if region == 1:
        # find the coloumn sum of entire pixels in the image
        histValues = np.sum(img, axis=0)
    else:
        # region divides the image into desired number of horizontal strips
        # find the coloumn sum of pixels of the defined region
        # histValues = np.sum(img[img.shape[0] // region:, :], axis=0)
        histValues = histValues = np.sum(img[img.shape[0] - img.shape[0] // region:, :], axis=0)
    
    #  find the maximum and minimum values of pixels in the image
    maxValue = np.max(histValues) # it will be white pixels (eg 255) depends on lighting 
    minValue = minPer * maxValue # it will be black pixels (eg 0)

    # find the indices of the pixels with value greater than minValue
    indexArray = np.where(histValues >= minValue)
    averageCurveValue = int(np.average(indexArray))
    
    if display:
        # create a black image of the same size as the original image
        imgHist = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
        for x, intensity in enumerate(histValues):
            # draw a line of pixels with the intensity of the pixel
            #cv2.line(imgHist, (x, img.shape[0]), (x, np.int(img.shape[0] - intensity // 255 // region)), (255, 0, 255),1)
            cv2.line(imgHist, (x, img.shape[0]), (x, np.int(img.shape[0] - intensity // 255 )), (255, 0, 255),1)
            #  draw the average curve value
            cv2.circle(imgHist, (averageCurveValue, img.shape[0]), 20, (0, 255, 255), cv2.FILLED)
        return averageCurveValue, imgHist

    return averageCurveValue

