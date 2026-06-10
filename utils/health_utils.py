def calculate_bmi(weight_kg, height_cm):
    h = height_cm / 100
    return round(weight_kg / (h ** 2), 1)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal Weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def calculate_bmr(weight, height_cm, age, gender):
    if gender == "Male":
        return round(88.362 + (13.397 * weight) + (4.799 * height_cm) - (5.677 * age), 1)
    else:
        return round(447.593 + (9.247 * weight) + (3.098 * height_cm) - (4.330 * age), 1)

def calculate_daily_calories(bmr, exercise_level):
    multipliers = {
        "sedentary":   1.2,
        "light":       1.375,
        "moderate":    1.55,
        "active":      1.725,
        "very_active": 1.9
    }
    return round(bmr * multipliers.get(exercise_level, 1.2), 1)

def calculate_water_intake(weight_kg, exercise_level):
    base = weight_kg * 0.033
    extra = {"moderate": 0.3, "active": 0.5, "very_active": 0.7}
    return round(base + extra.get(exercise_level, 0), 1)

def get_risk_level(bmi, sleep_hours, stress_level):
    score = 0
    if bmi >= 30 or bmi < 18.5: score += 3
    elif bmi >= 25:              score += 1
    if sleep_hours < 6:          score += 3
    elif sleep_hours < 7:        score += 1
    if stress_level >= 8:        score += 3
    elif stress_level >= 5:      score += 1
    if score >= 6:   return "High Risk"
    elif score >= 3: return "Moderate Risk"
    else:            return "Low Risk"

def calculate_health_score(bmi, sleep, stress, exercise, steps):
    score = 0
    # BMI (max 30)
    if 18.5 <= bmi <= 24.9:  score += 30
    elif 25 <= bmi <= 27:    score += 20
    elif bmi < 18.5:         score += 15
    else:                    score += 10
    # Sleep (max 25)
    if 7 <= sleep <= 9:      score += 25
    elif 6 <= sleep < 7:     score += 15
    else:                    score += 5
    # Stress (max 20) — lower is better
    score += max(0, 20 - (stress * 2))
    # Exercise (max 15)
    ex_map = {"sedentary": 0, "light": 5, "moderate": 10,
              "active": 13, "very_active": 15}
    score += ex_map.get(exercise, 5)
    # Steps (max 10)
    if steps >= 10000:       score += 10
    elif steps >= 7000:      score += 7
    elif steps >= 5000:      score += 4
    return min(score, 100)

def get_score_label(score):
    if score >= 80:   return "Excellent", "success"
    elif score >= 60: return "Good",      "primary"
    elif score >= 40: return "Fair",      "warning"
    else:             return "Poor",      "danger"
