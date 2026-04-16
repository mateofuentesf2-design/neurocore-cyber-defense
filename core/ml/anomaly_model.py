import numpy as np
import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

model = joblib.load(MODEL_PATH)

def detect_anomaly(features):
    X = np.array(features).reshape(1, -1)

    prediction = model.predict(X)[0]

    return prediction == -1