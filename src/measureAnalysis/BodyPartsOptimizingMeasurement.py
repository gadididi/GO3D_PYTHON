from src.frameTaker.distancecalculator import measure_distance
from src.frameTaker.outliersremoval import remove_outliers_by_depth_and_return_image
from src.infra import config
import math


def check_if_point_inside_the_frame(point):
    if 1 < point[0] < config.get_integer('OPTIONS', 'frame.cols'):
        if 1 < point[1] < config.get_integer('OPTIONS', 'frame.rows'):
            return True
    return False


class BodyPartsMeasurementOptimizer:

    # when init an optimiser, remove it's outliers and optimize the depth image before measuring or optimizing anything else.
    def __init__(self, depth_frame):
        self._optimized_depth_frame = remove_outliers_by_depth_and_return_image(depth_frame, config.get_float('LIDAR',
                                                                                                              "lidar.render.distance"))

    # measure distance in two parts:
    # first, traverse on the image from the foot and up, until you exit the body space.
    # second, sum the distances between that point of exit to the head and leg.
    def find_height_from_head_to_legs(self, head, ankle, intrin):
        foot = self.find_foot(ankle)
        foot_point_cols = foot[0]
        foot_point_rows = foot[1]

        line_from_foot_rows = foot_point_rows
        depth = self._optimized_depth_frame[line_from_foot_rows, foot_point_cols]
        while depth < 1000 and line_from_foot_rows > 1:
            depth = self._optimized_depth_frame[line_from_foot_rows - 1, foot_point_cols]
            if depth < 1000:
                line_from_foot_rows = line_from_foot_rows - 1

        head_point_cols = head[0]
        from_head = measure_distance(head, (head_point_cols, line_from_foot_rows), self._optimized_depth_frame,
                                     intrin)
        from_leg = measure_distance(foot, (foot_point_cols, line_from_foot_rows),
                                    self._optimized_depth_frame, intrin)

        print("distances:")
        print(f"from_head: {from_head}")
        print(f"from_leg: {from_leg}")
        print(f"from_leg + from_head: {from_leg + from_head}")
        return from_leg + from_head

    # calculates the height from the head to both of the feet, than returns the average
    def find_height(self, right_ankle, left_ankle, head, intrin):

        right_foot = self.find_foot(right_ankle)
        left_foot = self.find_foot(left_ankle)

        distance_to_right_foot = measure_distance(head, right_foot, self._optimized_depth_frame, intrin)
        distance_to_left_foot = measure_distance(head, left_foot, self._optimized_depth_frame, intrin)
        distance_between_feet = measure_distance(right_foot, left_foot, self._optimized_depth_frame, intrin)

        cos_alpha = (pow(distance_between_feet, 2) - pow(distance_to_left_foot, 2) - pow(distance_to_right_foot, 2)) / (
                2 * distance_to_left_foot * distance_to_right_foot)
        alpha = math.acos(cos_alpha)

        height = distance_to_right_foot * math.sin(alpha)

        print("distances:")
        print(height)

        print("average:")
        print((distance_to_left_foot + distance_to_right_foot) / 2)

    # travers on the depth image in order to find the lowest point of the foot in the picture.
    def find_foot(self, ankle):
        ankle_point_cols = ankle[0]
        ankle_point_rows = ankle[1]

        # bottom ankle border
        bottom_ankle_border = ankle_point_rows
        depth = self._optimized_depth_frame[bottom_ankle_border, ankle_point_cols]
        while depth < 1000 and bottom_ankle_border < config.get_integer('OPTIONS', 'frame.rows') - 1:
            depth = self._optimized_depth_frame[bottom_ankle_border + 1, ankle_point_cols]
            if depth < 1000:
                bottom_ankle_border = bottom_ankle_border + 1
        return ankle_point_cols, bottom_ankle_border

    # travers on the depth image in order to find the highest point of the middle of the head.
    def optimize_head_position(self, head_point):
        new_head_point_cols = head_point[0]
        new_head_point_rows = head_point[1]

        # right head border
        head_right_border = new_head_point_cols
        depth = self._optimized_depth_frame[new_head_point_rows, head_right_border]
        while depth < 1000 and head_right_border < 638:
            depth = self._optimized_depth_frame[new_head_point_rows, head_right_border + 1]
            if depth < 1000:
                head_right_border = head_right_border + 1

        # left head border
        head_left_border = new_head_point_cols
        depth = self._optimized_depth_frame[new_head_point_rows, head_left_border]
        while depth < 1000 and head_left_border > 1:
            depth = self._optimized_depth_frame[new_head_point_rows, head_left_border - 1]
            if depth < 1000:
                head_left_border = head_left_border - 1

        new_head_point_cols = round((head_right_border + head_left_border) / 2)

        # top head border
        head_top_border = new_head_point_rows
        depth = self._optimized_depth_frame[head_top_border, new_head_point_cols]
        while depth < 1000 and head_top_border > 1:
            depth = self._optimized_depth_frame[head_top_border - 1, new_head_point_cols]
            if depth < 1000:
                head_top_border = head_top_border - 1

        return self.advanced_head_optimization((new_head_point_cols, head_top_border))

    # after finding the highest point of the middle of the head, sometimes the head is tilted and causing the heights
    # point of the head to be somewhere else than the center of the head.
    # this method will perform a circular search in order to find that top point.
    def advanced_head_optimization(self, head):
        new_head_point_cols = head[0]
        new_head_point_rows = head[1]

        has_reached_the_top = False

        while not has_reached_the_top:
            for i in range(-10, 10):
                if check_if_point_inside_the_frame((new_head_point_cols + i, new_head_point_rows - 1)):
                    if self._optimized_depth_frame[new_head_point_rows - 1, new_head_point_cols + i] < 1000:
                        new_head_point_rows = new_head_point_rows - 1
                        new_head_point_cols = new_head_point_cols + i
                        break
                has_reached_the_top = True

        return new_head_point_cols, new_head_point_rows

    # optimizes the shoulder positions and straightens the line between the right and the left shoulders.
    def optimize_shoulders_position(self, point1, point2):
        average_height = round((point1[1] + point2[1]) / 2)

        # right shoulder border
        shoulder_right_border = point2[0]
        depth = self._optimized_depth_frame[average_height, shoulder_right_border]
        while depth < 1000 and shoulder_right_border < 638:
            depth = self._optimized_depth_frame[average_height, shoulder_right_border + 1]
            if depth < 1000:
                shoulder_right_border = shoulder_right_border + 1

        # left shoulder border
        shoulder_left_border = point1[0]
        depth = self._optimized_depth_frame[average_height, shoulder_left_border]
        while depth < 1000 and shoulder_left_border > 1:
            depth = self._optimized_depth_frame[average_height, shoulder_left_border - 1]
            if depth < 1000:
                shoulder_left_border = shoulder_left_border - 1

        return (shoulder_left_border, average_height), (shoulder_right_border, average_height)

    # optimizes the abdomen position and straightens the line between the right and the left points of the abdomen.
    def optimize_abdomen_position(self, point1, point2):
        average_height = round((point1[1] + point2[1]) / 2)

        # right abdomen border
        abdomen_right_border = point2[0]
        depth = self._optimized_depth_frame[average_height, abdomen_right_border]
        while depth < 1000 and abdomen_right_border < 638:
            depth = self._optimized_depth_frame[average_height, abdomen_right_border + 1]
            if depth < 1000:
                abdomen_right_border = abdomen_right_border + 1

        # left abdomen border
        abdomen_left_border = point1[0]
        depth = self._optimized_depth_frame[average_height, abdomen_left_border]
        while depth < 1000 and abdomen_left_border > 1:
            depth = self._optimized_depth_frame[average_height, abdomen_left_border - 1]
            if depth < 1000:
                abdomen_left_border = abdomen_left_border - 1

        return (abdomen_left_border, average_height), (abdomen_right_border, average_height)

    # optimizes the knee position by centering the point to the middle of the knee.
    def optimize_knee_position(self, knee_point):
        new_knee_point_cols = knee_point[0]
        new_knee_point_rows = knee_point[1]

        # right knee border
        knee_right_border = new_knee_point_cols
        depth = self._optimized_depth_frame[new_knee_point_rows, knee_right_border]
        while depth < 1000 and knee_right_border < 638:
            depth = self._optimized_depth_frame[new_knee_point_rows, knee_right_border + 1]
            if depth < 1000:
                knee_right_border = knee_right_border + 1

        # left knee border
        knee_left_border = new_knee_point_cols
        depth = self._optimized_depth_frame[new_knee_point_rows, knee_left_border]
        while depth < 1000 and knee_left_border > 1:
            depth = self._optimized_depth_frame[new_knee_point_rows, knee_left_border - 1]
            if depth < 1000:
                knee_left_border = knee_left_border - 1

        new_knee_point_cols = round((knee_right_border + knee_left_border) / 2)
        return new_knee_point_cols, new_knee_point_rows

    # optimizes the ankle position by centering the point to the middle of the ankle.
    def optimize_ankle_position(self, ankle_point):
        new_ankle_point_cols = ankle_point[0]
        new_ankle_point_rows = ankle_point[1]

        # right ankle border
        ankle_right_border = new_ankle_point_cols
        depth = self._optimized_depth_frame[new_ankle_point_rows, ankle_right_border]
        while depth < 1000 and ankle_right_border < 638:
            depth = self._optimized_depth_frame[new_ankle_point_rows, ankle_right_border + 1]
            if depth < 1000:
                ankle_right_border = ankle_right_border + 1

        # left ankle border
        ankle_left_border = new_ankle_point_cols
        depth = self._optimized_depth_frame[new_ankle_point_rows, ankle_left_border]
        while depth < 1000 and ankle_left_border > 1:
            depth = self._optimized_depth_frame[new_ankle_point_rows, ankle_left_border - 1]
            if depth < 1000:
                ankle_left_border = ankle_left_border - 1

        new_ankle_point_cols = round((ankle_right_border + ankle_left_border) / 2)
        return self.find_foot((new_ankle_point_cols, new_ankle_point_rows))

    # traversing on the depth image in order to find the lowest point of the ankle.
    def find_ankles_lowest_point(self, ankle_point):
        new_ankle_point_cols = ankle_point[0]
        new_ankle_point_rows = ankle_point[1]

        # ankle bottom border
        ankle_bottom_border = new_ankle_point_rows
        depth = self._optimized_depth_frame[ankle_bottom_border, new_ankle_point_cols]
        while depth < 1000 and ankle_bottom_border < 479:
            depth = self._optimized_depth_frame[ankle_bottom_border + 1, new_ankle_point_cols]
            if depth < 1000:
                ankle_bottom_border = ankle_bottom_border + 1

        return new_ankle_point_cols, new_ankle_point_rows

    # in order to make the measuring more robust, given a point, validate it is on the person and not pointing to the
    # background. If its corrupted, try to find the nearest valid point (as corrupted points are usually quite close to
    # the valid and true point.
    def validate_and_fix_corrupted_point(self, point):
        depth = self._optimized_depth_frame[point[1], point[0]]
        if depth < 1000:
            print(f"point is valid, distance:{depth}")
            return point
        else:
            new_point = self.find_nearest_valid_point(point)
            print(f"point isn't valid, changing to {new_point}")
            return new_point

    # performs a circular search in order to find the nearest valid point of a corrupted point (the points on the background)
    def find_nearest_valid_point(self, point):
        point_cols = point[0]
        point_rows = point[1]

        for k in range(1, 10):
            for i in range(k * (-1), k):
                for j in range(k * (-1), k):
                    if check_if_point_inside_the_frame((point_cols + i, point_rows + j)):
                        if self._optimized_depth_frame[point_rows + j, point_cols + i] < 1000:
                            return point_cols + i, point_rows + j

        print("error validating point")
        return point

    def get_optimized_frame(self):
        return self._optimized_depth_frame
