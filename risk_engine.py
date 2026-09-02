def calculate_risk(symptoms):

    symptom_count = len(symptoms)

    if symptom_count >= 5:
        return "High"

    elif symptom_count >= 3:
        return "Medium"

    else:
        return "Low"