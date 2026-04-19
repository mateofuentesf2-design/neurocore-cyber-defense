import numpy as np
import joblib
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from core.ml.feature_engineering import extract_features as extract_ml_features
from core.db import execute_query, execute_insert, get_connection

MODEL_PATH = "core/ml/model.pkl"
SCALER_PATH = "core/ml/scaler.pkl"
FEATURES_COUNT = 8
RETRAIN_THRESHOLD = 100  # Retrain after collecting 100 new samples

class AnomalyDetector:
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self._load_or_create_model()
        self._ensure_tables_exist()
        
    def _load_or_create_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                print("✅ ML model loaded from disk")
                return
            except Exception as e:
                print(f"⚠️ Error loading model: {e}")
        
        print("🔄 Creating new ML model")
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self._train_initial()
    
    def _ensure_tables_exist(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    features TEXT NOT NULL,
                    label INTEGER NOT NULL,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass  # Table already exists or DB not ready
    
    def _train_initial(self):
        # Generate diverse training data
        X_normal = []
        X_anomaly = []
        
        # Normal traffic patterns
        for _ in range(300):
            features = [
                np.random.randint(50, 200),      # length
                np.random.randint(0, 3),         # error count
                np.random.randint(0, 2),         # failed count
                np.random.randint(5, 25),        # get count
                np.random.randint(0, 15),        # post count
                np.random.randint(0, 5),         # special chars
                np.random.randint(0, 10),        # numbers
                np.random.randint(0, 8)          # spaces
            ]
            X_normal.append(features)
        
        # Anomalous patterns (attacks, scans, etc.)
        for _ in range(100):
            features = [
                np.random.randint(200, 1000),    # length (longer)
                np.random.randint(5, 20),        # error count (high)
                np.random.randint(3, 15),        # failed count (high)
                np.random.randint(0, 5),         # get count (low)
                np.random.randint(0, 3),         # post count (low)
                np.random.randint(10, 30),       # special chars (high)
                np.random.randint(15, 40),       # numbers (high)
                np.random.randint(20, 50)        # spaces (high)
            ]
            X_anomaly.append(features)
        
        # Combine and label: -1 for anomaly, 1 for normal
        X = np.array(X_normal + X_anomaly)
        y = np.array([1] * len(X_normal) + [-1] * len(X_anomaly))
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        
        # Save initial model
        self._save_model()
        print("✅ Initial ML model trained and saved")
    
    def _save_model(self):
        try:
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump(self.model, MODEL_PATH)
            joblib.dump(self.scaler, SCALER_PATH)
        except Exception as e:
            print(f"⚠️ Error saving model: {e}")
    
    def extract_features_from_event(self, event: dict) -> List[float]:
        raw = event.get("raw", "").lower()
        
        # Basic features
        length = len(raw)
        error_count = raw.count("error") + raw.count("fail") + raw.count("denied")
        failed_count = raw.count("failed") + raw.count("denied") + raw.count("invalid")
        get_count = raw.count("get")
        post_count = raw.count("post")
        special_chars = sum(raw.count(c) for c in ['<', '>', '\"', "'", ';', '(', ')', '&', '|'])
        numbers = sum(raw.count(str(i)) for i in range(10))
        spaces = raw.count(' ')
        
        return [
            float(length),
            float(error_count),
            float(failed_count),
            float(get_count),
            float(post_count),
            float(special_chars),
            float(numbers),
            float(spaces)
        ]
    
    def predict(self, features: List[float]) -> bool:
        if len(features) != FEATURES_COUNT:
            # Fallback to basic extraction if needed
            if isinstance(features, dict):
                features = self.extract_features_from_event(features)
            else:
                features = [float(x) for x in features[:FEATURES_COUNT]]
                while len(features) < FEATURES_COUNT:
                    features.append(0.0)
        
        try:
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scaler.transform(X)
            prediction = self.model.predict(X_scaled)[0]
            return prediction == -1  # -1 means anomaly
        except Exception as e:
            print(f"⚠️ ML prediction error: {e}")
            return False
    
    def add_training_sample(self, features: List[float], label: int, source: str = "unknown"):
        """Add a new training sample for continuous learning"""
        try:
            features_str = json.dumps(features)
            execute_insert(
                "INSERT INTO ml_training_data (features, label, source) VALUES (?, ?, ?)",
                (features_str, label, source)
            )
            
            # Check if we need to retrain
            self._check_retrain()
        except Exception as e:
            print(f"⚠️ Error adding training sample: {e}")
    
    def _check_retrain(self):
        """Check if we have enough new samples to retrain"""
        try:
            count = execute_query(
                "SELECT COUNT(*) FROM ml_training_data WHERE created_at > datetime('now', '-1 hour')"
            )[0][0]
            
            if count >= RETRAIN_THRESHOLD:
                print("🔄 Retraining ML model with new data...")
                self._retrain_with_new_data()
        except:
            pass  # Ignore errors in retraining check
    
    def _retrain_with_new_data(self):
        """Retrain model with recent data"""
        try:
            # Get recent training data
            rows = execute_query("""
                SELECT features, label FROM ml_training_data 
                ORDER BY created_at DESC LIMIT 1000
            """)
            
            if len(rows) < 10:
                return
            
            X = []
            y = []
            
            for features_str, label in rows:
                try:
                    features = json.loads(features_str)
                    if len(features) == FEATURES_COUNT:
                        X.append(features)
                        y.append(label)
                except:
                    continue
            
            if len(X) < 10:
                return
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale and train
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)
            
            # Save updated model
            self._save_model()
            print(f"✅ ML model retrained with {len(X)} samples")
            
        except Exception as e:
            print(f"⚠️ Error during retraining: {e}")

# Global instance
detector = AnomalyDetector()

def predict_anomaly(features_or_event) -> bool:
    """Convenience function for anomaly detection"""
    return detector.predict(features_or_event)

def add_training_sample(features, label: int, source: str = "unknown"):
    """Add training sample for continuous learning"""
    detector.add_training_sample(features, label, source)