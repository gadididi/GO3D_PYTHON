from src.detection.bodyDetection import HumanPartSegmentationDetector


class MLConfig:
    def __init__(self):
        # init the file locations for the model, caffe model and pose deploy file
        self._model = "detection/models/enet256_weight0501.hdf5"
        self._caffe_model = "detection/models/pose_iter_440000.caffemodel"
        self._pose_deploy = "detection/models/pose_deploy_linevec.prototxt"
        self._human_part_detector = HumanPartSegmentationDetector(self._model, self._caffe_model, self._pose_deploy)

    def get_human_parts_detector(self):
        return self._human_part_detector
