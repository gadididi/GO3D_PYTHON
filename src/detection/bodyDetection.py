import cv2
import matplotlib
import numpy as np
from tensorflow.keras.models import load_model

matplotlib.use("TkAgg")


class HumanPartSegmentationDetector:
    def __init__(self, model_path_segmentation, caffe_path_model, cfg_caffe_path):
        self.__model_seg = load_model(model_path_segmentation)
        self.__size_of_img = 256
        self.__num_of_class = 7
        self.__caffe_model_net = cv2.dnn.readNetFromCaffe(cfg_caffe_path, caffe_path_model)
        self.__threshold = 0.1
        self.__nPoints = 15
        self.POSE_PAIRS = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 5], [5, 6], [6, 7], [1, 14], [14, 8], [8, 9], [9, 10],
                           [14, 11],
                           [11, 12], [12, 13]]

        self.body_parts_caffe = {'left_shoulder': 2, 'right_shoulder': 5, 'right_abdomen': 11, 'left_abdomen': 8,
                                 'left_elbow': 3, 'right_elbow': 6, 'left_arm': 4, 'right_arm': 7,
                                 'left_knee': 9, 'right_knee': 12, 'chest_center': 1, 'left_ankle': 10,
                                 'right_ankle': 13, 'head': 0}
        self.body_part_seg = {'shoulder_line_class': 4, 'abdomen_line_class': 5}

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

        # For show seg image remove the comment below

        # plt.figure(1)
        # plt.imshow(seg_img)
        # plt.show(block=False)
        # plt.pause(0.05)
        # plt.clf()
        return seg_img

    def find_body_part(self, body_points, segmentation_image):
        """
        find_body_part run over body parts and measure the distance between them.
        :param body_points: point of body part detected before
        :param segmentation_image:
        :return:
        """
        print("start the measuring....")
        body_parts = {}
        shoulders = self.find_shoulders_point(body_points, segmentation_image)
        abdomen = self.find_abdomen_point(body_points)
        chest = self.find_chest_point(body_points)
        knees = self.find_knee_point(body_points)
        arms = self.find_arms_point(body_points)
        elbows = self.find_elbow_point(body_points)
        ankles = self.find_ankle_point(body_points)
        head = self.find_head_point(body_points)

        if shoulders is not None:
            body_parts['shoulders'] = shoulders

        if abdomen is not None:
            body_parts['abdomen'] = abdomen

        if chest is not None:
            body_parts['chest'] = chest

        if knees is not None:
            body_parts['knees'] = knees

        if arms is not None:
            body_parts['arms'] = arms

        if elbows is not None:
            body_parts['elbows'] = elbows

        if ankles is not None:
            body_parts['ankles'] = ankles

        if head is not None:
            body_parts['head'] = head

        return body_parts

    def find_ankle_point(self, body_points):
        if self.body_parts_caffe['left_ankle'] in body_points and self.body_parts_caffe['right_ankle'] in body_points:
            left_ankle = body_points[self.body_parts_caffe['left_ankle']]
            right_ankle = body_points[self.body_parts_caffe['right_ankle']]
            return left_ankle, right_ankle

    def find_knee_point(self, body_points):
        if self.body_parts_caffe['left_knee'] in body_points and self.body_parts_caffe['right_knee'] in body_points:
            left_knee = body_points[self.body_parts_caffe['left_knee']]
            right_knee = body_points[self.body_parts_caffe['right_knee']]
            return left_knee, right_knee

    def find_elbow_point(self, body_points):
        if self.body_parts_caffe['left_elbow'] in body_points and self.body_parts_caffe['right_elbow'] in body_points:
            left_elbow = body_points[self.body_parts_caffe['left_elbow']]
            right_elbow = body_points[self.body_parts_caffe['right_elbow']]
            return left_elbow, right_elbow

    def find_arms_point(self, body_points):
        if self.body_parts_caffe['left_arm'] in body_points and self.body_parts_caffe['right_arm'] in body_points:
            left_arm = body_points[self.body_parts_caffe['left_arm']]
            right_arm = body_points[self.body_parts_caffe['right_arm']]
            return left_arm, right_arm

    def find_chest_point(self, body_points):
        if self.body_parts_caffe['chest_center'] in body_points:
            return body_points[self.body_parts_caffe['chest_center']]

    def find_head_point(self, body_points):
        if self.body_parts_caffe['head'] in body_points:
            return body_points[self.body_parts_caffe['head']]

    def find_shoulders_point(self, body_points, segmentation_image):
        if self.body_parts_caffe['left_shoulder'] in body_points and self.body_parts_caffe['right_shoulder'] in body_points:
            left_s = body_points[self.body_parts_caffe['left_shoulder']]
            right_s = body_points[self.body_parts_caffe['right_shoulder']]
            line_shoulder = segmentation_image[left_s[1]]
            l_tmp = np.where(line_shoulder == self.body_part_seg['shoulder_line_class'])
            left_s_new = l_tmp[0].min()
            right_s_new = l_tmp[0].max()
            return (left_s_new, left_s[1]), (right_s_new, right_s[1])

    def find_abdomen_point(self, body_points):
        if self.body_parts_caffe['left_abdomen'] in body_points and self.body_parts_caffe['right_abdomen'] in body_points:
            left_ab = body_points[self.body_parts_caffe['left_abdomen']]
            right_ab = body_points[self.body_parts_caffe['right_abdomen']]
            return left_ab, right_ab

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

    def find_body_points(self, path):
        frame = cv2.imread(path)
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
        # self.draw_skeleton(points, frameCopy, frame)
        segmentation_image = self.detect(frame)
        return self.find_body_part(body_points, segmentation_image)
