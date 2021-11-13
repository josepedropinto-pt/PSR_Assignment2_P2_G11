#!/usr/bin/python3
import argparse

import cv2
import numpy as np
import json
from time import ctime, time

radius = 10

def main():
    global radius
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

    whiteboard = np.ones((width, height, channel), np.uint8) * 255

    window_name = 'Pynting'
    global color
    color = (0, 0, 0)
    # set black as default

    while True:

        _, frame = capture.read()

        processed_image = frame.copy()
        mins = np.array([ranges['limits']['B/H']['min'], ranges['limits']['G/S']['min'], ranges['limits']['R/V'][
            'min']])  # Converts the dictionary representation in np.array, which is the representation required by the inRange function
        maxs = np.array(
            [ranges['limits']['B/H']['max'], ranges['limits']['G/S']['max'], ranges['limits']['R/V']['max']])

        mask_limits = cv2.inRange(processed_image, mins, maxs)  # Mask to detect the green box
        # cv2.bitwise_and(processed_image, processed_image, mask= mask_limits)

        contours, hierarchy = cv2.findContours(
            mask_limits, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) != 0:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)

            if area > 150:
                x, y, w, h = cv2.boundingRect(c)
                centroid = (int(x + w / 2), int(y + h / 2))
                cv2.drawMarker(frame, centroid,
                               color=(0, 0, 255), markerType=cv2.MARKER_CROSS, thickness=3)

                cv2.circle(whiteboard, centroid, radius= radius, color=color, thickness=-1)

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, whiteboard)

        cv2.imshow('processed_image', mask_limits)
        cv2.imshow('frame', frame)

        key = cv2.waitKey(10)

        if key == ord('r'):
            color = (0, 0, 255)
        elif key == ord('g'):
            color = (0, 255, 0)
        elif key == ord('b'):
            color = (255, 0, 0)
        elif key == ord('+'):
            radius += 1
        elif key == ord('-'):
            radius -= 1
        elif key == ord('c'):
            whiteboard = np.ones((width, height, channel), np.uint8) * 255
        elif key == ord('w'):
            time_string = ctime(time())
            file_name = "Drawing_" + time_string + ".png"
            cv2.imwrite(file_name, whiteboard)
        elif key == ord('q'):
            break


if __name__ == "__main__":
    main()
