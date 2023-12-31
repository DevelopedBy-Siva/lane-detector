import cv2
import numpy as np


def find_edges_with_canny(image):
    """
        - Convert lane_image to grayscale
        - Filter the grayscale_image to reduce noise
        - Canny Edge detection

        :param image: Lane image
        :return: Canny edge detected image
    """
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_image = cv2.GaussianBlur(grayscale_image, (5, 5), 0)
    canny_image = cv2.Canny(blur_image, 50, 150)
    return canny_image


def apply_region_of_interest(canny_image):
    """
        Applies a region of interest mask to a Canny edge-detected image.
        :param canny_image: Canny edge-detected image
        :return: Masked Canny image within the specified region of interest
    """
    image_height = canny_image.shape[0]
    region_vertices = np.array([[(200, image_height), (1100, image_height), (550, 250)]])
    region_mask = np.zeros_like(canny_image)
    cv2.fillPoly(region_mask, region_vertices, 255)
    masked_canny_image = cv2.bitwise_and(canny_image, region_mask)
    return masked_canny_image


def draw_hough_lines(image, hough_lines):
    """
        Draws detected Hough lines on a black image.
        :param image: Lane image
        :param hough_lines: Hough lines
        :return: Image with the detected lines drawn on it
    """
    line_image = np.zeros_like(image)
    if hough_lines is not None:
        for x1, y1, x2, y2 in hough_lines:
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return line_image


def calculate_coordinates(image, line_parameters):
    """
        Calculate the coordinates of a line based on its slope and intercept.
        :param image: The image for which the coordinates are being calculated
        :param line_parameters: The slope and intercept of the line
        :return: An array containing the coordinates [x1, y1, x2, y2] of the line
    """
    slope, intercept = line_parameters
    y1 = image.shape[0]
    y2 = int(y1 * (3 / 5))
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    return np.array([x1, y1, x2, y2])


def calculate_average_coordinates(image, lines):
    """
        Calculate the average coordinates of left and right lanes based on detected lines
        :param image: The image for which lines are being averaged
        :param lines: A collection of lines detected in the image
        :return: An array containing the coordinates of both left and right lanes
    """
    left_lane_fits = []
    right_lane_fits = []

    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        intercept = parameters[1]

        if slope < 0:
            left_lane_fits.append((slope, intercept))
        else:
            right_lane_fits.append((slope, intercept))
    try:
        left_lane_average_fit = np.average(left_lane_fits, axis=0)
        right_lane_average_fit = np.average(right_lane_fits, axis=0)

        left_lane_coordinates = calculate_coordinates(image, left_lane_average_fit)
        right_lane_coordinates = calculate_coordinates(image, right_lane_average_fit)
        return np.array([left_lane_coordinates, right_lane_coordinates])
    except Exception as _:
        return []
