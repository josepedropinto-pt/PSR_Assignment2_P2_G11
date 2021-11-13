#!/usr/bin/python3
import argparse

import cv2
import numpy as np
import json

click = False






def onMouse(cursor, xposition, yposition, flags, param):

    global click
    if cursor == cv2.EVENT_LBUTTONDOWN:
        click = True
     #   param[yposition, xposition] = color
        cv2.circle(param, (xposition, yposition), 10, color, -1)

    elif cursor == cv2.EVENT_MOUSEMOVE and click == True:
        # param[yposition, xposition] = color
         cv2.circle(param, (xposition, yposition), 10, color, -1)

    elif cursor == cv2.EVENT_LBUTTONUP:
        click = False

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json JSON', type=str, required=True, help='Full path to json file.')

    args = vars(parser.parse_args())

    # Open imported json
    lim = open(args['json JSON'])
    ranges = json.load(lim)
    print(ranges)
    lim.close()

    # Initialize canvas size with one video capture
    capture = cv2.VideoCapture(0)
    _, frame = capture.read()
    width, height, channel = frame.shape

    whiteboard = np.ones((width, height, channel),np.uint8)*255

    window_name = 'Pynting'

    global color
    color = (0, 0, 0)  # set black as default


    while True:
        _, frame = capture.read()
        cv2.imshow('frame', frame)

        processed_image = frame.copy()
        mins = np.array([ranges['limits']['B/H']['min'], ranges['limits']['G/S']['min'], ranges['limits']['R/V'][
            'min']])  # Converts the dictionary representation in np.array, which is the representation required by the inRange function
        maxs = np.array([ranges['limits']['B/H']['max'], ranges['limits']['G/S']['max'], ranges['limits']['R/V']['max']])


        mask_limits = cv2.inRange(processed_image, mins, maxs)  # Mask to detect the green box
        cv2.bitwise_and(processed_image, processed_image, mask= mask_limits)
        cv2.imshow('processed_image', mask_limits)


        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(~mask_limits, 4, cv2.CV_32S)
        areas = stats[labels, cv2.CC_STAT_AREA]
        print(areas)

        # max_area = 0
        # for i in labels:
        #     if areas[1](i) > max_area:
        #         max_area =

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, whiteboard)

        key = cv2.waitKey(10)

        if key == ord('r'):
            color = (0, 0, 255)
        elif key == ord('g'):
            color = (0, 255, 0)
        elif key == ord('b'):
            color = (255, 0, 0)
        elif key == ord('q'):
            break

        cv2.setMouseCallback(window_name, onMouse, param=whiteboard)


if __name__ == "__main__":
    main()