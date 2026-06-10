import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

os.makedirs("models", exist_ok=True)

# ── 1. K-MEANS ──────────────────────────────────────────────
print("Training K-Means...")
df_km = pd.read_csv("datasets/Sleep_health_and_lifestyle_dataset_k-means_.csv")

le_bmi = LabelEncoder()
df_km["BMI_encoded"] = le_bmi.fit_transform(df_km["BMI Category"])

features_km = ["Sleep Duration", "Stress Level", "BMI_encoded", "Daily Steps"]
X_km = df_km[features_km]

scaler = StandardScaler()
X_km_scaled = scaler.fit_transform(X_km)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(X_km_scaled)

cluster_labels = {0: "Healthy Lifestyle", 1: "Moderate Risk", 2: "High Risk"}
joblib.dump(kmeans, "models/kmeans_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(le_bmi, "models/le_bmi.pkl")
print("K-Means done.")

# ── 2. RANDOM FOREST ────────────────────────────────────────
print("\nTraining Random Forest...")
df_rf = pd.read_csv("datasets/Sleep_health_and_lifestyle_dataset_RF_.csv")
df_rf = df_rf.drop(columns=["Blood Pressure"])

le_gender = LabelEncoder()
df_rf["Gender"] = le_gender.fit_transform(df_rf["Gender"])

le_target = LabelEncoder()
df_rf["BMI_label"] = le_target.fit_transform(df_rf["BMI Category"])

features_rf = ["Gender", "Age", "Sleep Duration", "Quality of Sleep",
               "Physical Activity Level", "Stress Level", "Heart Rate", "Daily Steps"]
X_rf = df_rf[features_rf]
y_rf = df_rf["BMI_label"]

X_train, X_test, y_train, y_test = train_test_split(X_rf, y_rf, test_size=0.2, random_state=42)
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

preds = rf.predict(X_test)
print(f"RF Accuracy: {accuracy_score(y_test, preds):.3f}")
print(classification_report(y_test, preds, target_names=le_target.classes_))

joblib.dump(rf,        "models/rf_model.pkl")
joblib.dump(le_gender, "models/le_gender.pkl")
joblib.dump(le_target, "models/le_target.pkl")
print("Random Forest saved.")

# ── 3. KNN ──────────────────────────────────────────────────
print("\nTraining KNN...")
df_diet = pd.read_csv("datasets/final_diet_meal_data.csv")

le_meal = LabelEncoder()
le_goal = LabelEncoder()
df_diet["Meal_encoded"] = le_meal.fit_transform(df_diet["Meal_Type"])
df_diet["Goal_encoded"] = le_goal.fit_transform(df_diet["Goal"])

features_knn = ["Meal_encoded", "Calories", "Proteins", "Carbs", "Fats"]
X_knn = df_diet[features_knn]
y_knn = df_diet["Goal_encoded"]

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_knn, y_knn)

joblib.dump(knn,     "models/knn_model.pkl")
joblib.dump(le_meal, "models/le_meal.pkl")
joblib.dump(le_goal, "models/le_goal.pkl")
joblib.dump(df_diet, "models/diet_data.pkl")
print("KNN saved.")

print("\n✅ All models trained and saved in models/ folder.")
