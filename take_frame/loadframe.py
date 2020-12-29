import cv2
import numpy as np


def load_frame(frame_name):
    depth_image = np.loadtxt(f"{frame_name}_depth.txt", dtype=int)
    accel_image = np.loadtxt(f"{frame_name}_accel.txt", dtype=float)
    gyro_image = np.loadtxt(f"{frame_name}_gyro.txt", dtype=float)

    print(accel_image)
    print(gyro_image)

    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', depth_image)
    cv2.waitKey()
