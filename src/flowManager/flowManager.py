import threading

from src.flowManager.frameproccessor import FrameProcessor
from src.flowManager.mlconfig import MLConfig
from src.frameSaver import saveframe
from src.frameTaker.takeframe import FrameTaker


class FlowManager:

    def __init__(self):
        self._frameTaker = FrameTaker()
        self._ML_config = MLConfig()

    def start_scan_stream(self):
        th = threading.Thread(target=self._frameTaker.start_stream)
        th.start()

    def get_and_save_scan_saved_frames(self, file_name):
        return saveframe.save_frames_to_file_system(self._frameTaker.get_frame_cache(), file_name)

    def take_snapshot(self):
        self._frameTaker.take_snapshot()

    def process_frames(self, file_name):
        frame_processor = FrameProcessor(file_name, self._ML_config)
        frame_processor.start_processing()
        results = frame_processor.get_results()
        return results

    def exit_scan(self):
        self._frameTaker.exit_scan()

    def get_last_image(self):
        return self._frameTaker.get_last_image()

