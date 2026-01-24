import joblib
import json
import numpy as np

model = joblib.load("model.joblib")

def handler(event, context=None):
    data = np.array(event["features"]).reshape(1, -1)
    pred = model.predict(data)
    return {"prediction": int(pred[0])}