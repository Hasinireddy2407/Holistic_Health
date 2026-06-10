from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import joblib
from utils.health_utils import (
    calculate_bmi, get_bmi_category,
    calculate_bmr, calculate_daily_calories,
    calculate_water_intake, get_risk_level,
    calculate_health_score, get_score_label
)
from utils.rule_engine import (
    get_sleep_tips, get_stress_tips,
    get_mood_tips, get_workout_suggestion
)

app = Flask(__name__)

# ── Load all models once at startup ──────────────────────────
kmeans     = joblib.load("models/kmeans_model.pkl")
scaler     = joblib.load("models/scaler.pkl")
le_bmi     = joblib.load("models/le_bmi.pkl")
rf         = joblib.load("models/rf_model.pkl")
le_gender  = joblib.load("models/le_gender.pkl")
le_target  = joblib.load("models/le_target.pkl")
knn        = joblib.load("models/knn_model.pkl")
le_meal    = joblib.load("models/le_meal.pkl")
le_goal    = joblib.load("models/le_goal.pkl")
diet_df    = joblib.load("models/diet_data.pkl")
workout_df = pd.read_csv("datasets/workout_dataset.csv")

cluster_map = {0: "Healthy Lifestyle", 1: "Moderate Risk", 2: "High Risk"}


# ── Feature 4: Workout cards with calories + frequency ───────
def get_workout_recommendation(bmi, gender):
    bmi_cat  = get_bmi_category(bmi)

    # Assign workout type based on BMI
    if bmi >= 30:        wtype = "Cardio"
    elif bmi >= 25:      wtype = "HIIT"
    elif bmi < 18.5:     wtype = "Strength"
    else:                wtype = "Yoga"

    # Filter by gender first, fallback to all
    filtered = workout_df[workout_df["Gender"] == gender]
    if len(filtered) == 0:
        filtered = workout_df

    type_df = filtered[filtered["Workout_Type"] == wtype]

    # Group by exercise name → average calories burned + frequency
    grouped = (
        type_df.groupby("Name of Exercise")
        .agg(
            avg_calories=("Calories_Burned",            "mean"),
            avg_freq    =("Workout_Frequency (days/week)", "mean")
        )
        .reset_index()
        .sort_values("avg_calories", ascending=False)
        .head(6)
    )

    exercises = []
    for _, row in grouped.iterrows():
        exercises.append({
            "name":     row["Name of Exercise"],
            "calories": int(round(row["avg_calories"])),
            "freq":     round(row["avg_freq"], 1)
        })

    suggestion = get_workout_suggestion(bmi_cat, wtype)
    return suggestion, exercises, wtype, bmi_cat


# ── Diet recommendation via KNN filter ───────────────────────
def get_diet_recommendations(goal):
    goal_map = {"lose": "Lose", "maintain": "Maintain", "gain": "Gain"}
    mapped_goal = goal_map.get(goal.lower(), "Maintain")

    results = {}
    for meal in ["Breakfast", "Lunch", "Dinner"]:
        filtered = diet_df[
            (diet_df["Goal"]      == mapped_goal) &
            (diet_df["Meal_Type"] == meal)
        ]
        if len(filtered) == 0:
            filtered = diet_df[diet_df["Meal_Type"] == meal]
        sample = filtered.sample(min(3, len(filtered)), random_state=42).to_dict("records")
        results[meal] = sample
    return results


# ── Feature 6: Calorie gap ────────────────────────────────────
def get_calorie_gap(daily_calories, diet, goal):
    all_foods   = diet.get("Breakfast", []) + diet.get("Lunch", []) + diet.get("Dinner", [])
    plan_cals   = sum(f["Calories"] for f in all_foods) / max(len(all_foods), 1) * 3
    gap         = round(daily_calories - plan_cals, 0)

    if goal == "lose":
        if gap > 200:
            msg   = f"Your recommended meal plan is {int(gap)} kcal below your daily need — good deficit for weight loss."
            color = "success"
        elif gap < -200:
            msg   = f"Your meal plan exceeds your daily target by {int(abs(gap))} kcal — consider smaller portions."
            color = "warning"
        else:
            msg   = "Your meal plan calories align well with your weight loss target."
            color = "info"

    elif goal == "gain":
        if gap < -200:
            msg   = f"Your meal plan gives {int(abs(gap))} kcal above your daily need — good surplus for weight gain."
            color = "success"
        elif gap > 200:
            msg   = f"Add ~{int(gap)} more kcal to your meals daily to support weight gain effectively."
            color = "warning"
        else:
            msg   = "Your meal plan is close to your maintenance calories — add healthy snacks to gain."
            color = "info"

    else:  # maintain
        if abs(gap) <= 200:
            msg   = "Your meal plan calories match your daily maintenance requirement well."
            color = "success"
        else:
            msg   = f"Calorie gap of {int(abs(gap))} kcal detected — adjust portion sizes to stay on track."
            color = "warning"

    return msg, color, int(plan_cals)


