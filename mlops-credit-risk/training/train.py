import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# SageMaker paths
data_path = "/opt/ml/input/data/train/data.csv"
model_path = "/opt/ml/model/model.joblib"

# Load data
df = pd.read_csv(data_path)
X = df.drop("default", axis=1)
y = df["default"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)

pred = model.predict(X_test)
acc = accuracy_score(y_test, pred)
print("Accuracy:", acc)

joblib.dump(model, model_path)