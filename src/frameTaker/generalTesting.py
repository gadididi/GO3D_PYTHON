from src.frameTaker.loadframe import load_frame
from src.frameTaker.distancecalculator import measure_distance, \
    find_highest_valid_pixel_in_the_center, find_lowest_valid_pixel_in_the_center
from src.frameTaker.outliersremoval import remove_outliers_by_depth_and_return_image
import cv2


# depth_frame = FrameTaker(scan_name="ori_1").start_stream()
# load_frame_and_remove_depth_outliers("test_box_0")
depth, accel, gyro = load_frame("ori_1_0")
modified_depth = remove_outliers_by_depth_and_return_image(depth, 0.3)
pixel_1 = find_highest_valid_pixel_in_the_center(modified_depth)
pixel_2 = find_lowest_valid_pixel_in_the_center(modified_depth)


depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(modified_depth, alpha=0.03), cv2.COLORMAP_JET)
cv2.line(depth_colormap, (pixel_1[1], pixel_1[0]),  (pixel_2[1], pixel_2[0]), (255, 255, 255), 2)
cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
cv2.imshow('RealSense', depth_colormap)
cv2.waitKey()
#
#
distance = measure_distance(pixel_1, pixel_2, modified_depth)
#
print(distance)

#
# print(f"Frame taking and reloading test accuracy is: {start_test()}")