# ── Routes ────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    # Form inputs
    name     = request.form.get("name", "User")
    age      = int(request.form["age"])
    gender   = request.form["gender"]
    height   = float(request.form["height"])
    weight   = float(request.form["weight"])
    sleep    = float(request.form["sleep"])
    stress   = int(request.form["stress"])
    mood     = request.form["mood"]
    exercise = request.form["exercise"]
    goal     = request.form["goal"]
    steps    = int(request.form.get("steps", 5000))

    # ── Basic calculations ──
    bmi      = calculate_bmi(weight, height)
    bmi_cat  = get_bmi_category(bmi)
    bmr      = calculate_bmr(weight, height, age, gender)
    calories = calculate_daily_calories(bmr, exercise)
    water    = calculate_water_intake(weight, exercise)
    risk     = get_risk_level(bmi, sleep, stress)

    # ── Health Score ──
    health_score              = calculate_health_score(bmi, sleep, stress, exercise, steps)
    score_label, score_color  = get_score_label(health_score)

    # ── K-Means: cluster user ──
    safe_bmi_cat = bmi_cat if bmi_cat in le_bmi.classes_ else "Normal Weight"
    bmi_enc      = le_bmi.transform([safe_bmi_cat])[0]
    km_input     = scaler.transform([[sleep, stress, bmi_enc, steps]])
    cluster_num  = kmeans.predict(km_input)[0]
    cluster_label = cluster_map.get(int(cluster_num), "Moderate Risk")

    # ── Random Forest: predict health condition ──
    gender_enc  = le_gender.transform([gender])[0]
    quality     = min(int(sleep), 9)
    activity_map = {"sedentary": 20, "light": 40, "moderate": 60,
                    "active": 80, "very_active": 90}
    activity    = activity_map.get(exercise, 50)
    rf_input    = [[gender_enc, age, sleep, quality, activity, stress, 75, steps]]
    rf_pred     = rf.predict(rf_input)[0]
    health_condition = le_target.inverse_transform([rf_pred])[0]

    # ── KNN: diet recommendations ──
    diet = get_diet_recommendations(goal)

    # ── Feature 4: Workout cards ──
    workout_tip, exercises, wtype, bmi_cat_label = get_workout_recommendation(bmi, gender)

    # ── Rule-based tips ──
    sleep_tips  = get_sleep_tips(sleep)
    stress_tips = get_stress_tips(stress)
    mood_tips   = get_mood_tips(mood)

    # ── Feature 6: Calorie gap ──
    calorie_msg, calorie_color, plan_cals = get_calorie_gap(calories, diet, goal)

    # ── Macro averages for pie chart ──
    all_foods    = diet.get("Breakfast", []) + diet.get("Lunch", []) + diet.get("Dinner", [])
    avg_carbs    = round(np.mean([f["Carbs"]    for f in all_foods]) if all_foods else 50, 1)
    avg_proteins = round(np.mean([f["Proteins"] for f in all_foods]) if all_foods else 25, 1)
    avg_fats     = round(np.mean([f["Fats"]     for f in all_foods]) if all_foods else 15, 1)

    return render_template("dashboard.html",
        # identity
        name=name, age=age, gender=gender,
        # health metrics
        bmi=bmi, bmi_cat=bmi_cat, bmr=bmr,
        calories=calories, water=water, risk=risk,
        health_score=health_score, score_label=score_label, score_color=score_color,
        # ML outputs
        cluster=cluster_label, health_condition=health_condition,
        # diet
        diet=diet,
        avg_carbs=avg_carbs, avg_proteins=avg_proteins, avg_fats=avg_fats,
        # feature 4: workout
        workout_tip=workout_tip, exercises=exercises,
        workout_type=wtype, bmi_cat_label=bmi_cat_label,
        # feature 6: calorie gap
        calorie_msg=calorie_msg, calorie_color=calorie_color, plan_cals=plan_cals,
        # lifestyle tips
        sleep_tips=sleep_tips, stress_tips=stress_tips,
        mood_tips=mood_tips, mood=mood,
        sleep=sleep, stress=stress, goal=goal, steps=steps, exercise=exercise
    )


if __name__ == "__main__":
    app.run(debug=True)
