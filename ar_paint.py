#!/usr/bin/python3

import argparse
import math
import cv2
import numpy as np
import json
from time import ctime, time
from numpy.linalg import norm
import readchar
from colorama import Fore, Back, Style
from termcolor import cprint
import copy
# from pynput.keyboard import Key, Controller
# import keyboard


# Variable initializing values
radius = 10
painting_color = (0, 0, 0)
previous_point = (0, 0)
global mouse_coordinates
mouse_toggle = False
global whiteboard
previous_mouse_point = (0, 0)
global drawing_mode
x_previous = 0
y_previous = 0
global frame_painting
alpha = 1


# def onShapes(cursor, xposition, yposition, flags, param):
#     shape = readchar.readkey()
#     if shape == ord('s'):
#         print('Drawing square')
#     elif shape == ord('o'):
#         print('drawing circle')
#
#
#     if cursor == cv2.EVENT_MOUSEMOVE:
#          previous_draw = (x_previous, y_previous)
#          centroid= (xposition, yposition)
#          final_point = (yposition -y_previous, xposition-x_previous)
#          radius_draw = norm(final_point)
#          print(radius_draw)
#
#          cv2.circle(param, (xposition, yposition), 10, painting_color, -1)


def onMouse(cursor, xposition, yposition, flags, param):
    global previous_mouse_point

    # Calls the function when mouse_toggle is set to True and mouse is moving
    if cursor == cv2.EVENT_MOUSEMOVE and mouse_toggle == True:

        # Draws line with the mouse position
        if previous_mouse_point == (0, 0):
            previous_mouse_point = (xposition, yposition)

        aux = (previous_point[0] - xposition, previous_point[1] - yposition)
        if math.sqrt(aux[0] ** 2 + aux[1] ** 2) > 320:
            cv2.circle(param, (xposition, yposition), radius, painting_color, -1)
        else:
            cv2.line(img=param,
                     pt1=previous_mouse_point,
                     pt2=(xposition, yposition),
                     color=painting_color,
                     thickness=radius)
        previous_mouse_point = (xposition, yposition)


