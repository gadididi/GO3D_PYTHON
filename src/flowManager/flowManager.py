import threading

from src.frameSaver import saveframe
from src.frameTaker.takeframe import FrameTaker


class FlowManager:

    def __init__(self):
        self._frameTaker = FrameTaker()

    def start_scan_stream(self):
        th = threading.Thread(target=self._frameTaker.start_stream())
        th.start()

    def get_and_save_scan_saved_frames(self, file_name):
        return saveframe.save_frames_to_file_system(self._frameTaker.get_frame_cache(), file_name)

