import cv2
import numpy as np

from src.sqlConnector.sqlconnector import SQLConnector

ROWS = 640
COLS = 480


def save_frames_to_file_system(frames, scan_name):
    sql_connection = SQLConnector()
    frame_count = 0
    for frame in frames:
        frame_count += 1
        depth_frame = frame[0]
        intrin = frame[1]
        color = frame[2]

        depth_array = np.empty(shape=(ROWS, COLS), dtype=float)
        for row in range(ROWS):
            for col in range(COLS):
                depth_array[row][col] = depth_frame.get_distance(row, col)

        depth_name = f"fileStorage/{scan_name}_depth_{frame_count}.txt"
        image_name = f"fileStorage/{scan_name}_image_{frame_count}.png"
        intrin_name = f"fileStorage/{scan_name}_intrin_{frame_count}.txt"

        np.savetxt(depth_name, depth_array, fmt='%f')
        cv2.imwrite(image_name, color)
        save_intrin(intrin_name, intrin)
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
