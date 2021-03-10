import pyrealsense2 as rs
import numpy as np

# Configure depth and color streams
from src.frameTaker.takeframe import accel_data, gyro_data


def start_test():
    test_score = 0
    test_cases = 0

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.accel, rs.format.motion_xyz32f, 200)
    config.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 200)

    # Start streaming
    pipeline.start(config)

    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    accel_frame = accel_data(frames[1].as_motion_frame().get_motion_data())
    gyro_frame = gyro_data(frames[2].as_motion_frame().get_motion_data())

    # Convert images to numpy arrays
    depth_image = np.asanyarray(depth_frame.get_data())
    accel_data_image = np.asanyarray(accel_frame)
    gyro_data_image = np.asanyarray(gyro_frame)
    pipeline.stop()

    np.savetxt("frame_capture_test_depth.txt", depth_image, fmt='%d')
    np.savetxt("frame_capture_test_accel.txt", accel_data_image, fmt='%.32f')
    np.savetxt("frame_capture_test_gyro.txt", gyro_data_image, fmt='%.32f')

    new_depth_image = np.loadtxt("frame_capture_test_depth.txt", dtype=int)
    new_accel_data_image = np.loadtxt("frame_capture_test_accel.txt", dtype=np.float64)
    new_gyro_data_image = np.loadtxt("frame_capture_test_gyro.txt", dtype=np.float64)

    # check if the save kept the data and didn't changed it
    test_cases = test_cases + 1
    if (new_depth_image == depth_image).all():
        test_score = test_score + 1
        print("Yes, both the depth arrays are same")
    else:
        print("No, both the depth arrays are not same")

    test_cases = test_cases + 1
    if (new_accel_data_image == accel_data_image).all():
        test_score = test_score + 1
        print("Yes, both the accel arrays are same")
    else:
        print("No, both the accel arrays are not same")

    test_cases = test_cases + 1
    if (new_gyro_data_image == gyro_data_image).all():
        test_score = test_score + 1
        print("Yes, both the gyro arrays are same")
    else:
        print("No, both the gyro arrays are not same")

    return float(test_score / test_cases)