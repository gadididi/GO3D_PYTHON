import math
import pyrealsense2 as rs
import vg

from src.frameTaker.outliersremoval import get_image_center

FOCAL_LEN_CM = 0.188
SENSOR_HEIGHT_CM = 2.6
SENSOR_WIDTH_CM = 6.1
ROWS = 640
COLS = 480


def measure_distance(pixel_1, pixel_2, depth_frame, intrin):
    u_distance = depth_frame[pixel_1[0], pixel_1[1]]
    v_distance = depth_frame[pixel_2[0], pixel_2[1]]

    point1 = rs.rs2_deproject_pixel_to_point(intrin, [pixel_1[0], pixel_1[1]], u_distance)
    point2 = rs.rs2_deproject_pixel_to_point(intrin, [pixel_2[0], pixel_2[1]], v_distance)

    return math.sqrt(math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2) + math.pow(point1[2] - point2[2], 2))


def get_distance(u_vector, v_vector):
    angle_between_vectors = float(vg.angle(u_vector, v_vector))
    distance = math.sqrt(
        pow(u_vector[2], 2) + pow(v_vector[2], 2) - 2 * u_vector[2] * v_vector[2] * math.cos(angle_between_vectors))
    return distance


def check_if_area_has_also_close_pixels(depth_frame, row, col):
    close_pixels_counter = 0
    for rows_around in range(row - 3, row + 3):
        for cols_around in range(col - 3, col + 3):
            if 0 < rows_around < depth_frame.shape[0]:
                if 0 < cols_around < depth_frame.shape[1]:
                    if depth_frame[rows_around, cols_around] < 10000:
                        close_pixels_counter += 1
    return close_pixels_counter >= 6


def find_highest_valid_pixel(depth_frame):
    for row in range(depth_frame.shape[0] - 1):
        for col in range(depth_frame.shape[1] - 1):
            if depth_frame[row][col] < 10000:
                if check_if_area_has_also_close_pixels(depth_frame, row, col):
                    return row, col
    raise Exception("Couldn't find a valid pixel, the image might be corrupted")


def find_lowest_valid_pixel(depth_frame):
    for row in range(depth_frame.shape[0] - 1, 0, -1):
        for col in range(depth_frame.shape[1] - 1):
            if depth_frame[row][col] < 10000:
                if check_if_area_has_also_close_pixels(depth_frame, row, col):
                    return row, col
    raise Exception("Couldn't find a valid pixel, the image might be corrupted")


def find_highest_valid_pixel_in_the_center(depth_frame):
    _, center_col = get_image_center(depth_frame)
    for row in range(depth_frame.shape[0] - 1):
        if depth_frame[row][center_col] < 10000:
            if check_if_area_has_also_close_pixels(depth_frame, row, center_col):
                return row, center_col
    raise Exception("Couldn't find a valid pixel, the image might be corrupted")


def find_lowest_valid_pixel_in_the_center(depth_frame):
    _, center_col = get_image_center(depth_frame)
    for row in range(depth_frame.shape[0] - 1, 0, -1):
        if depth_frame[row][center_col] < 10000:
            if check_if_area_has_also_close_pixels(depth_frame, row, center_col):
                return row, center_col
    raise Exception("Couldn't find a valid pixel, the image might be corrupted")
