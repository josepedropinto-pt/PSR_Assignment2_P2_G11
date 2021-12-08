#!/usr/bin/python3

# ---------------------------------------------------
# List of Required Modules to Import
# ---------------------------------------------------
import argparse
import math
import cv2
import numpy as np
import json
from time import ctime, time
from colorama import Fore, Back, Style
from termcolor import cprint
import color_by_numbers
import mediapipe as mp
from collections import deque

# PSR, University of Aveiro, November 2021.
# Contributors
# - Jose Pedro Pinto
# - Vinicius Campos
# - Pedro Carvalho


# ---------------------------------------------------
# Global variables initialization and default values
# ---------------------------------------------------

global whiteboard
global frame_painting
global canvas
global color_0, color_1, color_2, color_3
global path_to_color_by_numbers
global width_frame, height_frame
global mask_color0, mask_color1, mask_color2, mask_color3
global original
width_canvas = 400
height_canvas = 800

draw_square = False
draw_circle = False
mouse_toggle = False
what_to_draw = None

painting_color = (0, 0, 0)
previous_point = (0, 0)
previous_point_hp = (0, 0)
previous_mouse_point = (0, 0)
global previous_point_shape
centroid_finger = (0, 0)
x_previous = 0
y_previous = 0
radius = 10
alpha = 1


# ------------------------------------------------------------------------------------------------------#

# ---------------------------------------------------
# Menu with shortcuts and commands
# ---------------------------------------------------
def print_menu():
    print('''
    Here is your Command List
    ------------------------- ''')
    print("- TO QUIT       " + u"\U000026D4" + "    -> PRESS 'q'")
    print("- TO CLEAR      " + u"\U0001F195" + "    -> PRESS 'c'")
    print("- TO SAVE       " + u"\U0001f4be" + "    -> PRESS 'w'")
    print("- SHOW MENU     " + u"\U0001f4d6" + "    -> PRESS 'z'")

    print("- RED PAINT    " + Back.RED + "      " + Style.RESET_ALL + " -> PRESS " + Fore.RED + "'r'" + Fore.RESET)
    print("- GREEN PAINT  " + Back.GREEN + "      " + Style.RESET_ALL + " -> PRESS " + Fore.GREEN + "'g'" + Fore.RESET)
    print("- BLUE PAINT   " + Back.BLUE + "      " + Style.RESET_ALL + " -> PRESS " + Fore.BLUE + "'b'" + Fore.RESET)
    print(
        "- PINK PAINT   " + Back.MAGENTA + "      " + Style.RESET_ALL + " -> PRESS " + Fore.MAGENTA + "'p'" + Fore.RESET)
    print(
        "- ORANGE PAINT " + Back.LIGHTRED_EX + "      " + Style.RESET_ALL + " -> PRESS " + Fore.LIGHTRED_EX + "'o'" + Fore.RESET)
    print("- YELLOW PAINT " + Back.LIGHTYELLOW_EX + "      " + Style.RESET_ALL + " -> PRESS "
          + Fore.LIGHTYELLOW_EX + "'y'" + Fore.RESET)
    print("- ERASE        " + Back.WHITE + "      " + Style.RESET_ALL + " -> PRESS 'e'")
    print("- TRANSPARENCY +" + " \u2b1c " + "  -> PRESS " + Fore.GREEN + "'h'" + Fore.RESET)
    print("- TRANSPARENCY -" + " \U0001f533" + "   -> PRESS " + Fore.RED + "'l'" + Fore.RESET)
    print("- MOUSE MODE    " + u"\U0001F5B1" + "     -> PRESS 'm'")
    print("- MOUSE MODE OFF " + u"\U0001F4FA" + "   -> PRESS 'n'")
    print("- THICKER BRUSH " + u"\U0001F58C" + "     -> PRESS '" + "+" + "'")
    print("- THINNER BRUSH " + u"\U0001F58C" + "     -> PRESS '-'")
    print("- Square Shape  " + u"\u25FC " + "    -> PRESS 's'")
    print("- Circle Shape  " + u"\u20DD" + "      -> PRESS 'd'")
    print("- Paint color 0 " + u"\U0001f522" + "    -> PRESS '0'")
    print("- Paint color 1 " + u"\U0001f522" + "    -> PRESS '1'")
    print("- Paint color 2 " + u"\U0001f522" + "    -> PRESS '2'")
    print("- Paint color 3 " + u"\U0001f522" + "    -> PRESS '3'")
    print("- Paint Grade   " + u"\U0001F50D" + "    -> PRESS 'j'")


