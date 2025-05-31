from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle
import numpy as np
import os

# 모델 저장 디렉토리 생성
os.makedirs('models', exist_ok=True)

# 데이터 로드
iris = load_iris()
X, y = iris.data, iris.target

# 학습/테스트 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 학습
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 모델 저장
model_info = {
    'model': model,
    'feature_names': iris.feature_names,
    'target_names': iris.target_names,
    'model_type': 'classification'
}

model_path = os.path.join('models', 'iris_model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model_info, f)

print(f"Model saved as {model_path}")
print("\nFeature names:", iris.feature_names)
print("Target names:", iris.target_names)
print("\nExample input format:")
print("sepal length (cm), sepal width (cm), petal length (cm), petal width (cm)")
print("Example: 5.1, 3.5, 1.4, 0.2") 