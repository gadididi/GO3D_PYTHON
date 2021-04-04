import cv2
import numpy as np

from src.detection.bodyDetection import HumanPartSegmentationDetector
from src.frameSaver import saveframe
from src.frameTaker.distancecalculator import measure_distance
from src.frameTaker.loadframe import load_frame
from src.frameTaker.outliersremoval import remove_outliers_by_depth
from src.frameTaker.takeframe import FrameTaker
from src.measureAnalysis.BodyPartsOptimizingMeasurement import BodyPartsMeasurementOptimizer
from src.sqlConnector.sqlconnector import SQLConnector


def take_frame():
    frame_taker = FrameTaker()
    frame_taker.start_stream()
    saveframe.save_frames_to_file_system(frame_taker.get_frame_cache(), "test_10")


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
    # take_frame()
    depth, image, intrin = load_frame("test_10", 2)
    optimizer = BodyPartsMeasurementOptimizer(depth)
    # print(1)

    model = "detection/models/enet256_weight0501.hdf5"
    caffe_model = "detection/models/pose_iter_440000.caffemodel"
    pose_deploy = "detection/models/pose_deploy_linevec.prototxt"

    human_part_detector = HumanPartSegmentationDetector(model, caffe_model, pose_deploy)
    body_parts = human_part_detector.find_body_points("fileStorage/test_10_image_1.png")

    shoulders = body_parts['shoulders']
    abdomen = body_parts['abdomen']
    head = body_parts['head']
    ankles = body_parts['ankles']
    knees = body_parts['knees']

    new_shoulder = optimizer.optimize_shoulders_position(shoulders[0], shoulders[1])
    print(f"shoulder size: {measure_distance(new_shoulder[0], new_shoulder[1], depth, intrin)}")

    new_abdomen = optimizer.optimize_abdomen_position(abdomen[0], abdomen[1])
    print(f"abdomen size: {measure_distance(new_abdomen[0], new_abdomen[1], depth, intrin)}")

    new_left_knee = optimizer.optimize_knee_position(knees[0])
    new_right_knee = optimizer.optimize_knee_position(knees[1])

    new_head = optimizer.optimize_head_position(head)
    new_left_ankle = optimizer.optimize_knee_position(ankles[0])
    new_right_ankle = optimizer.optimize_knee_position(ankles[1])

    depth_map_show = None
    depth_map_show = cv2.normalize(depth, depth_map_show, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    depth_map_show = cv2.applyColorMap(depth_map_show, cv2.COLORMAP_COOL)

    cv2.circle(depth_map_show, shoulders[0], 1, (255, 255, 255))
    cv2.circle(depth_map_show, shoulders[1], 1, (255, 255, 255))
    cv2.circle(depth_map_show, head, 1, (255, 255, 255))
    cv2.circle(depth_map_show, new_head, 5, (100, 0, 255))
    cv2.line(depth_map_show, shoulders[0], shoulders[1], (255, 255, 255))
    cv2.circle(depth_map_show, new_shoulder[0], 5, (0, 0, 255))
    cv2.circle(depth_map_show, new_shoulder[1], 5, (0, 0, 255))
    cv2.circle(depth_map_show, abdomen[0], 1, (255, 255, 255))
    cv2.circle(depth_map_show, abdomen[1], 1, (255, 255, 255))
    cv2.line(depth_map_show, abdomen[0], abdomen[1], (255, 255, 255))
    cv2.circle(depth_map_show, ankles[0], 1, (255, 255, 255))
    cv2.circle(depth_map_show, new_left_ankle, 5, (0, 0, 0))
    cv2.circle(depth_map_show, new_right_ankle, 5, (0, 0, 0))
    cv2.circle(depth_map_show, knees[0], 1, (255, 255, 255))
    cv2.circle(depth_map_show, knees[1], 1, (255, 255, 255))
    cv2.circle(depth_map_show, new_left_knee, 5, (0, 255, 0))
    cv2.circle(depth_map_show, new_right_knee, 5, (0, 255, 0))
    cv2.circle(depth_map_show, new_abdomen[0], 5, (255, 0, 0))
    cv2.circle(depth_map_show, new_abdomen[1], 5, (255, 0, 0))
    cv2.line(depth_map_show, knees[0], ankles[0], (255, 255, 255))
    cv2.line(depth_map_show, knees[1], ankles[1], (255, 255, 255))
    cv2.line(depth_map_show, knees[1], abdomen[1], (255, 255, 255))
    cv2.line(depth_map_show, knees[0], abdomen[0], (255, 255, 255))
    cv2.circle(depth_map_show, head, 1, (255, 255, 255))
    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', depth_map_show)
    cv2.waitKey(0)