# ------------------------------------------------------------------------------------------------------#

# ---------------------------------------------------
# Function for color with Numbers
# ---------------------------------------------------
def color_with_numbers(color):
    global color_0, color_1, color_2, color_3, canvas
    global path_to_color_by_numbers, height_frame, width_frame, height_canvas
    global width_canvas, mask_color0, mask_color1, mask_color2, mask_color3, original
    dn = 15

    color_0 = (color[0][2], color[0][1], color[0][0])
    color_1 = (color[1][2], color[1][1], color[1][0])
    color_2 = (color[2][2], color[2][1], color[2][0])
    color_3 = (color[3][2], color[3][1], color[3][0])

    color_0_up = np.array([color[0][2] + dn, color[0][1] + dn, color[0][0] + dn])
    color_0_down = np.array([color[0][2] - dn, color[0][1] - dn, color[0][0] - dn])

    color_1_up = np.array([color[1][2] + dn, color[1][1] + dn, color[1][0] + dn])
    color_1_down = np.array([color[1][2] - dn, color[1][1] - dn, color[1][0] - dn])

    color_2_up = np.array([color[2][2] + dn, color[2][1] + dn, color[2][0] + dn])
    color_2_down = np.array([color[2][2] - dn, color[2][1] - dn, color[2][0] - dn])

    color_3_up = np.array([color[3][2] + dn, color[3][1] + dn, color[3][0] + dn])
    color_3_down = np.array([color[3][2] - dn, color[3][1] - dn, color[3][0] - dn])

    colors = [color_0_up, color_0_down, color_1_up, color_1_down,
              color_2_up, color_2_down, color_3_up, color_3_down]

    for j in range(len(colors)):
        for i in range(3):

            if colors[j][i] < 0:
                colors[j][i] = 0

            elif colors[j][i] > 255:
                colors[j][i] = 255

    # Original image initializing
    original = cv2.imread(path_to_color_by_numbers, 1)

    cv2.namedWindow('Original', cv2.WINDOW_NORMAL)
    cv2.imshow('Original', original)

    (width_canvas, height_canvas, channel) = original.shape
    canvas = np.ones((width_canvas, height_canvas, channel), np.uint8) * 255

    mask_color0 = cv2.inRange(original, color_0_down, color_0_up)
    mask_color1 = cv2.inRange(original, color_1_down, color_1_up)
    mask_color2 = cv2.inRange(original, color_2_down, color_2_up)
    mask_color3 = cv2.inRange(original, color_3_down, color_3_up)

    mask_color0 = cv2.GaussianBlur(mask_color0, (5, 5), 0)
    mask_color1 = cv2.GaussianBlur(mask_color1, (5, 5), 0)
    mask_color2 = cv2.GaussianBlur(mask_color2, (5, 5), 0)
    mask_color3 = cv2.GaussianBlur(mask_color3, (5, 5), 0)

    contours_0, hierarchy = cv2.findContours(
        mask_color0, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(canvas, contours_0, -1, (0, 0, 0), 4)

    contours_1, hierarchy = cv2.findContours(
        mask_color1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(canvas, contours_1, -1, (0, 0, 0), 4)

    contours_2, hierarchy = cv2.findContours(
        mask_color2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(canvas, contours_2, -1, (0, 0, 0), 4)

    contours_3, hierarchy = cv2.findContours(
        mask_color3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(canvas, contours_3, -1, (0, 0, 0), 4)

    for c_0 in contours_0:
        # Background Color
        # draw the contour and center of the shape on the image
        cv2.drawContours(canvas, [c_0], -1, (0, 0, 0), 2)
        cv2.putText(canvas, str(0), (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    for c_1 in contours_1:
        M = cv2.moments(c_1)
        cX_1 = int(M["m10"] / M["m00"])
        cY_1 = int(M["m01"] / M["m00"])

        # draw the contour and center of the shape on the image
        cv2.drawContours(canvas, [c_1], -1, (0, 0, 0), 2)
        cv2.putText(canvas, str(1), (cX_1, cY_1),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    for c_2 in contours_2:
        M = cv2.moments(c_2)
        cX_2 = int(M["m10"] / M["m00"])
        cY_2 = int(M["m01"] / M["m00"])

        # draw the contour and center of the shape on the image
        cv2.drawContours(canvas, [c_2], -1, (0, 0, 0), 2)
        cv2.putText(canvas, str(2), (cX_2, cY_2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    for c_3 in contours_3:
        M = cv2.moments(c_3)
        cX_3 = int(M["m10"] / M["m00"])
        cY_3 = int(M["m01"] / M["m00"])

        # draw the contour and center of the shape on the image
        cv2.drawContours(canvas, [c_3], -1, (0, 0, 0), 2)
        cv2.putText(canvas, str(3), (cX_3, cY_3),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    pie_chart = cv2.imread('pie_chart.png', 1)

    cv2.namedWindow('color map', cv2.WINDOW_NORMAL)
    cv2.imshow('color map', pie_chart)


# ------------------------------------------------------------------------------------------------------#

# ---------------------------------------------------
# Function for Paint_by_Numbers Grade
# ---------------------------------------------------

def evaluate_paint():
    global mask_color0, mask_color1, mask_color2, mask_color3
    global canvas, original

    mask_0_colored = cv2.bitwise_or(original, original, mask=mask_color0)
    mask_1_colored = cv2.bitwise_or(original, original, mask=mask_color1)
    mask_2_colored = cv2.bitwise_or(original, original, mask=mask_color2)
    mask_3_colored = cv2.bitwise_or(original, original, mask=mask_color3)

    result_0 = cv2.subtract(canvas, mask_0_colored)
    result_1 = cv2.subtract(canvas, mask_1_colored)
    result_2 = cv2.subtract(canvas, mask_2_colored)
    result_3 = cv2.subtract(canvas, mask_3_colored)

    total_0 = np.sum(mask_0_colored != 0)
    total_1 = np.sum(mask_1_colored != 0)
    total_2 = np.sum(mask_2_colored != 0)
    total_3 = np.sum(mask_3_colored != 0)

    weight_0 = total_0/(total_0+total_1+total_2+total_3)
    weight_1 = total_1/(total_0+total_1+total_2+total_3)
    weight_2 = total_2/(total_0+total_1+total_2+total_3)
    weight_3 = total_3/(total_0+total_1+total_2+total_3)

    painted_0 = np.sum(result_0 == 0)
    painted_1 = np.sum(result_1 == 0)
    painted_2 = np.sum(result_2 == 0)
    painted_3 = np.sum(result_3 == 0)

    # New Painted with contours back pixels extracted 89702
    painted_0 = painted_0 - 89702
    painted_1 = painted_1 - 89702
    painted_2 = painted_2 - 89702
    painted_3 = painted_3 - 89702

    ratio_0 = painted_0/total_0
    ratio_1 = painted_1/total_1
    ratio_2 = painted_2/total_2
    ratio_3 = painted_3/total_3

    final_percentage = (ratio_0*weight_0 + ratio_1*weight_1 + ratio_2*weight_2 + ratio_3 * weight_3)*100
    print("Your Grade is: " + Fore.GREEN + str(round(final_percentage, 2)) + Fore.RESET + " %")
    if final_percentage == 100:
        cprint('You are a genius!'
               , color='white', on_color='on_green', attrs=['blink'])
    elif final_percentage == 0:
        cprint('Go home and practice Picasso!'
               , color='white', on_color='on_red', attrs=['blink'])
    elif 2 < final_percentage < 50:
        cprint('Just work a little more, you will get there Da Vinci'
               , color='white', on_color='on_yellow', attrs=['blink'])
    elif 51 < final_percentage < 99:
        cprint('What a masterpiece Miguel Angelo'
               , color='white', on_color='on_blue', attrs=['blink'])
# ------------------------------------------------------------------------------------------------------#

# ---------------------------------------------------
# Function for shape drawing
# ---------------------------------------------------
def onShapes(cursor, xposition, yposition, flags, param):
    # Call of global variables
    global previous_point_shape, cX, cY, circle_radius, what_to_draw

    whiteboard_copy = param.copy()
    if draw_square == True or draw_circle == True:
        if previous_point_shape == (0, 0):
            previous_point_shape = (xposition, yposition)

        (cX, cY) = (xposition, yposition)
        if draw_square:
            cv2.rectangle(whiteboard_copy, previous_point_shape, (cX, cY), painting_color,
                          radius)  # Square move animation
        elif draw_circle:
            aux = (cX - previous_point_shape[0], cY - previous_point_shape[1])
            circle_radius = math.sqrt(aux[0] ** 2 + aux[1] ** 2)
            cv2.circle(whiteboard_copy, previous_point_shape, int(circle_radius), painting_color, radius)
        cv2.imshow('Pynting', whiteboard_copy)

    elif draw_square == False and what_to_draw == ord('s'):
        cv2.rectangle(param, previous_point_shape, (cX, cY), painting_color,
                      radius)  # Fix the square on whiteboard
        what_to_draw = None
        return
    elif draw_circle == False and what_to_draw == ord('d'):
        cv2.circle(param, previous_point_shape, int(circle_radius), painting_color, radius)
        what_to_draw = None
        return

# ------------------------------------------------------------------------------------------------------#

# ---------------------------------------------------
# Function for Functioning Modes
# ---------------------------------------------------

def onModes(usp, ar, pn, mouse, hp):
    if usp == False and ar == False and pn is None and hp == False and mouse == False:
        return 'normal_mode'

    elif usp == True and ar == False and pn is None and hp == False and mouse == False:
        return 'usp_mode'

    elif usp == True and ar == False and pn is None and hp == False and mouse == True:
        return 'usp_w_mouse_mode'

    elif usp == False and ar == True and pn is None and hp == False and mouse == False:
        return 'ar_mode'

    elif usp == False and ar == False and pn is not None and hp == False and mouse == False:
        return 'pn_mode'

    elif usp == False and ar == False and pn is not None and hp == False and mouse == True:
        return 'pn_w_mouse_mode'

    elif usp == False and ar == False and pn is None and hp == True and mouse == False:
        return 'hp_mode'


# ------------------------------------------------------------------------------------------------------#

# ---------------------------------------------------
# Function for Mouse Drawing
# ---------------------------------------------------

def onMouse(cursor, xposition, yposition, flags, param):
    # Call of Global Variables
    global previous_mouse_point

    # Calls the function when mouse_toggle is set to True and mouse is moving
    if cursor == cv2.EVENT_MOUSEMOVE and mouse_toggle == True:

        # Draws line with the mouse position
        if previous_mouse_point == (0, 0):
            previous_mouse_point = (xposition, yposition)

        aux = (previous_point[0] - xposition, previous_point[1] - yposition)
        if math.sqrt(aux[0] ** 2 + aux[1] ** 2) > 200:
            cv2.circle(param, (xposition, yposition), radius, painting_color, -1)
        else:
            cv2.line(img=param,
                     pt1=previous_mouse_point,
                     pt2=(xposition, yposition),
                     color=painting_color,
                     thickness=radius)
        previous_mouse_point = (xposition, yposition)


# ------------------------------------------------------------------------------------------------------#


def main():
    # Defining Global variables
    global radius, painting_color, previous_point, mouse_toggle, frame_painting, previous_point_shape, hands, whiteboard_hand, centroid_finger
    global alpha, path_to_color_by_numbers, canvas, draw_square, draw_circle, what_to_draw
    global color_0, color_1, color_2, color_3, width_canvas, height_canvas, width_frame
    global whiteboard, rpoints, draw, my_hands, rgb_hand, previous_point_hp, height_frame
    count = 0  # Counter to print the menu after x iterations

    # ---------------------------------------------------
    # Definition of Parser Arguments
    # ---------------------------------------------------
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

    parser.add_argument('-m',
                        '--mirror_image',
                        action='store_true',
                        help='Mirror the image captured by camera')

    parser.add_argument('-pn',
                        '--color_by_numbers',
                        type=str,
                        default=None,
                        help='Path to file to paint by numbers')

    parser.add_argument('-hp',
                        '--hand_painting',
                        action='store_true',
                        help='Using finger as pencil')

    args = vars(parser.parse_args())

    # ------------------------------------------------------------------------------------------------------#

    # ---------------------------------------------------
    # Printing of commands list and welcome message
    # ---------------------------------------------------
    print("\nWelcome to our AR_Paint \n\nContributors: "
          "\n- Jose Pedro Pinto"
          "\n- Vinicius Campos"
          "\n- Pedro Carvalho"
          " \n\nPSR, University of Aveiro, ""November 2021.\n")

    print_menu()

    # ------------------------------------------------------------------------------------------------------#

    # Creating all of the windows
    window_whiteboard = 'Pynting'
    window_segmented = 'Segmented image'
    window_original_frame = 'Original Frame'

    # Open imported json
    lim = open(args['json_JSON'])
    ranges = json.load(lim)
    lim.close()

    # Initialize canvas size with one video capture
    capture = cv2.VideoCapture(0)
    _, frame = capture.read()
    width_frame, height_frame, channel = frame.shape

    if args['augmented_reality']:
        whiteboard = np.ones((width_frame, height_frame, channel), np.uint8)
        painting_color = (255, 0, 0)
    elif args['hand_painting']:
        whiteboard_hand = np.ones((width_frame, height_frame, channel), np.uint8) * 255
    else:
        whiteboard = np.ones((width_frame, height_frame, channel), np.uint8) * 255

    # Import color by numbers function
    if args['color_by_numbers'] is not None:
        color = color_by_numbers.main(args['color_by_numbers'], 4)
        path_to_color_by_numbers = args['color_by_numbers']
        color_with_numbers(color)

    if args['hand_painting']:
        my_hands = mp.solutions.hands
        hands = my_hands.Hands()
        draw = mp.solutions.drawing_utils
        rpoints = [deque(maxlen=512)]

    while True:
        # Read each frame of the video capture
        _, frame = capture.read()

        if args['mirror_image']:
            frame = cv2.flip(frame, 1)

        mode = onModes(args['use_shake_prevention'], args['augmented_reality'],
                       args['color_by_numbers'], mouse_toggle, args['hand_painting'])

        # Frame copies for overlays and new windows
        image_for_segmentation = frame.copy()
        image_for_hand_paint = frame.copy()

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

        if mode == 'hp_mode':
            rgb_hand = cv2.cvtColor(image_for_hand_paint, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb_hand)
            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    draw.draw_landmarks(rgb_hand, hand_landmarks, my_hands.HAND_CONNECTIONS)
                    for id, landmark in enumerate(hand_landmarks.landmark):
                        h, w, _ = rgb_hand.shape
                        cx_finger, cy_finger = int(landmark.x * w), int(landmark.y * h)
                        centroid_finger = (cx_finger, cy_finger)
                        if hand_landmarks != 0:
                            if id == 8:
                                rpoints[0].append((cx_finger, cy_finger))
                                cv2.circle(rgb_hand, (cx_finger, cy_finger), radius, (0, 0, 255), -1)

        # If it finds any contours >0, it calculates one with max. area
        if len(contours) != 0:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)

            # Starts painting only if it's bigger than threshold defined
            if area > 500:
                # Extract coordinates of bounding box
                x, y, w, h = cv2.boundingRect(c)

                # Draw a green rectangle around the drawer object
                cv2.rectangle(image_for_segmentation, (x, y), (x + w + 20, y + h + 20), (0, 255, 0), -1)
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
                if mode == 'usp_mode':
                    aux = (previous_point[0] - centroid[0], previous_point[1] - centroid[1])
                    if math.sqrt(aux[0] ** 2 + aux[1] ** 2) > 200:
                        cv2.circle(whiteboard, centroid, radius, painting_color, -1)
                    else:
                        cv2.line(img=whiteboard,
                                 pt1=previous_point,
                                 pt2=centroid,
                                 color=painting_color,
                                 thickness=radius)
                    previous_point = centroid

                # Only draw with mouse moving functionality
                elif mode == 'usp_w_mouse_mode':
                    cv2.setMouseCallback(window_whiteboard, onMouse, param=whiteboard)

                # Normal mode without mouse functionality and USP
                elif mode == 'ar_mode':
                    cv2.line(img=whiteboard,
                             pt1=previous_point,
                             pt2=centroid,
                             color=painting_color,
                             thickness=radius)
                    previous_point = centroid

                elif mode == 'pn_mode':
                    cv2.line(img=canvas,
                             pt1=previous_point,
                             pt2=centroid,
                             color=painting_color,
                             thickness=radius)
                    previous_point = centroid

                elif mode == 'pn_w_mouse_mode':
                    cv2.setMouseCallback('canvas', onMouse, param=canvas)

                elif mode == 'normal_mode':
                    cv2.line(img=whiteboard,
                             pt1=previous_point,
                             pt2=centroid,
                             color=painting_color,
                             thickness=radius)
                    previous_point = centroid

        if mode == 'hp_mode':
            if previous_point_hp == (0, 0):
                previous_point_hp = centroid_finger

            cv2.line(img=whiteboard_hand,
                     pt1=previous_point_hp,
                     pt2=centroid_finger,
                     color=painting_color,
                     thickness=radius)
            previous_point_hp = centroid_finger

        # ------------------------------------------------------------------------------------------------------#
        # ---------------------------------------------------
        # Configuring and Plotting Windows for all Modes
        # ---------------------------------------------------

        if args['augmented_reality']:

            # Configuring Transparency of Augmented Reality mode
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

        elif args['color_by_numbers'] is not None:
            # Defining the window and plotting the image_segmented
            cv2.namedWindow(window_segmented, cv2.WINDOW_NORMAL)
            cv2.imshow(window_segmented, mask_segmented)

            # Defining the window and plotting the original frame
            cv2.namedWindow(window_original_frame, cv2.WINDOW_NORMAL)
            cv2.imshow(window_original_frame, frame)

            # Display the canvas for painting by numbers
            cv2.namedWindow('canvas', cv2.WINDOW_NORMAL)
            cv2.imshow('canvas', canvas)

        elif args['hand_painting']:

            # Convert and display hand with landmarks
            rgb_hand = cv2.cvtColor(rgb_hand, cv2.COLOR_RGB2BGR)
            cv2.namedWindow('window_hand', cv2.WINDOW_NORMAL)
            cv2.imshow('window_hand', rgb_hand)

            # Defining the window and plotting the whiteboard
            cv2.namedWindow('window_whiteboard_hand', cv2.WINDOW_NORMAL)
            cv2.imshow('window_whiteboard_hand', whiteboard_hand)

            # Defining the window and plotting the original frame
            cv2.namedWindow(window_original_frame, cv2.WINDOW_NORMAL)
            cv2.imshow(window_original_frame, frame)

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
        if count == 15:
            print_menu()
            count = 0

        # ------------------------------------------------------------------------------------------------------#
        # ---------------------------------------------------
        # Defining all Keyboard Shortcuts and there Functions
        # ---------------------------------------------------

        if key == ord('r'):
            painting_color = (0, 0, 255)
            print('Pencil color ' + Fore.RED + 'Red' + Fore.RESET)
            count += 1

        elif key == ord('g'):
            painting_color = (0, 255, 0)
            print('Wow pencil color ' + Fore.GREEN + 'Green' + Fore.RESET
                  + ', what a great choice')
            count += 1

        elif key == ord('b'):
            painting_color = (255, 0, 0)
            print('Pencil color ' + Fore.BLUE + 'Blue' + Fore.RESET)
            count += 1

        elif key == ord('p'):
            painting_color = (180, 105, 255)
            print('Pencil color ' + Fore.MAGENTA + 'Pink' + Fore.RESET)
            count += 1

        elif key == ord('y'):
            painting_color = (0, 255, 255)
            print('Pencil color ' + Fore.LIGHTYELLOW_EX + 'Yellow' + Fore.RESET)
            count += 1

        elif key == ord('o'):
            painting_color = (0, 165, 255)
            print('Pencil color ' + Fore.LIGHTRED_EX + 'Orange' + Fore.RESET)
            count += 1

        elif key == ord('e'):
            if args['augmented_reality']:
                painting_color = (0, 0, 0)
                print('You Turned the ' + Fore.BLUE + 'Eraser' + Fore.RESET + ' on.')
            else:
                painting_color = (255, 255, 255)
                print('You Turned the ' + Fore.BLUE + 'Eraser' + Fore.RESET + ' on.')
            count += 1

        elif key == ord('+'):
            radius += 1
            print('Pencil size' + Fore.GREEN +
                  ' increased ' + Fore.RESET + 'to ' + str(radius))
            count += 1

        elif key == ord('-'):
            if radius == 1:
                print("Pencil size minimum reached!")
            else:
                radius -= 1
                print('Pencil size' + Fore.RED +
                      ' decreased ' + Fore.RESET + 'to ' + str(radius))
            count += 1

        elif key == ord('h'):
            alpha -= 0.05
            print('Transparency ' + Fore.GREEN +
                  ' set to  ' + Fore.RESET + str(100 - (round(alpha * 100))) + '%')
            count += 1

        elif key == ord('l'):
            alpha += 0.05
            print('Transparency ' + Fore.RED +
                  ' set to ' + Fore.RESET + str(100 - (round(alpha * 100))) + '%')
            count += 1

        elif key == ord('c'):
            if args['augmented_reality']:
                whiteboard = np.ones((width_frame, height_frame, channel), np.uint8)

            elif args['hand_painting']:
                whiteboard_hand = np.ones((width_frame, height_frame, channel), np.uint8) * 255

            else:
                whiteboard = np.ones((width_frame, height_frame, channel), np.uint8) * 255

            cprint('Nice job, you just killed a masterpiece...',
                   color='white', on_color='on_red', attrs=['blink'])
            count += 1

        elif key == ord('w'):
            if args['augmented_reality']:
                time_string = ctime(time()).replace(' ', '_')
                file_name = "Drawing_" + time_string + ".png"
                cv2.imwrite(file_name, frame_painting)
            else:
                time_string = ctime(time()).replace(' ', '_')
                file_name = "Drawing_" + time_string + ".png"
                cv2.imwrite(file_name, whiteboard)
            count += 1

        elif args['use_shake_prevention'] and key == ord('m') or args['color_by_numbers'] and key == ord('m'):
            mouse_toggle = True
            print('Now you can move your mouse to paint')
            count += 1

        elif args['use_shake_prevention'] and key == ord('n') or args['color_by_numbers'] and key == ord('n'):
            mouse_toggle = False
            print('You can no longer use your mouse to paint')
            count += 1

        elif key == ord('0'):
            painting_color = color_0
            print('Painting with color 0 of Paint by numbers')
            count += 1

        elif key == ord('1'):
            painting_color = color_1
            print('Painting with color 1 of Paint by numbers')
            count += 1

        elif key == ord('2'):
            painting_color = color_2
            print('Painting with color 2 of Paint by numbers')
            count += 1

        elif key == ord('3'):
            painting_color = color_3
            print('Painting with color 3 of Paint by numbers')
            count += 1

        elif key == ord('s'):
            print('Draw Square')
            if not draw_square:
                previous_point_shape = (0, 0)

            draw_square = not draw_square
            what_to_draw = key
            cv2.setMouseCallback(window_whiteboard, onShapes, param=whiteboard)
            count += 1

        elif key == ord('d'):
            print('Draw Circle')
            if not draw_circle:
                previous_point_shape = (0, 0)

            draw_circle = not draw_circle
            what_to_draw = key
            cv2.setMouseCallback(window_whiteboard, onShapes, param=whiteboard)
            count += 1

        elif key == ord('j') and mode == 'pn_mode':
            evaluate_paint()

        elif key == ord('z'):
            print_menu()

        elif key == ord('q'):
            cprint("\nThank you for using AR Paint, hope to you see you again soon\n", color='white',
                   on_color='on_blue')
            print("Masterpiece creators:\n\t- Jose Pedro Pinto \n\t- Pedro Carvalho\n\t- Vinicius Campos\n")
            print("----------------------------------------------------------\n\n")
            break


# ------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    main()
