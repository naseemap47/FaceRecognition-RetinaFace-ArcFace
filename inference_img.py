from keras.models import load_model
from mtcnn import MTCNN
from my_utils import alignment_procedure
from tensorflow.keras.preprocessing import image
import ArcFace
import cv2
import numpy as np
import pandas as pd
import argparse


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str, required=True,
                help="path to image")
ap.add_argument("-m", "--model", type=str, required=True,
                help="path to saved .h5 model, eg: dir/model.h5")

args = vars(ap.parse_args())
path_to_img = args["image"]
path_saved_model = args["model"]

# Load saved model
face_rec_model = load_model(path_saved_model, compile=True)

detector = MTCNN()

arcface_model = ArcFace.loadModel()
arcface_model.load_weights("arcface_weights.h5")
target_size = arcface_model.layers[0].input_shape[0][1:3]

class_names = ['Naseem', 'Vikas']

img = cv2.imread(path_to_img)
detections = detector.detect_faces(img)

if len(detections) > 0:
    for detect in detections:
        right_eye = detect['keypoints']['right_eye']
        left_eye = detect['keypoints']['left_eye']
        bbox = detect['box']
        norm_img_roi = alignment_procedure(img, left_eye, right_eye, bbox)

        img_resize = cv2.resize(norm_img_roi, target_size)
        # what this line doing? must?
        img_pixels = image.img_to_array(img_resize)
        img_pixels = np.expand_dims(img_pixels, axis=0)
        img_norm = img_pixels/255  # normalize input in [0, 1]
        img_embedding = arcface_model.predict(img_norm)[0]

        data = pd.DataFrame([img_embedding], columns=np.arange(512))

        predict = face_rec_model.predict(data)[0]
        print(predict)
        pose_class = class_names[predict.argmax()]

        # Show Result
        cv2.putText(
            img, f'{pose_class}',
            (40, 50), cv2.FONT_HERSHEY_PLAIN,
            2, (255, 0, 255), 2
        )

    cv2.imshow('Image', img)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
