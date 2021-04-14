from src.frameTaker.distancecalculator import measure_distance
from src.frameTaker.loadframe import load_frame
from src.measureAnalysis.BodyPartsOptimizingMeasurement import BodyPartsMeasurementOptimizer


class FrameProcessor:
    def __init__(self, frame_name, ml_config):
        self._results = 0
        self._frame_name = frame_name
        self._ml_config = ml_config
        self._frame_name = frame_name
        self._depth, self._image, self._intrin = load_frame(frame_name, 1)
        self._optimizer = BodyPartsMeasurementOptimizer(self._depth)

        # To be calculated
        self._calculated_height = 0
        self._calculated_shoulder_length = 0
        self._calculated_abdomen_length = 0
        self._calculated_right_shoulder_to_elbow = 0
        self._calculated_left_shoulder_to_elbow = 0
        self._calculated_right_thigh = 0
        self._calculated_left_thigh = 0

    def start_processing(self):
        human_part_detector = self._ml_config.get_human_parts_detector()
        body_parts = human_part_detector.find_body_points(f"fileStorage/{self._frame_name}_image_1.png")

        shoulders = body_parts['shoulders']
        abdomen = body_parts['abdomen']
        head = body_parts['head']
        ankles = body_parts['ankles']
        knees = body_parts['knees']
        elbows = body_parts['elbows']

        # validation
        validated_left_shoulder = self._optimizer.validate_and_fix_corrupted_point(shoulders[0])
        validated_right_shoulder = self._optimizer.validate_and_fix_corrupted_point(shoulders[1])
        validated_left_abdomen = self._optimizer.validate_and_fix_corrupted_point(abdomen[0])
        validated_right_abdomen = self._optimizer.validate_and_fix_corrupted_point(abdomen[1])
        validated_left_knee = self._optimizer.validate_and_fix_corrupted_point(knees[0])
        validated_right_knee = self._optimizer.validate_and_fix_corrupted_point(knees[1])
        validated_left_ankle = self._optimizer.validate_and_fix_corrupted_point(ankles[0])
        validated_right_ankle = self._optimizer.validate_and_fix_corrupted_point(ankles[1])
        validated_head = self._optimizer.validate_and_fix_corrupted_point(head)
        validated_left_elbow = self._optimizer.validate_and_fix_corrupted_point(elbows[0])
        validated_right_elbow = self._optimizer.validate_and_fix_corrupted_point(elbows[1])

        new_shoulder = self._optimizer.optimize_shoulders_position(validated_left_shoulder, validated_right_shoulder)
        new_abdomen = self._optimizer.optimize_abdomen_position(validated_left_abdomen, validated_right_abdomen)
        new_left_knee = self._optimizer.optimize_knee_position(validated_left_knee)
        new_right_knee = self._optimizer.optimize_knee_position(validated_right_knee)
        new_head = self._optimizer.optimize_head_position(validated_head)
        new_left_ankle = self._optimizer.optimize_knee_position(validated_left_ankle)
        new_right_ankle = self._optimizer.optimize_knee_position(validated_right_ankle)
        bottom_leg_right = self._optimizer.validate_and_fix_corrupted_point(
            self._optimizer.find_lowest_bottom_point(new_right_ankle))
        bottom_leg_left = self._optimizer.validate_and_fix_corrupted_point(
            self._optimizer.find_lowest_bottom_point(new_left_ankle))

        self._calculated_height = self._optimizer.find_height(bottom_leg_right, bottom_leg_left, new_head, self._intrin)
        self._calculated_abdomen_length = measure_distance(new_abdomen[0], new_abdomen[1], self._depth, self._intrin)
        self._calculated_shoulder_length = measure_distance(new_shoulder[0], new_shoulder[1], self._depth, self._intrin)
        self._calculated_right_shoulder_to_elbow = measure_distance(new_shoulder[0], validated_left_elbow, self._depth,
                                                                    self._intrin)
        self._calculated_left_shoulder_to_elbow = measure_distance(new_shoulder[1], validated_right_elbow, self._depth,
                                                                   self._intrin)
        self._calculated_right_thigh = measure_distance(new_abdomen[1], new_right_knee, self._depth, self._intrin)
        self._calculated_left_thigh = measure_distance(new_abdomen[0], new_left_knee, self._depth, self._intrin)

        self.generate_results()

    def get_results(self):
        return self._results

    def generate_results(self):
        self._results = {'height': self._calculated_height, 'abdomen': self._calculated_abdomen_length,
                         'shoulders': self._calculated_shoulder_length,
                         'right_shoulder_to_elbow': self._calculated_right_shoulder_to_elbow,
                         'left_shoulder_to_elbow': self._calculated_left_shoulder_to_elbow,
                         'right_thigh': self._calculated_left_thigh}