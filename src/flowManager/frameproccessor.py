from src.frameTaker.distancecalculator import measure_distance
from src.frameTaker.loadframe import load_frame
from src.measureAnalysis.BodyPartsOptimizingMeasurement import BodyPartsMeasurementOptimizer
from src.sqlConnector.sqlconnector import SQLConnector


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
        self._calculated_BMI_score = 0

    def start_processing(self):
        # run the body parts detector on the image
        human_part_detector = self._ml_config.get_human_parts_detector()
        body_parts = human_part_detector.find_body_points(f"fileStorage/{self._frame_name}_image_1.png")

        shoulders = body_parts['shoulders']
        abdomen = body_parts['abdomen']
        head = body_parts['head']
        ankles = body_parts['ankles']
        knees = body_parts['knees']
        elbows = body_parts['elbows']

        # validation and optimization of the points found by the model
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

        # calculate the height from the head to the legs and choose the max between legs
        calculated_height_right = self._optimizer.find_height_from_head_to_legs(new_head, new_right_ankle, self._intrin)
        calculated_height_left = self._optimizer.find_height_from_head_to_legs(new_head, new_left_ankle, self._intrin)
        self._calculated_height = max(calculated_height_left, calculated_height_right)

        # calculate body parts sizes by measuring the distance between two given points.
        self._calculated_abdomen_length = measure_distance(new_abdomen[0], new_abdomen[1], self._depth, self._intrin)
        self._calculated_shoulder_length = measure_distance(new_shoulder[0], new_shoulder[1], self._depth, self._intrin)
        self._calculated_right_shoulder_to_elbow = measure_distance(new_shoulder[0], validated_left_elbow, self._depth,
                                                                    self._intrin)
        self._calculated_left_shoulder_to_elbow = measure_distance(new_shoulder[1], validated_right_elbow, self._depth,
                                                                   self._intrin)
        self._calculated_right_thigh = measure_distance(new_abdomen[1], new_right_knee, self._depth, self._intrin)
        self._calculated_left_thigh = measure_distance(new_abdomen[0], new_left_knee, self._depth, self._intrin)

        # saves the results in-memory
        self.generate_results()

    def get_results(self):
        return self._results

    def generate_results(self):
        self._results = {'body_height': round(self._calculated_height, 2), 'abdomen': round(self._calculated_abdomen_length, 2),
                         'shoulders': round(self._calculated_shoulder_length, 2),
                         'right_shoulder_to_elbow': round(self._calculated_right_shoulder_to_elbow, 2),
                         'left_shoulder_to_elbow': round(self._calculated_left_shoulder_to_elbow, 2),
                         'right_thigh': round(self._calculated_right_thigh, 2), 'left_thigh': round(self._calculated_left_thigh, 2)}

    def calculate_BMI(self, weight):
        if self._calculated_height < 0:
            raise ValueError("Error: couldn't calculate BMI before calculating height")
        else:
            # BMI Score = weight / (height^2)
            self._calculated_BMI_score = weight / (pow(self._calculated_height, 2))
            self._results['bmi_score'] = round(self._calculated_BMI_score, 2)
            self._results['weight'] = round(weight, 2)

    def save_process_results(self):
        sql_connector = SQLConnector()
        sql_connector.save_scan_results(self._frame_name, self._results)
