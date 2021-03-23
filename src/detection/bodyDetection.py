import cv2
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from tensorflow.keras.models import load_model

matplotlib.use("TkAgg")


class HumanPartSegmentationDetector:
    def __init__(self, model_path_segmentation, caffe_path_model, cfg_caffe_path):
        self.__model_seg = load_model(model_path_segmentation)
        self.__size_of_img = 256
        self.__num_of_class = 7
        self.__caffe_model_net = cv2.dnn.readNetFromCaffe(cfg_caffe_path, caffe_path_model)
        self.__threshold = 0.2
        self.__nPoints = 15
        self.POSE_PAIRS = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 5], [5, 6], [6, 7], [1, 14], [14, 8], [8, 9], [9, 10],
                           [14, 11],
                           [11, 12], [12, 13]]

        self.body_parts = {'left_shoulder': 2, 'right_shoulder': 5}

    def detect(self, orig_img):
        # scale the img to 256*256*3 input for neural network
        bgr_img = cv2.resize(orig_img, (self.__size_of_img, self.__size_of_img))
        img = bgr_img[..., ::-1]
        img = img * (1 / 255.0)

        # Add batch dimension: 1 x D x D x 3
        img_tensor = np.expand_dims(img, 0)

        raw_output = self.__model_seg.predict(img_tensor)
        output = np.reshape(raw_output, (1, self.__size_of_img, self.__size_of_img, self.__num_of_class))

        # Get mask
        seg_labels = output[0, :, :, :]
        seg_img = np.argmax(seg_labels, axis=2)

        # Display
        seg_img = seg_img[:, :, np.newaxis]
        seg_img = np.array(seg_img, dtype='uint8')
        seg_img = cv2.resize(seg_img, (640, 480))
        plt.figure(1)
        plt.imshow(seg_img)
        plt.show(block=False)
        plt.pause(0.05)
        plt.clf()
        return seg_img

    def find_body_part(self, body_points, segmentation_image):
        """
        find_body_part run over body parts and measure the distance between them.
        :param body_points: point of body part detected before
        :param segmentation_image:
        :return:
        """
        print("start the measuring....")
        self.find_shoulders_point(body_points, segmentation_image)

    def find_shoulders_point(self, body_points, segmentation_image):
        if self.body_parts['left_shoulder'] in body_points and self.body_parts['right_shoulder']:
            left_s = body_points[self.body_parts['left_shoulder']]
            right_s = body_points[self.body_parts['right_shoulder']]
            print("hhh")




    def draw_skeleton(self, points, frameCopy, frame):
        # Draw Skeleton
        for triple in self.POSE_PAIRS:
            partA = triple[0]
            partB = triple[1]

            if points[partA] and points[partB]:
                a = (points[partA][0], points[partA][1])
                b = (points[partB][0], points[partB][1])
                cv2.line(frame, a, b, (0, 255, 255), 3)

        cv2.imshow("after", frameCopy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # TODO: CHANGE X TO ND-ARRAY
    def find_body_points(self, x):
        frame = cv2.imread(x)
        frameCopy = np.copy(frame)
        frameWidth = frame.shape[1]
        frameHeight = frame.shape[0]

        net = self.__caffe_model_net

        inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (frameWidth, frameHeight),
                                        (0, 0, 0), swapRB=False, crop=False)

        net.setInput(inpBlob)

        output = net.forward()
        H = output.shape[2]
        W = output.shape[3]

        # Empty list to store the detected keypoints
        points = []
        body_points = {}
        for i in range(self.__nPoints):
            # confidence map of corresponding body's part.
            probMap = output[0, i, :, :]

            # Find global maxima of the probMap.
            minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

            # Scale the point to fit on the original image
            x = (frameWidth * point[0]) / W
            y = (frameHeight * point[1]) / H

            if prob > self.__threshold:
                cv2.circle(frameCopy, (int(x), int(y)), 1, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
                cv2.putText(frameCopy, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                            lineType=cv2.LINE_AA)
                cv2.circle(frame, (int(x), int(y)), 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

                # Add the point to the list if the probability is greater than the threshold
                points.append((int(x), int(y), i))
                body_points[i] = (int(x), int(y))
            else:
                points.append(None)

        # if you want to see the skeleton body remove the comment below
        self.draw_skeleton(points, frameCopy, frame)
        segmentation_image = self.detect(frame)
        self.find_body_part(body_points, segmentation_image)


d = HumanPartSegmentationDetector("./models/enet256_weight0501.hdf5", "./models/pose_iter_440000.caffemodel",
                                  "./models/pose_deploy_linevec.prototxt")
d.find_body_points("./images/2.jpg")
