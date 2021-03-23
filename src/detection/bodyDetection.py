import cv2
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from tensorflow.keras.models import load_model

matplotlib.use("TkAgg")


class HumanPartSegmentationDetector:
    def __init__(self, model_path):
        self.__model = load_model(model_path)
        self.__size_of_img = 256
        self.__num_of_class = 7

    # TODO: change path to ndarry in the future
    def detect(self, path_o_img):
        orig_img = cv2.imread(path_o_img, cv2.IMREAD_UNCHANGED)

        # scale the img to 256*256*3 input for neural network
        bgr_img = cv2.resize(orig_img, (256, 256))
        img = bgr_img[..., ::-1]
        img = img * (1 / 255.0)

        # Add batch dimension: 1 x D x D x 3
        img_tensor = np.expand_dims(img, 0)

        raw_output = self.__model.predict(img_tensor)
        output = np.reshape(raw_output, (1, self.__size_of_img, self.__size_of_img, self.__num_of_class))

        # Get mask
        seg_labels = output[0, :, :, :]
        seg_img = np.argmax(seg_labels, axis=2)

        # Display
        seg_img = seg_img[:, :, np.newaxis]
        seg_img = np.array(seg_img, dtype='uint8')
        seg_img = cv2.resize(seg_img, (640, 480))
        display_img = cv2.resize(bgr_img, (640, 480))
        plt.figure(1)
        plt.imshow(seg_img)
        plt.show(block=False)
        plt.pause(0.05)
        plt.clf()
        cv2.imshow('img', display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        self.find_body_part(seg_img)

    def find_body_part(self, image):
        ...


d = HumanPartSegmentationDetector("./models/enet256_weight0501.hdf5")
d.detect('./man2.jpg')
