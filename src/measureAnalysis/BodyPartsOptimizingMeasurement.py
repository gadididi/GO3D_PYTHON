from src.frameTaker.distancecalculator import measure_distance
from src.frameTaker.outliersremoval import remove_outliers_by_depth_and_return_image


def check_if_point_inside_the_frame(point):
    if 1 < point[0] < 478:
        if 1 < point[1] < 638:
            return True
    return False


class BodyPartsMeasurementOptimizer:
    def __init__(self, depth_frame):
        self._optimized_depth_frame = remove_outliers_by_depth_and_return_image(depth_frame, 0.2)

    def find_height(self, right_ankle, left_ankle, head, intrin):
        distance_to_right_ankle = measure_distance(head, right_ankle, self._optimized_depth_frame, intrin)
        distance_to_left_ankle = measure_distance(head, left_ankle, self._optimized_depth_frame, intrin)

        print("distances:")
        print(distance_to_right_ankle)
        print(distance_to_left_ankle)

        print("average:")
        print((distance_to_left_ankle + distance_to_right_ankle) / 2)

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

        return new_head_point_cols, head_top_border

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

        print(f"knee left border: {knee_left_border} knee right border: {knee_right_border}")
        new_knee_point_cols = round((knee_right_border + knee_left_border) / 2)
        return new_knee_point_cols, new_knee_point_rows

    def find_lowest_bottom_point(self, ankle_point):
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

    def validate_and_fix_corrupted_point(self, point):
        depth = self._optimized_depth_frame[point[1], point[0]]
        if depth < 1000:
            print(f"point is valid, distance:{depth}")
            return point
        else:
            new_point = self.find_nearest_valid_point(point)
            print(f"point isn't valid, changing to {new_point}")
            return new_point

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
