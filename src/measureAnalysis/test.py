import cv2
import numpy as np

from src.frameSaver import saveframe
from src.frameTaker.loadframe import load_frame
from src.frameTaker.outliersremoval import remove_outliers_by_depth
from src.frameTaker.takeframe import FrameTaker
from src.sqlConnector.sqlconnector import SQLConnector


def take_frame():
    frame_taker = FrameTaker()
    frame_taker.start_stream()
    saveframe.save_frames_to_file_system(frame_taker.get_frame_cache(), "test_3")


def load(file_name):
    depth_image, accel_image, gyro_image = load_frame(file_name, 1)
    remove_outliers_by_depth(depth_image, 0.1)


def test_get_4d_image():

    frame_taker = FrameTaker()
    frame_taker.start_stream()

    image = frame_taker.get_last_image()
    depth_image = frame_taker.get_last_depth_image()
    depth_image_two = depth_image[:, :, np.newaxis]

    print(image.shape)
    print(depth_image_two.shape)

    new_image = np.concatenate((image, depth_image_two), axis=2)

    print(new_image.shape)
    cv2.imwrite("test.png", new_image)


def test_get_3d_image():

    frame_taker = FrameTaker()
    frame_taker.start_stream()

    image = frame_taker.get_last_image()

    print(image.shape)
    cv2.imwrite("test2.png", image)


def sql_lite_test():
    connector = SQLConnector()
    connector.save_scan("test1", "path1", "path2", 1)
    connector.save_scan("test1", "path1", "path2", 2)
    val = connector.load_scan_by_name("test1")
    connector.close()
    print(val)


if __name__ == '__main__':
    take_frame()
    depth, image, intrin = load_frame("test_3", 1)
    print(1)
    # modified_depth = remove_outliers_by_depth_and_return_image(depth, 0.2)
    # pixel_1 = find_highest_valid_pixel_in_the_center(modified_depth)
    # pixel_2 = find_lowest_valid_pixel_in_the_center(modified_depth)
    #
    # distance = measure_distance(pixel_1, pixel_2, modified_depth, intrin)
    # print(distance)
    #
    # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(modified_depth, alpha=0.03), cv2.COLORMAP_JET)
    # cv2.line(depth_colormap, (pixel_1[1], pixel_1[0]), (pixel_2[1], pixel_2[0]), (255, 255, 255), 2)
    # cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    # cv2.imshow('RealSense', depth_colormap)
    # cv2.waitKey()
