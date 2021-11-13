#!/usr/bin/env python
import argparse
import timeit


import cv2
import numpy as np
import json


# /home/vinicius/Desktop/PSR_Git/psr_21-22/Parte05/images/atlas2000_e_atlasmv.png


# Create each trackbar function using globals
def onTrackbarminBH(minBH):
    global minimumBH
    minimumBH = minBH


def onTrackbarmaxBH(maxBH):
    global maximumBH
    maximumBH = maxBH


def onTrackbarminGS(minGS):
    global minimumGS
    minimumGS = minGS


def onTrackbarmaxGS(maxGS):
    global maximumGS
    maximumGS = maxGS


def onTrackbarminRV(minRV):
    global minimumRV
    minimumRV = minRV


def onTrackbarmaxRV(maxRV):
    global maximumRV
    maximumRV = maxRV

def main():
    # Globals
    global maximumBH, maximumGS, maximumRV, minimumBH, minimumGS, minimumRV

    minimumBH = 0
    minimumGS = 0
    minimumRV = 0
    maximumBH = 255
    maximumGS = 255
    maximumRV = 255



    window_name = 'window - Ex3d'

    # Load image
    capture = cv2.VideoCapture(0)

    parser = argparse.ArgumentParser()
    parser.add_argument('-hsv', '--hue_saturation_value', help='To modify the image using HSV instead of BGR',
                        action='store_true')
    args = vars(parser.parse_args())

    # show image
    cv2.namedWindow(window_name)

    # Create Trackbars
    cv2.createTrackbar('Min B/H', window_name, 0, 255, onTrackbarminBH)
    cv2.createTrackbar('Max B/H', window_name, 255, 255, onTrackbarmaxBH)
    cv2.createTrackbar('Min G/S', window_name, 0, 255, onTrackbarminGS)
    cv2.createTrackbar('Max G/S', window_name, 255, 255, onTrackbarmaxGS)
    cv2.createTrackbar('Min R/V', window_name, 0, 255, onTrackbarminRV)
    cv2.createTrackbar('Max R/V', window_name, 255, 255, onTrackbarmaxRV)

    while True:
        _, image = capture.read()
        image_original = image.copy()

        if args['hue_saturation_value']:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            cv2.imshow('HSV', image)


        ranges = {'limits': {'B/H': {'max': maximumBH, 'min': minimumBH},
                             'G/S': {'max': maximumGS, 'min': minimumGS},
                             'R/V': {'max': maximumRV, 'min': minimumRV}}}

        # Process image
        mins = np.array([ranges['limits']['B/H']['min'], ranges['limits']['G/S']['min'], ranges['limits']['R/V'][
            'min']])  # Converts the dictionary representation in np.array, which is the representation required by the inRange function
        maxs = np.array([ranges['limits']['B/H']['max'], ranges['limits']['G/S']['max'], ranges['limits']['R/V']['max']])
        mask = cv2.inRange(image, mins, maxs)  # Mask to detect the green box

        # update image
        cv2.namedWindow(window_name)
        cv2.imshow(window_name, mask)
        key = cv2.waitKey(1)


        cv2.namedWindow('original')
        cv2.imshow('original',image_original)

        # Press q to quit the program and saves the directory
        if key == ord('q'):
            file_name = 'limits.json'
            with open(file_name, 'w') as file_handle:
                print('Writing dictionary ranges to file ' + file_name)
                json.dump(ranges, file_handle)
                break


if __name__ == "__main__":
    main()
