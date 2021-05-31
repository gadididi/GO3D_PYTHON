import cv2
import numpy as np

from src.detection.bodyDetection import HumanPartSegmentationDetector
from src.frameSaver import saveframe
from src.frameTaker.distancecalculator import measure_distance
from src.frameTaker.loadframe import load_frame
from src.frameTaker.outliersremoval import remove_outliers_by_depth
from src.frameTaker.takeframe import FrameTaker
from src.infra import config
from src.infra.config import load_configs
from src.measureAnalysis.BodyPartsOptimizingMeasurement import BodyPartsMeasurementOptimizer
from src.sqlConnector.sqlconnector import SQLConnector


def take_frame(frame_name):
    frame_taker = FrameTaker()
    frame_taker.start_stream()
    saveframe.save_frames_to_file_system(frame_taker.get_frame_cache(), frame_name)


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
    load_configs()
    # scans = SQLConnector().get_last_k_scans(10)
    get_cv_image_base_64 = SQLConnector().get_cv_image_base_64("test_21")

    print("config check")
    rows = config.get_integer('OPTIONS', 'frame.rows')
    print(rows)
    # take_frame("test_31")
    depth, image, intrin = load_frame("MonMay31202111,12,17GMT+0300(IsraelDaylightTime)", 1)
    optimizer = BodyPartsMeasurementOptimizer(depth)
    # print(1)

    model = "detection/models/enet256_weight0501.hdf5"
    caffe_model = "detection/models/pose_iter_440000.caffemodel"
    pose_deploy = "detection/models/pose_deploy_linevec.prototxt"

    human_part_detector = HumanPartSegmentationDetector(model, caffe_model, pose_deploy)
    body_parts = human_part_detector.find_body_points("fileStorage/MonMay31202111,12,17GMT+0300(IsraelDaylightTime)_image_1.png")

    shoulders = body_parts['shoulders']
    abdomen = body_parts['abdomen']
    head = body_parts['head']
    ankles = body_parts['ankles']
    knees = body_parts['knees']
    elbows = body_parts['elbows']

    # validation
    validated_left_shoulder = optimizer.validate_and_fix_corrupted_point(shoulders[0])
    validated_right_shoulder = optimizer.validate_and_fix_corrupted_point(shoulders[1])
    validated_left_abdomen = optimizer.validate_and_fix_corrupted_point(abdomen[0])
    validated_right_abdomen = optimizer.validate_and_fix_corrupted_point(abdomen[1])
    validated_left_knee = optimizer.validate_and_fix_corrupted_point(knees[0])
    validated_right_knee = optimizer.validate_and_fix_corrupted_point(knees[1])
    validated_left_ankle = optimizer.validate_and_fix_corrupted_point(ankles[0])
    validated_right_ankle = optimizer.validate_and_fix_corrupted_point(ankles[1])
    validated_head = optimizer.validate_and_fix_corrupted_point(head)
    validated_left_elbow = optimizer.validate_and_fix_corrupted_point(elbows[0])
    validated_right_elbow = optimizer.validate_and_fix_corrupted_point(elbows[1])

    new_shoulder = optimizer.optimize_shoulders_position(validated_left_shoulder, validated_right_shoulder)
    new_abdomen = optimizer.optimize_abdomen_position(validated_left_abdomen, validated_right_abdomen)
    print(f"abdomen size: {measure_distance(new_abdomen[0], new_abdomen[1], depth, intrin)}")

    new_left_knee = optimizer.optimize_knee_position(validated_left_knee)
    new_right_knee = optimizer.optimize_knee_position(validated_right_knee)

    new_head = optimizer.optimize_head_position(validated_head)
    new_left_ankle = optimizer.optimize_ankle_position(validated_left_ankle)
    new_right_ankle = optimizer.optimize_ankle_position(validated_right_ankle)

    bottom_leg_right = optimizer.validate_and_fix_corrupted_point(optimizer.find_lowest_bottom_point(new_right_ankle))
    bottom_leg_left = optimizer.validate_and_fix_corrupted_point(optimizer.find_lowest_bottom_point(new_left_ankle))

    optimizer.find_height_version_2(new_head, bottom_leg_right, intrin)

    optimizer.find_height(bottom_leg_right, bottom_leg_left, new_head, intrin)

    depth_map_show = None
    depth_map_show = cv2.normalize(optimizer.get_optimized_frame(), depth_map_show, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    depth_map_show = cv2.applyColorMap(depth_map_show, cv2.COLORMAP_COOL)

    cv2.circle(depth_map_show, shoulders[0], 1, (255, 255, 255))
    cv2.circle(depth_map_show, shoulders[1], 1, (255, 255, 255))
    cv2.circle(depth_map_show, bottom_leg_right, 5, (255, 255, 255))
    cv2.circle(depth_map_show, bottom_leg_left, 5, (255, 255, 255))
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

    cv2.circle(depth_map_show, elbows[0], 5, (100, 100, 100))
    cv2.circle(depth_map_show, elbows[1], 5, (100, 100, 100))

    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', depth_map_show)
    cv2.waitKey(0)
