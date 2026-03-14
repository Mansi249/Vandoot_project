import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# 1. Load the synthetic dataset you just created
df = pd.read_csv('sensor_data_v2.csv')

# 2. Define Features (X) and Target (y)
# We drop 'Label' because that's what we want to predict
X = df.drop('Label', axis=1)
y = df['Label']

# 3. Split data: 80% for training, 20% for testing the accuracy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize the Random Forest
# We use 100 trees to ensure redundancy if a sensor fails
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)

# 5. Train the "Judge"
model.fit(X_train, y_train)

# 6. Evaluate: How smart is our model?
y_pred = model.predict(X_test)
print(f"Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print("\nDetailed Report:\n", classification_report(y_test, y_pred))

# 7. SAVE THE BRAIN
# This file 'vandoot_judge.pkl' is what goes on the Raspberry Pi
joblib.dump(model, 'vandoot_judge.pkl')
print("\nSuccess! 'vandoot_judge.pkl' is saved and ready for the Pi.")