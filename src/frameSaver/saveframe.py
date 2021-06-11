import cv2
import numpy as np

from src.infra import config
from src.sqlConnector.sqlconnector import SQLConnector


def save_frames_to_file_system(frames, scan_name):
    sql_connection = SQLConnector()
    frame_count = 0

    # should support multiple number of frames, but only one is needed in this part of the project
    for frame in frames:
        frame_count += 1
        depth_frame = frame[0]
        intrin = frame[1]
        color = frame[2]

        rows = config.get_integer('LIDAR', 'lidar.rows')
        cols = config.get_integer('LIDAR', 'lidar.cols')

        # extract the distance from the depth frame (pixel by pixel)
        depth_array = np.empty(shape=(rows, cols), dtype=float)
        for row in range(rows):
            for col in range(cols):
                depth_array[row][col] = depth_frame.get_distance(row, col)

        # file locations of the save
        depth_name = f"fileStorage/{scan_name}_depth_{frame_count}.txt"
        image_name = f"fileStorage/{scan_name}_image_{frame_count}.png"
        intrin_name = f"fileStorage/{scan_name}_intrin_{frame_count}.txt"

        # save depth as text
        np.savetxt(depth_name, depth_array, fmt='%f')

        # save the rgb image as png
        cv2.imwrite(image_name, color)
        
        # call to intrin saver, to save the intring details as text
        save_intrin(intrin_name, intrin)

        # save all the data in the db
        sql_connection.save_scan(scan_name, depth_name, intrin_name, image_name, frame_count)
    sql_connection.close()


def save_intrin(intrin_name, intrin):
    fp = open(intrin_name, "w")
    fp.write(f"{intrin.coeffs}\n")  # coeffs
    fp.write(f"{intrin.fx}\n")  # fx
    fp.write(f"{intrin.fy}\n")  # fy
    fp.write(f"{intrin.ppx}\n")  # ppx
    fp.write(f"{intrin.ppy}\n")  # ppy
    fp.write(f"{intrin.height}\n")  # height
    fp.write(f"{intrin.width}\n")  # width
    fp.close()
