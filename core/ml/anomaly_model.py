import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
	
	def __init__(self):
		self.model = IsolationForest(contamination=0.1)
		self.trained = False
	
	def train(self, data):
		data = np.random.rand(100, 4)
		self.model.fit(data)
		self.trained = True
		
	def predict(self, sample):
		if not self.trained:
			self:train()
			
		result = self.model.predict([features])
		return result[0] == -1
		
