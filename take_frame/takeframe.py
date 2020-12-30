import pyrealsense2 as rs
import numpy as np
import cv2
import keyboard
import matplotlib.pyplot as plt


def gyro_data(gyro):
    return np.asarray([gyro.x, gyro.y, gyro.z])


def accel_data(accel):
    return np.asarray([accel.x, accel.y, accel.z])


class FrameTaker:
    def __init__(self, scan_name):
        self._frame_count = 0
        self._scan_name = scan_name
        self._pipeline = rs.pipeline()
        self._config = rs.config()
        self._config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self._config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self._config.enable_stream(rs.stream.accel, rs.format.motion_xyz32f, 200)
        self._config.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 200)

    def start_stream(self):
        # Start streaming
        self._pipeline.start(self._config)

        try:
            while True:
                frames = self._pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()

                accel_frame = accel_data(frames[2].as_motion_frame().get_motion_data())
                gyro_frame = gyro_data(frames[3].as_motion_frame().get_motion_data())

                if not depth_frame or not color_frame:
                    continue

                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                accel_data_image = np.asanyarray(accel_frame)
                gyro_data_image = np.asanyarray(gyro_frame)

                if keyboard.is_pressed('p'):  # if key 'p' is pressed
                    self.save_np_arrays(depth_image=depth_image, accel_data_image=accel_data_image, gyro_data_image=gyro_data_image)
                    print("picture taken")
                if keyboard.is_pressed('esc'):  # if key 'esc' is pressed
                    print("exiting")
                    return

                cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
                cv2.imshow('RealSense', color_image)
                cv2.waitKey(1)

        finally:
            # Stop streaming
            self._pipeline.stop()

    def save_np_arrays(self, depth_image, accel_data_image, gyro_data_image):
        # plt.imsave(str(f"{self._scan_name}_{self._frame_count}_depth.png"), depth_image)
        np.savetxt(f"{self._scan_name}_{self._frame_count}_depth.txt", depth_image, fmt='%d')
        np.savetxt(f"{self._scan_name}_{self._frame_count}_accel.txt", accel_data_image, fmt='%f')
        np.savetxt(f"{self._scan_name}_{self._frame_count}_gyro.txt", gyro_data_image, fmt='%f')
