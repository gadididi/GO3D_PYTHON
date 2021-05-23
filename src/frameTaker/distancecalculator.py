import math

import pyrealsense2 as rs
import vg


def measure_distance(pixel_1, pixel_2, depth_frame, intrin):
    u_distance = depth_frame[pixel_1[1], pixel_1[0]]
    v_distance = depth_frame[pixel_2[1], pixel_2[0]]

    point1 = rs.rs2_deproject_pixel_to_point(intrin, [pixel_1[0], pixel_1[1]], u_distance)
    point2 = rs.rs2_deproject_pixel_to_point(intrin, [pixel_2[0], pixel_2[1]], v_distance)

    return math.sqrt(
        math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2) + math.pow(point1[2] - point2[2], 2))


def get_distance(u_vector, v_vector):
    angle_between_vectors = float(vg.angle(u_vector, v_vector))
    distance = math.sqrt(
        pow(u_vector[2], 2) + pow(v_vector[2], 2) - 2 * u_vector[2] * v_vector[2] * math.cos(angle_between_vectors))
    return distance
