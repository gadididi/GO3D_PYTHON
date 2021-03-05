import cv2
import numpy as np

from src.frameTaker import outliersremoval


def load_frame_and_show(frame_name):
    depth_image = np.loadtxt(f"{frame_name}_depth.txt", dtype=float).T
    accel_image = np.loadtxt(f"{frame_name}_accel.txt", dtype=float)
    gyro_image = np.loadtxt(f"{frame_name}_gyro.txt", dtype=float)

    print(accel_image)
    print(gyro_image)

    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', depth_colormap)
    cv2.waitKey()


def load_frame(frame_name):
    depth_image = np.loadtxt(f"{frame_name}_depth.txt", dtype=float).T
    accel_image = np.loadtxt(f"{frame_name}_accel.txt", dtype=float)
    gyro_image = np.loadtxt(f"{frame_name}_gyro.txt", dtype=float)

    return depth_image, accel_image, gyro_image


def load_frame_and_remove_depth_outliers(frame_name):
    depth_image = np.loadtxt(f"{frame_name}_depth.txt", dtype=float).T
    outliersremoval.remove_outliers_by_depth(depth_image, 0.1)
