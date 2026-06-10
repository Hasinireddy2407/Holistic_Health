def get_sleep_tips(sleep_hours):
    if sleep_hours < 6:
        return [
            "You are severely sleep deprived — aim for 7–9 hours.",
            "Avoid screens at least 1 hour before bed.",
            "Fix a consistent sleep and wake-up time every day.",
            "Avoid caffeine after 3 PM."
        ]
    elif sleep_hours < 7:
        return [
            "You need slightly more sleep — target 7–8 hours.",
            "Try a 10-minute wind-down routine before bed.",
            "Keep your bedroom cool and dark."
        ]
    return [
        "Your sleep duration is healthy — maintain this routine.",
        "Consistency is key — keep the same sleep schedule on weekends too."
    ]

def get_stress_tips(stress_level):
    if stress_level >= 8:
        return [
            "Critical stress level — consider speaking to a counselor.",
            "Practice 10 minutes of meditation daily.",
            "Try box breathing: inhale 4s, hold 4s, exhale 4s.",
            "Take short breaks every hour and reduce screen time."
        ]
    elif stress_level >= 5:
        return [
            "Moderate stress detected — try yoga or light stretching.",
            "Journal your thoughts for 5 minutes each morning.",
            "A 20-minute walk in natural light can significantly reduce stress."
        ]
    return [
        "Stress levels are well managed — great job!",
        "Keep up your current relaxation habits."
    ]

def get_mood_tips(mood):
    tips = {
        "sad": [
            "Try mood-boosting foods: dark chocolate, bananas, walnuts.",
            "Get at least 20 minutes of sunlight exposure today.",
            "Reach out to a friend or family member for a chat."
        ],
        "anxious": [
            "Avoid caffeine when feeling anxious.",
            "Try progressive muscle relaxation — tense and release each muscle group.",
            "Eat magnesium-rich foods: spinach, almonds, avocado."
        ],
        "tired": [
            "Eat iron-rich foods: lentils, spinach, beans.",
            "Stay hydrated — drink at least 8 glasses of water.",
            "A 20-minute power nap between 1–3 PM can restore energy."
        ],
        "happy": [
            "Great mood! Maintain it with regular exercise.",
            "Keep eating a balanced, colourful diet.",
            "Use this energy to build a positive habit today."
        ],
        "neutral": [
            "Stay consistent with your health habits.",
            "Try something new today — a new fruit, recipe, or walking route.",
            "A 15-minute stretch session can improve your mood naturally."
        ]
    }
    return tips.get(mood.lower(), ["Stay positive and keep going!"])

def get_workout_suggestion(bmi_category, workout_type):
    suggestions = {
        "Obese":         "Start with 30 min daily walking. Low-impact cardio only. Avoid joint strain.",
        "Overweight":    "Cardio 4×/week + light strength training. Avoid heavy lifts initially.",
        "Normal Weight": "Maintain with 3–4×/week mixed training. You have flexibility to try any style.",
        "Underweight":   "Focus on Strength training 4×/week with a high-calorie, high-protein diet.",
        "Normal":        "Maintain with 3–4×/week mixed training."
    }
    base = suggestions.get(bmi_category, "Stay active with moderate exercise.")
    return f"{base} Recommended workout style: {workout_type}."
