import cv2
import numpy as np
import pyrealsense2 as rs

from src.frameTaker import outliersremoval
from src.sqlConnector.sqlconnector import SQLConnector


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


def load_frame(scan_name, frame_number):
    sql_connection = SQLConnector()
    frame = sql_connection.load_only_one_frame(scan_name, frame_number)[0]
    depth_image = np.loadtxt(frame[2], dtype=float).T
    intrin_image = load_intrin(frame[3])
    color_image = frame[4]
    sql_connection.close()

    return depth_image, color_image, intrin_image


def load_frame_and_remove_depth_outliers(frame_name):
    depth_image = np.loadtxt(f"{frame_name}_depth.txt", dtype=float).T
    outliersremoval.remove_outliers_by_depth(depth_image, 0.1)


def load_intrin(frame_name):
    intrin = rs.intrinsics()

    fp = open(frame_name, 'r')
    intrin.coeffs = list(map(float, fp.readline().strip("[]\n").split(",")))
    intrin.fy = float(fp.readline())
    intrin.fx = float(fp.readline())
    intrin.ppx = float(fp.readline())
    intrin.ppy = float(fp.readline())
    intrin.height = int(fp.readline())
    intrin.width = int(fp.readline())
    intrin.model = rs.distortion.inverse_brown_conrady

    return intrin


