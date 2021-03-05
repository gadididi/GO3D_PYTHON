import numpy as np

ROWS = 640
COLS = 480


def save_frames_to_file_system(frames, file_name):
    frame_count = 0
    for frame in frames:
        frame_count += 1
        depth_frame = frame[0]
        accel_data_image = frame[1]
        gyro_data_image = frame[2]

        depth_array = np.empty(shape=(ROWS, COLS), dtype=float)
        for row in range(ROWS):
            for col in range(COLS):
                depth_array[row][col] = depth_frame.get_distance(row, col)

        np.savetxt(f"{file_name}]_depth_{frame_count}.txt", depth_array, fmt='%f')
        np.savetxt(f"{file_name}_accel_{frame_count}..txt", accel_data_image, fmt='%f')
        np.savetxt(f"{file_name}_gyro_{frame_count}..txt", gyro_data_image, fmt='%f')
