'''
# Author List:      RIG-NITC
# Theme:            Self Driving Car
# Filename:         main.py
# Functions:        generate_pwm
# Global variables: pwmR, pwmL, counter , midPoint, basePoint , Kp ,
#                   ip_cam_url, base, serverAddressPort, UDPClientSocket
                    imageTrackCenter, laneCenter
'''


####################### IMPORT MODULES #######################

import cv2
import numpy as np
import socket
import lane_detection as lane_detection

##############################################################



msgFromClient = "124,120"
bytesToSend = str.encode(msgFromClient)
serverAddressPort = ("192.168.203.18", 4210)  # get from the serial monitor
# bufferSize = 255
move_forward = False

# Create a UDP socket at client side
UDPClientSocket = socket.socket(
    family=socket.AF_INET, type=socket.SOCK_DGRAM)

ip_cam_url = "http://192.168.203.169:8080/video"  # IP Camera URL


averageCurveList = []

pwmR = 255  # constant pwm for right wheel #53
pwmL = 255  # contant pwm for left wheel

Kp = 1.0  # proportional gain #0.80
Kd = 0.25  # 0.2
prev_diff = 0

# Starting a video capture from the ip web cam
capture = cv2.VideoCapture(ip_cam_url)


def generate_pwm(diff):
    '''
    Purpose:
    ---
    Generate pwm for the wheels of the car based on the
    center of the track and the midpoint of the track
    Input Arguments:
    ---
    `imageTrackCenter` :  [ integer ]
            Average center of the track of in the image
    `laneCenter` :  [ integer ]
            Center of the lane considered near the bottom of the image

    Returns:
    ---
    None
    Example call:
    ---
    generate_pwm(300,240)
    '''
    global pwmR, pwmL, prev_diff
    
    if diff > 0:
        # check if pwmR is string
        de = abs(prev_diff - diff)
        pwmR = pwmR  # -0.2*diff
        pwmL = pwmL - Kp * diff + Kd * de
        prev_diff = diff

    elif diff < 0:
        de = abs(diff - prev_diff)
        pwmR = pwmR + Kp * diff + Kd * de
        pwmL = pwmL  # +0.2*diff

    else:
        pwmR = pwmR
        pwmL = pwmL

    if (pwmL < 100):
        pwmL = "0" + str(round(pwmL))
    else:
        pwmL = str(round(pwmL))
    if (pwmR < 100):
        pwmR = "0" + str(round(pwmR))
    else:
        pwmR = str(round(pwmR))

    # print(pwmL, pwmR, Kp * diff)

    bytesToSend = str.encode(pwmL + "," + pwmR)
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    # reset the pwmR and pwmL to 255
    pwmR = 255
    pwmL = 255


def main():
    '''
    Purpose:
    ---
    Main function for the program
    Input Arguments:
    ---
    None
    Returns:
    ---
    None
    Example call:
    ---
    main()
    '''
    global pwmR, pwmL
    # global laneCenter, imageTrackCenter
    global move_forward, sign_detected



    while capture.isOpened():
        ret, img = capture.read()
        # cv2.imwrite("image.png",img)

        if ret:

            imgCopy = img.copy()

            #############   STEP 1  ##################  

            # apply thresholding to segment the track
            thresholded = lane_detection.thresholding(imgCopy)
            # cv2.imshow("original_img", img )
            cv2.imshow("thresholded", thresholded)


            ############# STEP 2  #####################

            # find the points to apply the perspective transform

            h ,w ,c = img.shape
            points = [(50, 100), (640, 100), (0, 430), (640, 430)]  # 150 # 100
            pts1 = np.float32(points)

            # find the width and height of the perspective transform image

            pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])

            # find the perspective transform matrix
            matrix = cv2.getPerspectiveTransform(pts1, pts2)

            # apply warpPerspective to get the perspective transform image
            imgWarp = cv2.warpPerspective(thresholded, matrix, (w, h))
            imgWarpPoints = lane_detection.drawPoints(imgCopy, points)

            cv2.imshow("imgWarp", imgWarp )
            cv2.imshow("imgWarpPoints", imgWarpPoints)


            ############# STEP 3  #####################

            # get the track center and the lane center
            
            laneCenter, imgHist1 = lane_detection.getHistogram(
                imgWarp, display=True, minPer=0.8)
            imageTrackCenter, imgHist2 = lane_detection.getHistogram(
                imgWarp, display=True, minPer=0, region=4)    

            diff = imageTrackCenter - laneCenter
            #print(offset)   

            cv2.imshow("imgHist1", imgHist1)
            cv2.imshow("imgHist2", imgHist2)

            generate_pwm(diff)

            cv2.imshow('Original_image', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            capture.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()