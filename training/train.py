import argparse
import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import joblib
import numpy as np

def main():
    parser = argparse.ArgumentParser()

    # SageMaker passes the channel name as a positional arg (e.g., "train")
    parser.add_argument("channel", nargs="?", default="train")

    # Optional override for local runs
    parser.add_argument("--data-dir", type=str)

    # Allow SageMaker's extra args without failing
    args, _ = parser.parse_known_args()

    # SageMaker mounts data at /opt/ml/input/data/<channel>/
    data_dir = args.data_dir or f"/opt/ml/input/data/{args.channel}"
    data_path = os.path.join(data_dir, "data.csv")

    if not os.path.exists(data_path):
        raise RuntimeError(f"Training data not found at {data_path}")

    df = pd.read_csv(data_path)

    # Assumption: last column is target, others are features
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    preds = model.predict_proba(X_val)[:, 1]

    # Guard AUC for small/skewed demo data
    if len(np.unique(y_val)) > 1:
        auc = roc_auc_score(y_val, preds)
        print("Validation AUC:", auc)
    else:
        print("WARNING: Only one class present in validation set. AUC not defined.")

    model_dir = "/opt/ml/model"
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "model.joblib")
    joblib.dump(model, model_path)

    print("Model saved to:", model_path)

if __name__ == "__main__":
    main()
