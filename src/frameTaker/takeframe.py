import time

import pyrealsense2 as rs
import numpy as np
import cv2
import keyboard

from src.infra import config


def gyro_data(gyro):
    return np.asarray([gyro.x, gyro.y, gyro.z])


def accel_data(accel):
    return np.asarray([accel.x, accel.y, accel.z])


class FrameTaker:
    def __init__(self):
        self._cols = config.get_integer('LIDAR', 'lidar.cols')
        self._rows = config.get_integer('LIDAR', 'lidar.rows')

        self._frame_count = 0
        self._pipeline = rs.pipeline()
        self._config = rs.config()

        # enable various streams in the camera.

        # enable LiDAR
        self._config.enable_stream(rs.stream.depth, self._rows, self._cols, rs.format.z16, 30)

        # enable RGB camera
        self._config.enable_stream(rs.stream.color, self._rows, self._cols, rs.format.bgr8, 30)

        # enable accelerometer (for test and calibration purposes)
        self._config.enable_stream(rs.stream.accel, rs.format.motion_xyz32f, 200)

        # enable gyroscope (for test and calibration purposes)
        self._config.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 200)

        self._frames_cache = []
        self._take_snapshot = False
        self._exit_scan = False
        self._last_image = None
        self._last_depth_image = None
        self._healthy = False

    def start_stream(self):
        # Start streaming
        self._pipeline.start(self._config)
        align_to = rs.stream.color
        align = rs.align(align_to)

        try:
            while True:
                # time out is 30 seconds because on some computers, booting the camera takes quite a time.
                frames = self._pipeline.wait_for_frames(timeout_ms=30000)
                aligned_frames = align.process(frames)
                color_frame = aligned_frames.get_color_frame()
                depth_frame = aligned_frames.get_depth_frame()

                if not depth_frame or not color_frame:
                    continue

                # intrinsics
                color_intrin = color_frame.profile.as_video_stream_profile().intrinsics

                # build np array representation for the color and depth images
                color_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())

                # if the users wishes to take a snapshot
                if self._take_snapshot:
                    self._take_snapshot = False
                    self._frames_cache.append([depth_frame, color_intrin, color_image])
                    self._frame_count += 1
                    time.sleep(0.5)
                    print("picture taken")

                # if key 'esc' is pressed or the user wishes to cancel the can
                if keyboard.is_pressed('esc') or self._exit_scan:
                    self._exit_scan = False
                    print("exiting")
                    self._pipeline.stop()
                    return

                # build an heatmap out of the depth map in order to show that in the GUI.
                depth_map_show = None
                depth_map_show = cv2.normalize(depth_image, depth_map_show, alpha=0, beta=255,
                                               norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                depth_map_show = cv2.applyColorMap(depth_map_show, cv2.COLORMAP_COOL)
                cv2.circle(depth_map_show, (int(depth_map_show.shape[1] / 2), int(depth_map_show.shape[0] / 2)), 2,
                           (0, 0, 255),
                           -1)
                self._last_image = depth_map_show
                self._last_depth_image = depth_image
                self._healthy = True

        except IOError as e:
            print(e)
            self._healthy = False
        except RuntimeError as e:
            print(e)
            self._healthy = False

    def get_frame_cache(self):
        return self._frames_cache

    def take_snapshot(self):
        self._take_snapshot = True

    def exit_scan(self):
        self._exit_scan = True
        self._healthy = False
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

    def is_healthy(self):
        return self._healthy
