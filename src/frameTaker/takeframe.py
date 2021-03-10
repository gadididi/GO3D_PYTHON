import pyrealsense2 as rs
import numpy as np
import cv2
import keyboard

ROWS = 640
COLS = 480


def gyro_data(gyro):
    return np.asarray([gyro.x, gyro.y, gyro.z])


def accel_data(accel):
    return np.asarray([accel.x, accel.y, accel.z])


class FrameTaker:
    def __init__(self):
        self._frame_count = 0
        self._pipeline = rs.pipeline()
        self._config = rs.config()
        self._config.enable_stream(rs.stream.depth, ROWS, COLS, rs.format.z16, 30)
        self._config.enable_stream(rs.stream.color, ROWS, COLS, rs.format.bgr8, 30)
        self._config.enable_stream(rs.stream.accel, rs.format.motion_xyz32f, 200)
        self._config.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 200)
        self._frames_cache = []
        self._take_snapshot = False
        self._exit_scan = False
        self._last_image = None

    def start_stream(self):
        # Start streaming
        self._pipeline.start(self._config)

        try:
            while True:
                frames = self._pipeline.wait_for_frames(timeout_ms=30000)
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()

                accel_frame = accel_data(frames[2].as_motion_frame().get_motion_data())
                gyro_frame = gyro_data(frames[3].as_motion_frame().get_motion_data())

                if not depth_frame or not color_frame:
                    continue

                color_image = np.asanyarray(color_frame.get_data())
                accel_data_image = np.asanyarray(accel_frame)
                gyro_data_image = np.asanyarray(gyro_frame)

                if keyboard.is_pressed('p') or self._take_snapshot:  # if key 'p' is pressed
                    self._take_snapshot = False
                    self._frames_cache.append([depth_frame, accel_data_image, gyro_data_image])
                    self._frame_count += 1
                    print("picture taken")
                if keyboard.is_pressed('esc') or self._exit_scan:  # if key 'esc' is pressed
                    self._exit_scan = False
                    print("exiting")
                    self._pipeline.stop()
                    return

                cv2.circle(color_image, (int(color_image.shape[1] / 2), int(color_image.shape[0] / 2)), 2, (0, 0, 255),
                           -1)
                cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
                self._last_image = color_image
                cv2.imshow('RealSense', color_image)
                cv2.waitKey(1)

        except IOError as e:
            print(e)

    def get_frame_cache(self):
        return self._frames_cache

    def take_snapshot(self):
        self._take_snapshot = True

    def exit_scan(self):
        self._exit_scan = True

    def get_last_image(self):
        return self._last_image
