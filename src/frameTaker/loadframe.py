import numpy as np
import pyrealsense2 as rs

from src.frameTaker import outliersremoval
from src.sqlConnector.sqlconnector import SQLConnector


# returns depth, color and intrin images, given a scan name and the number (order) of frame.
# the order of frame should support taking multiple frames but in this stage of the project only one is needed.
def load_frame(scan_name, frame_number):
    sql_connection = SQLConnector()
    frame = sql_connection.load_only_one_frame(scan_name, frame_number)[0]
    depth_image = np.loadtxt(frame[2], dtype=float).T
    intrin_image = load_intrin(frame[3])
    color_image = frame[4]
    sql_connection.close()

    return depth_image, color_image, intrin_image


# load the intrin string representation from a txt file and parse it into a realsense intrin object
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


