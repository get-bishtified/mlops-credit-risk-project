from flask import Flask, request
import joblib
import numpy as np

app = Flask(__name__)

# Load model (SageMaker downloads it to /opt/ml/model)
model = joblib.load('/opt/ml/model/model.joblib')

@app.route('/invocations', methods=['POST'])
def invocations():
    # Expect CSV input: "value1,value2,..."
    csv_data = request.data.decode('utf-8')
    features = [float(x) for x in csv_data.split(',')]
    prediction = model.predict(np.array([features]))
    return str(float(prediction[0]))

@app.route('/ping', methods=['GET'])
def ping():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)