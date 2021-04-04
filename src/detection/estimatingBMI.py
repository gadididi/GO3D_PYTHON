import numpy as np
import face_recognition
from sklearn.externals import joblib


def get_face_encoding(image_path):
    print(image_path)
    picture_of_me = face_recognition.load_image_file(image_path)
    my_face_encoding = face_recognition.face_encodings(picture_of_me)
    if not my_face_encoding:
        print("no face found !!!")
        return np.zeros(128).tolist()
    return my_face_encoding[0].tolist()


def predict_height_width_BMI(test_image, height_model, weight_model, bmi_model):
    test_array = np.expand_dims(np.array(get_face_encoding(test_image)), axis=0)
    height = np.asscalar(np.exp(height_model.predict(test_array)))
    weight = np.asscalar(np.exp(weight_model.predict(test_array)))
    bmi = np.asscalar(np.exp(bmi_model.predict(test_array)))
    return {'height': height, 'weight': weight, 'bmi': bmi}


height_model = './models/bmi_models/weight_predictor.model'
weight_model = './models/bmi_models/height_predictor.model'
bmi_model = './models/bmi_models/bmi_predictor.model'
height_model = joblib.load(height_model)
weight_model = joblib.load(weight_model)
bmi_model = joblib.load(bmi_model)
print(predict_height_width_BMI("./images/5.jpg", height_model, weight_model, bmi_model))
