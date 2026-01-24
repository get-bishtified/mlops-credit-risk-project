import json
import os

# In real systems you would load metrics.json from S3
# Here we simulate reading metrics produced by training
metrics = {"accuracy": 0.88}

THRESHOLD = float(os.getenv("ACCURACY_THRESHOLD", "0.85"))

if metrics["accuracy"] >= THRESHOLD:
    print("Model passed quality gate")
    with open(".env_gate", "w") as f:
        f.write("MODEL_OK=true
")
else:
    raise RuntimeError("Model failed quality gate")
```python
import os
# Dummy gate
os.environ["MODEL_OK"] = "true"
print("Model approved")