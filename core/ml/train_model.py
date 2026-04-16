import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

# 🔥 Dataset realista (debes mejorar esto con logs reales)
data = [
    [120, 1, 1, 0, 0, 1, 1],
    [80, 0, 0, 1, 0, 0, 0],
    [200, 3, 2, 0, 0, 1, 2],
    [50, 0, 0, 0, 1, 0, 0],
]

X = np.array(data)

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

model.fit(X)

joblib.dump(model, "core/ml/model.pkl")

print("✅ Modelo entrenado y guardado")