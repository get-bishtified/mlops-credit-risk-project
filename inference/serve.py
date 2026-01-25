import joblib
import numpy as np

def model_fn(model_dir):
    return joblib.load(f"{model_dir}/model.joblib")

def input_fn(input_data, content_type):
    if content_type == "text/csv":
        values = [float(x) for x in input_data.decode("utf-8").split(",")]
        return np.array([values])
    raise ValueError("Unsupported content type")

def predict_fn(data, model):
    return model.predict(data)

def output_fn(prediction, accept):
    return str(float(prediction[0])), "text/plain"
