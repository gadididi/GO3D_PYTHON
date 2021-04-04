from src.detection.bodyDetection import HumanPartSegmentationDetector

test = HumanPartSegmentationDetector("models/enet256_weight0501.hdf5", "models/pose_iter_440000.caffemodel",
                                     "models/pose_deploy_linevec.prototxt")

shoulders = test.find_body_points("images/1.jpg")
print(shoulders)
