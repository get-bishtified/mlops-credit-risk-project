import argparse
import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import joblib

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="/opt/ml/input/data/train")
    args = parser.parse_args()

    data_path = os.path.join(args.data_dir, "data.csv")
    if not os.path.exists(data_path):
        raise RuntimeError(f"Training data not found at {data_path}")

    df = pd.read_csv(data_path)

    # Example schema assumption:
    # last column = target
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    preds = model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, preds)
    print("Validation AUC:", auc)

    model_dir = "/opt/ml/model"
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "model.joblib")
    joblib.dump(model, model_path)

    print("Model saved to:", model_path)

if __name__ == "__main__":
    main()
