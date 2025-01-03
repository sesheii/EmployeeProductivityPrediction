from django.shortcuts import render


def prediction_view(request):
    # Example list of features
    features = ["experience", "hours_worked", "projects_completed", "overtime_hours"]

    result = None  # Default result

    if request.method == "POST":
        # Process submitted form data
        form_data = {feature: request.POST.get(feature) for feature in features}
        # Call your prediction model with `form_data`
        # For example: result = predict(form_data)
        result = f"Predicted Value (Example): {form_data}"  # Example placeholder

    return render(request, "predict.html", {"features": features, "result": result})
