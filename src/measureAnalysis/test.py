
import threading
import time

import numpy as np
import cv2

from src.frameSaver import saveframe
from src.frameTaker.distancecalculator import find_lowest_valid_pixel_in_the_center, \
    find_highest_valid_pixel_in_the_center, measure_distance, GSD
from src.frameTaker.loadframe import load_frame
from src.frameTaker.outliersremoval import remove_outliers_by_depth, remove_outliers_by_depth_and_return_image
from src.frameTaker.takeframe import FrameTaker


def take_frame():
    frame_taker = FrameTaker()
    th = threading.Thread(target=frame_taker.start_stream)
    th.start()
    time.sleep(10)
    frame_taker.take_snapshot()
    time.sleep(1)

    saveframe.save_frames_to_file_system(frame_taker.get_frame_cache(), "test_1")


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
    cv2.imwrite( "test.png",new_image)


if __name__ == '__main__':
    test_get_4d_image()
    # take_frame()
    # depth, accel, gyro = load_frame("test_1", 1)
    # modified_depth = remove_outliers_by_depth_and_return_image(depth, 0.1)
    # pixel_1 = find_highest_valid_pixel_in_the_center(modified_depth)
    # pixel_2 = find_lowest_valid_pixel_in_the_center(modified_depth)
    #
    # distance = GSD(modified_depth.T)
    # print(abs(pixel_2[0] - pixel_1[0]) * distance)
    #
    # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(modified_depth, alpha=0.03), cv2.COLORMAP_JET)
    # cv2.line(depth_colormap, (pixel_1[1], pixel_1[0]), (pixel_2[1], pixel_2[0]), (255, 255, 255), 2)
    # cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    # cv2.imshow('RealSense', depth_colormap)
    # cv2.waitKey()
