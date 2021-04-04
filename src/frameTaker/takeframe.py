import time

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
        self._last_depth_image = None

    def start_stream(self):
        # Start streaming
        self._pipeline.start(self._config)
        align_to = rs.stream.color
        align = rs.align(align_to)

        try:
            while True:
                frames = self._pipeline.wait_for_frames(timeout_ms=30000)
                aligned_frames = align.process(frames)
                color_frame = aligned_frames.get_color_frame()
                depth_frame = aligned_frames.get_depth_frame()

                if not depth_frame or not color_frame:
                    continue

                # Intrinsics
                color_intrin = color_frame.profile.as_video_stream_profile().intrinsics

                color_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())

                if keyboard.is_pressed('p') or self._take_snapshot:  # if key 'p' is pressed
                    self._take_snapshot = False
                    self._frames_cache.append([depth_frame, color_intrin, color_image])
                    self._frame_count += 1
                    time.sleep(0.5)
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
                self._last_depth_image = depth_image
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
        self.reset_cache()

    def reset_cache(self):
        self._frame_count = 0
        self._frames_cache = []
        self._take_snapshot = False
        self._last_image = None
        self._last_depth_image = None

    def get_last_image(self):
        return self._last_image

    def get_last_depth_image(self):
        return self._last_depth_image
