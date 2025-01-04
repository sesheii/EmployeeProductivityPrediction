from django.shortcuts import render
import joblib
import pandas as pd
from django.conf import settings
import os

# Load the dataset to get feature names
dataset_path = os.path.join(settings.BASE_DIR, "data", "HRDataset_v14.csv")  # Path to your dataset
df = pd.read_csv(dataset_path)
df = df.drop(["PerformanceScore"], axis=1)  # Assuming `PerformanceScore` is the target column
features = [
    'MarriedID', 'FromDiversityJobFairID', 'Salary', 'EngagementSurvey',
    'EmpSatisfaction', 'SpecialProjectsCount', 'DaysLateLast30', 'Absences',
    'Age', 'Position_encoded', 'State_encoded', 'Sex_encoded',
    'MaritalDesc_encoded', 'CitizenDesc_encoded', 'HispanicLatino_encoded',
    'RaceDesc_encoded', 'Department_encoded', 'ManagerName_encoded',
    'RecruitmentSource_encoded'
]

# Dictionary of available models with their file paths
model_paths = {
    "Decision Tree": os.path.join(settings.BASE_DIR, "dump", "DecisionTreeClassifier.pkl"),
    "K-Nearest Neighbors": os.path.join(settings.BASE_DIR, "dump", "KNeighborsClassifier.pkl"),
    "Logistic Regression": os.path.join(settings.BASE_DIR, "dump", "LogisticRegression.pkl"),
    "Random Forest": os.path.join(settings.BASE_DIR, "dump", "RandomForestClassifier.pkl"),
    "Stacking Classifier": os.path.join(settings.BASE_DIR, "dump", "StackingClassifier.pkl"),
}

# Load models dynamically
models = {}
for name, path in model_paths.items():
    try:
        models[name] = joblib.load(path)
    except FileNotFoundError:
        print(f"Error: {name} model file not found at {path}")


def prediction_view(request):
    predictions = {}  # To store predictions from each model
    input_data = {feature: "" for feature in features}  # Initialize with empty strings
    error_message = None  # Default error message

    if request.method == "POST":
        try:
            # Collect and validate form data
            for feature in features:
                value = request.POST.get(feature)
                if value is None or value.strip() == "":
                    raise ValueError(f"Missing value for {feature}")
                input_data[feature] = value  # Store the raw value for display

            # Convert input_data to float for predictions
            numeric_data = {feature: float(input_data[feature]) for feature in features}

            # Convert to DataFrame (single row)
            new_data = pd.DataFrame([numeric_data])

            # Generate predictions for each model
            for model_name, model in models.items():
                predictions[model_name] = model.predict(new_data)[0]

        except ValueError as e:
            error_message = str(e)
        except Exception as e:
            error_message = "An error occurred while processing your request. Please try again."

    return render(
        request,
        "predict.html",
        {
            "features": features,
            "predictions": predictions,
            "input_data": input_data,
            "error_message": error_message,
        },
    )
