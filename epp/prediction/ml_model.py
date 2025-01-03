def predict_productivity(data):
    try:
        # Simulate a prediction with dummy data
        experience = data.get('experience', 0)
        hours_worked = data.get('hours_worked', 0)

        # Return dummy productivity score
        return f"Dummy prediction for experience={experience}, hours_worked={hours_worked}: 85.0"
    except Exception as e:
        return f"Error: {str(e)}"
