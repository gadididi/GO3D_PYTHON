import threading

from src.flowManager.bmiexplanationgenerator import BMIExplanationGenerator
from src.flowManager.frameproccessor import FrameProcessor
from src.flowManager.mlconfig import MLConfig
from src.frameSaver import saveframe
from src.frameTaker.takeframe import FrameTaker


class FlowManager:

    def __init__(self):
        self._frameTaker = FrameTaker()
        self._ML_config = MLConfig()
        self._bmi_explanation_generator = BMIExplanationGenerator()
        self._frame_processor = None

    def start_scan_stream(self):
        print("start scan")
        if not self._frameTaker.is_healthy():
            th = threading.Thread(target=self._frameTaker.start_stream)
            th.start()

    def get_and_save_scan_saved_frames(self, file_name):
        if self._frameTaker.is_healthy():
            return saveframe.save_frames_to_file_system(self._frameTaker.get_frame_cache(), file_name)
        else:
            raise RuntimeError("The camera connection is not healthy, please check camera L515")

    def take_snapshot(self):
        if self._frameTaker.is_healthy():
            self._frameTaker.take_snapshot()
        else:
            raise RuntimeError("The camera connection is not healthy, please check camera L515")

    def process_frames(self, file_name, weight):

        try:
            frame_processor = FrameProcessor(file_name, self._ML_config)
            frame_processor.start_processing()
            frame_processor.calculate_BMI(weight)
            results = frame_processor.get_results()
            frame_processor.save_process_results()
            return results
        except KeyError:
            raise RuntimeError("process frames Failed, probably in detection body part section")

    def exit_scan(self):
        if self._frameTaker.is_healthy():
            self._frameTaker.exit_scan()
        else:
            raise RuntimeError("The camera connection is not healthy, please check camera L515")

    def get_last_image(self):
        if self._frameTaker.is_healthy():
            return self._frameTaker.get_last_image()
        else:
            raise RuntimeError("The camera connection is not healthy, please check camera L515")

    def clear_cache(self):
        self._frameTaker.reset_cache()

    def generate_bmi_explanation(self, bmi_score):
        return self._bmi_explanation_generator.generate_explanation(bmi_score)
