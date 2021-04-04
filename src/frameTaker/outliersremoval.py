import math
import cv2


def remove_outliers_by_depth(depth_image, depth_threshold):
    center_row, center_col = get_image_center(depth_image)
    center_depth = depth_image[center_row][center_col]
    for row in range(depth_image.shape[0]):
        for col in range(depth_image.shape[1]):
            if compare_depths_delta(depth_image[row][col], center_depth) > depth_threshold:
                depth_image[row][col] = 10000

    show_results(depth_image)


def remove_outliers_by_depth_and_return_image(depth_image, depth_threshold):
    center_col, center_row = get_image_center(depth_image)
    center_depth = depth_image[center_col][center_row]
    for col in range(depth_image.shape[0]):
        for row in range(depth_image.shape[1]):
            if compare_depths_delta(depth_image[col][row], center_depth) > depth_threshold:
                depth_image[col][row] = 10000

    return depth_image


def get_image_center(depth_image):
    return int(depth_image.shape[0] / 2), int(depth_image.shape[1] / 2)


def compare_depths_delta(depth, depth_to_compare):
    return math.fabs(depth - depth_to_compare)


def show_results(depth_image):
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', depth_colormap)
    cv2.waitKey()