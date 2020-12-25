import cv2
import numpy as np


class DetectPerson:
    def __init__(self):
        self.__path_weight = 'yolov3.weights'
        self.__path_cfg = 'yolov3.cfg'
        self.__classes_path = 'yolov3.txt'
        self.__classes = []
        self.init_classes()
        self.__net = cv2.dnn.readNet(self.__path_weight, self.__path_cfg)
        self.__layer_names = self.__net.getLayerNames()
        self.__output_layers = [self.__layer_names[i[0] - 1] for i in self.__net.getUnconnectedOutLayers()]

    def init_classes(self):
        f = open(self.__classes_path, 'r')
        self.__classes = [line.strip() for line in f.readlines()]

    def detect(self, image):
        # image = cv2.resize(image, None, fx=0.4, fy=0.4)
        # Detecting objects
        blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.__net.setInput(blob)
        outs = self.__net.forward(self.__output_layers)
        class_ids = []
        confidences = []
        boxes = []
        Width = image.shape[1]
        Height = image.shape[0]
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if class_id == 0 and confidence > 0.3:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])
                    break

        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.6, 0.6)
        # check if is people detection
        for i in indices:
            i = i[0]
            box = boxes[i]
            if class_ids[i] == 0:
                label = str(self.__classes[int(class_id)])
                cv2.rectangle(image, (round(box[0]), round(box[1])), (round(box[0] + box[2]), round(box[1] + box[3])),
                              (0, 0, 0), 2)
                cv2.putText(image, label, (round(box[0]) - 10, round(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 0), 2)
                break
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', image)
        cv2.waitKey(1)
        # cv2.destroyAllWindows()