def main():
    # Global variables
    global radius, painting_color, previous_point, mouse_toggle, frame_painting, alpha

    # Argparse arguments for program Initialization
    parser = argparse.ArgumentParser()
    parser.add_argument('-j',
                        '--json_JSON',
                        type=str,
                        required=True,
                        help='Full path to json file.')
    parser.add_argument('-usp',
                        '--use_shake_prevention',
                        action='store_true',
                        help='To use shake prevention.')
    parser.add_argument('-ar',
                        '--augmented_reality',
                        action='store_true',
                        help='To draw on displayed frame')

    args = vars(parser.parse_args())

    # Creating all of the windows
    window_whiteboard = 'Pynting'
    window_segmented = 'Segmented image'
    window_original_frame = 'Original Frame'

    # Open imported json
    lim = open(args['json_JSON'])
    ranges = json.load(lim)
    lim.close()

    # Print list of Commands
    print('''
    Here is your Command List
    ------------------------- ''')
    print("- TO QUIT       " + u"\U000026D4" + "   -> PRESS 'q'")
    print("- TO CLEAR      " + u"\U0001F195" + "   -> PRESS 'c'")
    print("- TO SAVE       " + u"\U0001f4be" + "   -> PRESS 'w'")
    print("- RED PAINT    " + Back.RED + "      " + Style.RESET_ALL + " -> PRESS " + Fore.RED + "'r'" + Fore.RESET)
    print("- GREEN PAINT  " + Back.GREEN + "      " + Style.RESET_ALL + " -> PRESS " + Fore.GREEN + "'g'" + Fore.RESET)
    print("- BLUE PAINT   " + Back.BLUE + "      " + Style.RESET_ALL + " -> PRESS " + Fore.BLUE + "'b'" + Fore.RESET)
    print("- PINK PAINT   " + Back.MAGENTA + "      " + Style.RESET_ALL + " -> PRESS " + Fore.MAGENTA + "'p'" + Fore.RESET)
    print("- ORANGE PAINT " + Back.LIGHTRED_EX + "      " + Style.RESET_ALL + " -> PRESS " + Fore.LIGHTRED_EX + "'o'" + Fore.RESET)
    print("- YELLOW PAINT " + Back.LIGHTYELLOW_EX + "      " + Style.RESET_ALL + " -> PRESS " + Fore.LIGHTYELLOW_EX + "'b'" + Fore.RESET)
    print("- ERASE        " + Back.WHITE + "      " + Style.RESET_ALL + " -> PRESS 'e'")
    print("-TRANSPARENCY +" + " \u2b1c " + "   -> PRESS " + Fore.GREEN + "'h'" + Fore.RESET )
    print("-TRANSPARENCY -" + " \U0001f533" + "   -> PRESS " + Fore.RED + "'l'" + Fore.RESET)

    print("- MOUSE MODE    " + u"\U0001F5B1" + "    -> PRESS 'm'")
    print("- SCREEN MODE   " + u"\U0001F4FA" + "   -> PRESS 'o'")
    print("- THICKER BRUSH " + u"\U0001F58C" + "    -> PRESS '" + "+" + "'")
    print("- THINNER BRUSH " + u"\U0001F58C" + "    -> PRESS '-'")

    # Initialize canvas size with one video capture
    capture = cv2.VideoCapture(0)
    _, frame = capture.read()
    width, height, channel = frame.shape

    if args['augmented_reality']:
        whiteboard = np.ones((width, height, channel), np.uint8)
        painting_color = (255, 0, 0)
    else:
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

                # Draw a green rectangle around the drawer object
                cv2.rectangle(image_for_segmentation, (x,y), (x + w + 20, y + h + 20), (0,255,0), -1)
                frame = cv2.addWeighted(image_for_segmentation, 0.2, frame, 0.8, 0)

                # Calculate centroid and draw the red cross there
                centroid = (int(x + w / 2), int(y + h / 2))
                cv2.drawMarker(frame, centroid,
                               color=(0, 0, 255),
                               markerType=cv2.MARKER_CROSS,
                               thickness=3)

                # Draw on the image
                if previous_point == (0, 0):
                    previous_point = centroid

                # User shake prevention working without mouse functionality
                if args['use_shake_prevention'] and mouse_toggle == False and args['augmented_reality'] == False:
                    aux = (previous_point[0] - centroid[0], previous_point[1] - centroid[1])

                    if math.sqrt(aux[0] ** 2 + aux[1] ** 2) > 320:
                        cv2.circle(whiteboard, centroid, radius, painting_color, -1)
                    else:
                        cv2.line(img=whiteboard,
                                 pt1=previous_point,
                                 pt2=centroid,
                                 color=painting_color,
                                 thickness=radius)
                    previous_point = centroid

                # Only draw with mouse moving functionality
                elif mouse_toggle == True and args['use_shake_prevention'] == True and args[
                    'augmented_reality'] == False:
                    cv2.setMouseCallback(window_whiteboard, onMouse, param=whiteboard)

                # Normal mode without mouse functionality and USP
                elif mouse_toggle == False and args['use_shake_prevention'] == False and args['augmented_reality'] == False:
                    cv2.line(img=whiteboard,
                             pt1=previous_point,
                             pt2=centroid,
                             color=painting_color,
                             thickness=radius)
                    previous_point = centroid

                else:
                    cv2.line(img=whiteboard,
                             pt1=previous_point,
                             pt2=centroid,
                             color=painting_color,
                             thickness=radius)
                    previous_point = centroid
        if args['augmented_reality']:
            frame_painting = cv2.bitwise_or(frame, whiteboard)

            frame_painting = cv2.addWeighted(frame_painting, alpha, frame, 1 - alpha, 0)

            # Defining the window and plotting the image_segmented
            cv2.namedWindow(window_segmented, cv2.WINDOW_NORMAL)
            cv2.imshow(window_segmented, mask_segmented)

            # Defining the window and plotting the original frame
            cv2.namedWindow(window_original_frame, cv2.WINDOW_NORMAL)
            cv2.imshow(window_original_frame, frame)

            # Display the new image using frame as whiteboard
            cv2.namedWindow('Frame Painting', cv2.WINDOW_NORMAL)
            cv2.imshow('Frame Painting', frame_painting)

        else:
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
        # keyboard = Controller()

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

        elif key == ord('p'):
            painting_color = (180, 105, 255)
            print('Pencil color ' + Fore.MAGENTA + 'Pink' + Fore.RESET)

        elif key == ord('y'):
            painting_color = (0, 255, 255)
            print('Pencil color ' + Fore.LIGHTYELLOW_EX + 'Yellow' + Fore.RESET)

        elif key == ord('o'):
            painting_color = (0, 165, 255)
            print('Pencil color ' + Fore.LIGHTRED_EX + 'Orange' + Fore.RESET)

        elif key == ord('e'):
            if args['augmented_reality']:
                painting_color = (0, 0, 0)
                print('You Turned the ' + Fore.BLUE + 'Eraser' + Fore.RESET + ' on.')
            else:
                painting_color = (255, 255, 255)
                print('You Turned the ' + Fore.BLUE + 'Eraser' + Fore.RESET + ' on.')

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

        elif key == ord('h'):
            alpha -= 0.05
            print('Transparency ' + Fore.GREEN +
                  ' set to  ' + Fore.RESET + str(100-(round(alpha*100))) + '%')

        elif key == ord('l'):
            alpha += 0.05
            print('Transparency ' + Fore.RED +
                  ' set to ' + Fore.RESET + str(100-(round(alpha * 100))) + '%')

        elif key == ord('c'):
            if args['augmented_reality']:
                whiteboard = np.ones((width, height, channel), np.uint8)
                cprint('Nice job, you just killed a masterpiece...'
                       , color='white', on_color='on_red', attrs=['blink'])

            else:
                whiteboard = np.ones((width, height, channel), np.uint8) * 255
                cprint('Nice job, you just killed a masterpiece...'
                       , color='white', on_color='on_red', attrs=['blink'])

        elif key == ord('w'):
            if args['augmented_reality']:
                time_string = ctime(time()).replace(' ', '_')
                file_name = "Drawing_" + time_string + ".png"
                cv2.imwrite(file_name, frame_painting)
            else:
                time_string = ctime(time()).replace(' ', '_')
                file_name = "Drawing_" + time_string + ".png"
                cv2.imwrite(file_name, whiteboard)

        elif args['use_shake_prevention'] and key == ord('m'):
            mouse_toggle = True
            print('Now you can move your mouse to paint')

        elif args['use_shake_prevention'] and key == ord('n'):
            mouse_toggle = False
            print('You can no longer use your mouse to paint')

        # elif key == ord('d'):
        #     drawing_mode = True
        #     print('draw')
        #     cv2.setMouseCallback(window_whiteboard, onShapes, param=whiteboard)

        elif key == ord('q'):
            break


if __name__ == "__main__":
    main()
