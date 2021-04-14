import argparse
import better_exceptions
from pathlib import Path
from contextlib import contextmanager
import urllib.request
import numpy as np
import cv2
import dlib
import torch
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim
import torch.utils.data
import torch.nn.functional as F
from model import get_model
from defaults import _C as cfg


class AgeEstimation:
    def __init__(self, model_path):
        self.__model = get_model(model_name=cfg.MODEL.ARCH, pretrained=None)
        checkpoint = torch.load(model_path, map_location="cpu")
        self.__model.load_state_dict(checkpoint['state_dict'])
        print("=> loaded checkpoint '{}'".format(model_path))
        self.__model.eval()
        self.__margin = 0.4
        self.__detector = dlib.get_frontal_face_detector()
        self.__img_size = cfg.MODEL.IMG_SIZE
        self.__device = "cuda" if torch.cuda.is_available() else "cpu"

    def draw_label(self, image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.8, thickness=1):
        size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        x, y = point
        cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (255, 0, 0), cv2.FILLED)
        cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness, lineType=cv2.LINE_AA)

    def predict_age(self, img):
        with torch.no_grad():
            img = cv2.imread(img)
            input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_h, img_w, _ = np.shape(input_img)

            # detect faces using dlib detector
            detected = self.__detector(input_img, 1)
            faces = np.empty((len(detected), self.__img_size, self.__img_size, 3))

            if len(detected) > 0:
                for i, d in enumerate(detected):
                    x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
                    xw1 = max(int(x1 - self.__margin * w), 0)
                    yw1 = max(int(y1 - self.__margin * h), 0)
                    xw2 = min(int(x2 + self.__margin * w), img_w - 1)
                    yw2 = min(int(y2 + self.__margin * h), img_h - 1)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
                    cv2.rectangle(img, (xw1, yw1), (xw2, yw2), (255, 0, 0), 2)
                    faces[i] = cv2.resize(img[yw1:yw2 + 1, xw1:xw2 + 1], (self.__img_size, self.__img_size))

                # predict ages
                inputs = torch.from_numpy(np.transpose(faces.astype(np.float32), (0, 3, 1, 2))).to(self.__device)
                outputs = F.softmax(self.__model(inputs), dim=-1).cpu().numpy()
                ages = np.arange(0, 101)
                predicted_ages = (outputs * ages).sum(axis=-1)

                # draw results
                for i, d in enumerate(detected):
                    label = "{}".format(int(predicted_ages[i]))
                    self.draw_label(img, (d.left(), d.top()), label)

                cv2.imshow("result", img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()




### test !!

# def main():
#     a = AgeEstimation("./misc/epoch044_0.02343_3.9984.pth")
#     a.predict_age("../images/4.jpeg")
#
#
# if __name__ == '__main__':
#     main()
