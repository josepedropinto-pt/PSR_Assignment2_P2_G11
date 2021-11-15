#!/usr/bin/python3

import argparse
import math
import cv2
import numpy as np
import json
from time import ctime, time
from colorama import Fore, Back, Style
from termcolor import cprint


# Variable initializing values
radius = 10
painting_color = (0, 0, 0)
previous_point = (0, 0)
global mouse_coordinates
mousetougle = False
global whiteboard
previous_mouse_point = (0, 0)
wbinsteadframe = False



def onMouse(cursor, xposition, yposition, flags, param):

    global previous_mouse_point

    if cursor == cv2.EVENT_MOUSEMOVE and mousetougle == True:
        if previous_mouse_point==(0,0):
            previous_mouse_point = (xposition, yposition)
        cv2.line(img=param,
                 pt1=previous_mouse_point,
                 pt2=(xposition, yposition),
                 color=painting_color,
                 thickness=radius)
        previous_mouse_point = (xposition, yposition)

def main():
    # Global variables
    global radius, painting_color, previous_point, mousetougle

    # Argparse arguments for program Initialization
    parser = argparse.ArgumentParser()
    parser.add_argument('-j',
                        '--json JSON',
                        type=str,
                        required=True,
                        help='Full path to json file.')
    parser.add_argument('-usp',
                        '--use_shake_prevention',
                        action='store_true',
                        help='To use shake prevention.')

    args = vars(parser.parse_args())

    # Creating all of the windows
    window_whiteboard = 'Pynting'
    window_segmented = 'Segmented image'
    window_original_frame = 'Original Frame'

    # Open imported json
    lim = open(args['json JSON'])
    ranges = json.load(lim)
    lim.close()

    # Print list of Commands
    print('''
    Here is your Command List
    ------------------------- ''')
    print("- TO QUIT       " + u"\U000026D4" + "    -> PRESS 'q'")
    print("- TO CLEAR      " + u"\U0001F195" + "   -> PRESS 'c'")
    print("- TO SAVE       " + u"\U0001f4be" + "   -> PRESS 'w'")
    print("- RED PAINT   " + Back.RED + "      " + Style.RESET_ALL + " -> PRESS " + Fore.RED + "'r'" + Fore.RESET)
    print("- GREEN PAINT " + Back.GREEN + "      " + Style.RESET_ALL + " -> PRESS " + Fore.GREEN + "'g'" + Fore.RESET)
    print("- BLUE PAINT  " + Back.BLUE + "      " + Style.RESET_ALL + " -> PRESS " + Fore.BLUE + "'b'" + Fore.RESET)
    print("- THICKER BRUSH " + u"\U0001F58C" + "   -> PRESS '" + "+" + "'")
    print("- THINNER BRUSH " + u"\U0001F58C" + "   -> PRESS '-'")

    # Initialize canvas size with one video capture
    capture = cv2.VideoCapture(0)
    _, frame = capture.read()
    width, height, channel = frame.shape
    whiteboard = np.ones((width, height, channel), np.uint8) * 255


    while True:
        # Read each frame of the video capture
        _, frame = capture.read()

        # Frame copies for overlays and new windows
        image_for_segmentation = frame.copy()

        # Convert dict. into np.arrays to define the minimum thresholds
        min_thresh = np.array([ranges['limits']['B/H']['min'],
                               ranges['limits']['G/S']['min'],
                               ranges['limits']['R/V']['min']])

        # Convert dict. into np.arrays to define the maximum thresholds
        max_thresh = np.array([ranges['limits']['B/H']['max'],
                               ranges['limits']['G/S']['max'],
                               ranges['limits']['R/V']['max']])

        # Create mask using the Json extracted Thresholds
        mask_segmented = cv2.inRange(image_for_segmentation,
                                     min_thresh, max_thresh)

        # Find all the contours of white blobs in the mask_segmented
        contours, hierarchy = cv2.findContours(
            mask_segmented, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # If it finds any contours >0, it calculates one with max. area
        if len(contours) != 0:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)

            # Starts painting only if it's bigger than threshold defined
            if area > 400:
                # Extract coordinates of bounding box
                x, y, w, h = cv2.boundingRect(c)

                # Calculate centroid and draw the red cross there
                centroid = (int(x + w / 2), int(y + h / 2))
                cv2.drawMarker(frame, centroid,
                               color=(0, 0, 255),
                               markerType=cv2.MARKER_CROSS,
                               thickness=3)

                # Draw on the image
                if previous_point == (0, 0):
                    previous_point = centroid

                if args['use_shake_prevention'] and mousetougle == False:
                    aux = (previous_point[0] - centroid[0], previous_point[1] - centroid[1])

                    if math.sqrt(aux[0] ** 2 + aux[1] ** 2) > 50:
                        cv2.circle(frame, centroid, radius, painting_color, -1)
                    else:
                        cv2.line(img=whiteboard,
                                 pt1=previous_point,
                                 pt2=centroid,
                                 color=painting_color,
                                 thickness=radius)
                    previous_point = centroid

                elif mousetougle == True and args['use_shake_prevention'] == True:
                    cv2.setMouseCallback(window_whiteboard, onMouse, param=whiteboard)
                else:
                    cv2.line(img=whiteboard,
                             pt1=previous_point,
                             pt2=centroid,
                             color=painting_color,
                             thickness=radius)
                    previous_point = centroid

        # Defining the window and plotting the whiteboard
        cv2.namedWindow(window_whiteboard, cv2.WINDOW_NORMAL)
        cv2.imshow(window_whiteboard, whiteboard)

        # Defining the window and plotting the image_segmented
        cv2.namedWindow(window_segmented, cv2.WINDOW_NORMAL)
        cv2.imshow(window_segmented, mask_segmented)

        # Defining the window and plotting the original frame
        cv2.namedWindow(window_original_frame, cv2.WINDOW_NORMAL)
        cv2.imshow(window_original_frame, frame)

        key = cv2.waitKey(10)

        # Defining all keyboard shortcuts and there functions
        if key == ord('r'):
            painting_color = (0, 0, 255)
            print('Pencil color ' + Fore.RED + 'Red' + Fore.RESET)

        elif key == ord('g'):
            painting_color = (0, 255, 0)
            print('Wow pencil color ' + Fore.GREEN + 'Green' + Fore.RESET
                  + ', what a great choice')

        elif key == ord('b'):
            painting_color = (255, 0, 0)
            print('Pencil color ' + Fore.BLUE + 'Blue' + Fore.RESET)

        elif key == ord('+'):
            radius += 1
            print('Pencil size' + Fore.GREEN +
                  ' increased ' + Fore.RESET + 'to ' + str(radius))

        elif key == ord('-'):
            if radius == 1:
                print("Pencil size minimum reached!")
            else:
                radius -= 1
                print('Pencil size' + Fore.RED +
                      ' decreased ' + Fore.RESET + 'to ' + str(radius))

        elif key == ord('c'):
            whiteboard = np.ones((width, height, channel), np.uint8) * 255
            cprint('Nice job, you just killed a masterpiece...'
                   , color='white', on_color='on_red', attrs=['blink'])

        elif key == ord('w'):
            time_string = ctime(time()).replace(' ', '_')
            file_name = "Drawing_" + time_string + ".png"
            cv2.imwrite(file_name, whiteboard)

        elif args['use_shake_prevention'] and key == ord('m'):
            mousetougle = True
            print('Now you can move your mouse to paint')

        elif args['use_shake_prevention'] and key == ord('o'):
            mousetougle = False
            print('You can no longer use your mouse to paint')


        elif key == ord('s'):
            # color limits to create masks for each color
            maskblue = (255,0,0)
            maskgreen = (0,255,0)
            maskred = (0,0,255)

            # define kernel size to remove noise
            kernel = np.ones((7, 7), np.uint8)

            # create a mask for each color
            blue_mask = cv2.inRange(whiteboard, maskblue, maskblue)
            green_mask = cv2.inRange(whiteboard, maskgreen, maskgreen)
            red_mask = cv2.inRange(whiteboard, maskred, maskred)

            # Remove unnecessary noise from mask
            blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)
            blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
            red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
            red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)

            # Segment only the detected region
            segmented_blue = cv2.bitwise_and(whiteboard, whiteboard, mask=blue_mask)
            segmented_green = cv2.bitwise_and(whiteboard, whiteboard, mask=green_mask)
            segmented_red = cv2.bitwise_and(whiteboard, whiteboard, mask=red_mask)

            # Find contours from the mask
            redcontours, redhierarchy = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            #redcontours, redhierarchy = cv2.findContours(mask_color.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            output = cv2.drawContours(segmented_red, redcontours, -1, (255, 0, 255), 2)

            greencontours, greenhierarchy = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            output = cv2.drawContours(segmented_green, greencontours, -1, (255, 0, 255), 2)

            bluecontours, bluehierarchy = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            output = cv2.drawContours(segmented_blue, bluecontours, -1, (255, 0, 255), 2)

            # Showing the output
            cv2.imshow('Color Segmentation', output)

        elif key == ord('q'):
            break


if __name__ == "__main__":
    main()
