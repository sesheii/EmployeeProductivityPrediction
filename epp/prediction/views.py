# from django.shortcuts import render
# import joblib
# import pandas as pd
# from sklearn.model_selection import KFold
# from django.conf import settings
# import os

# # Load the raw dataset
# dataset_path = os.path.join(settings.BASE_DIR, "data", "HRDataset_v14.csv")  # Path to your dataset
# raw_df = pd.read_csv(dataset_path)

# # Preprocessing for the second instance
# preprocessed_df = raw_df.copy()

# # Preprocessing steps
# preprocessed_df['DOB'] = pd.to_datetime(preprocessed_df['DOB'], errors='coerce')
# preprocessed_df['LastPerformanceReview_Date'] = pd.to_datetime(preprocessed_df['LastPerformanceReview_Date'], errors='coerce')

# # Add the 'Age' feature
# preprocessed_df['Age'] = (preprocessed_df['LastPerformanceReview_Date'] - preprocessed_df['DOB']).dt.days // 365

# # Drop unnecessary columns
# columns_to_drop = [
#     'LastPerformanceReview_Date', 'ManagerID', 'PositionID', 'DeptID', 'EmpID',
#     'MaritalStatusID', 'GenderID', 'PerfScoreID', 'EmpStatusID', 'Zip',
#     'Employee_Name', 'Termd', 'DOB', 'DateofHire', 'DateofTermination',
#     'TermReason', 'EmploymentStatus'
# ]
# preprocessed_df = preprocessed_df.drop(columns=columns_to_drop)

# # Convert object columns to categorical
# col_cat = list(preprocessed_df.select_dtypes(include=['object']).columns)
# for col in col_cat:
#     if col != 'PerformanceScore':
#         preprocessed_df[col] = preprocessed_df[col].astype('category')
# col_cat = list(preprocessed_df.select_dtypes(include=['category']).columns)

# # Encode 'PerformanceScore'
# performance_score_mapping = {
#     "PIP": 0,
#     "Needs Improvement": 1,
#     "Fully Meets": 2,
#     "Exceeds": 3
# }
# preprocessed_df['PerformanceScore'] = preprocessed_df['PerformanceScore'].map(performance_score_mapping)
# preprocessed_df['PerformanceScore'] = pd.to_numeric(preprocessed_df['PerformanceScore'], errors='coerce')

# # Target encoding
# def kfold_target_encoding_weighted_mean(df, categorical_cols, target_col, n_splits=7, m=10):
#     df_encoded = df.copy()
#     global_mean = df[target_col].mean()

#     kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

#     for col in categorical_cols:
#         df_encoded[f'{col}_encoded'] = 0.0
#         for train_idx, val_idx in kf.split(df):
#             train_data, val_data = df.iloc[train_idx], df.iloc[val_idx]

#             category_means = train_data.groupby(col, observed=False)[target_col].mean()
#             category_counts = train_data.groupby(col, observed=False)[target_col].count()

#             smoothed_means = (category_means * category_counts + global_mean * m) / (category_counts + m)

#             test = val_data[col].map(smoothed_means)
#             has_nan = test.isnull().any()
#             if has_nan:
#                 val_encoded = val_data[col].map(smoothed_means).fillna(global_mean)
#             else:
#                 val_encoded = val_data[col].map(smoothed_means)

#             df_encoded.loc[val_idx, f'{col}_encoded'] = val_encoded.astype(float)

#     return df_encoded

# preprocessed_df = kfold_target_encoding_weighted_mean(preprocessed_df, col_cat, target_col='PerformanceScore', n_splits=5, m=10)

# # Drop categorical columns after encoding
# preprocessed_df = preprocessed_df.drop(columns=col_cat)

# # # Features and target
# # features = preprocessed_df.columns.tolist()
# # features.remove("PerformanceScore")  # Assuming 'PerformanceScore' is the target column

# categorical_features = {col: preprocessed_df[col].cat.categories.tolist() for col in col_cat}
# numerical_features = list(preprocessed_df.select_dtypes(include=['number']).columns)

# numerical_features.remove('PerformanceScore')

# # Models setup
# model_paths = {
#     "Decision Tree": os.path.join(settings.BASE_DIR, "dump", "DecisionTreeClassifier.pkl"),
#     "K-Nearest Neighbors": os.path.join(settings.BASE_DIR, "dump", "KNeighborsClassifier.pkl"),
#     "Logistic Regression": os.path.join(settings.BASE_DIR, "dump", "LogisticRegression.pkl"),
#     "Random Forest": os.path.join(settings.BASE_DIR, "dump", "RandomForestClassifier.pkl"),
#     "Stacking Classifier": os.path.join(settings.BASE_DIR, "dump", "StackingClassifier.pkl"),
# }

# models = {}
# for name, path in model_paths.items():
#     try:
#         models[name] = joblib.load(path)
#     except FileNotFoundError:
#         print(f"Error: {name} model file not found at {path}")


# def prediction_view(request):
#     predictions = {}  # To store predictions from each model
#     input_data = {feature: "" for feature in numerical_features + list(categorical_features.keys())}  # Initialize with empty strings
#     error_message = None  # Default error message

#     if request.method == "POST":
#         try:
#             # Collect and validate form data
#             for feature in numerical_features:
#                 value = request.POST.get(feature)
#                 if value is None or value.strip() == "":
#                     raise ValueError(f"Missing value for {feature}")
#                 input_data[feature] = float(value)  # Convert numerical features to float

#             for feature, categories in categorical_features.items():
#                 value = request.POST.get(feature)
#                 if value not in categories:
#                     raise ValueError(f"Invalid value for {feature}")
#                 input_data[feature] = value  # Keep categorical features as is

#             # Convert input_data to DataFrame for predictions
#             new_data = pd.DataFrame([input_data])

#             # Encode categorical features into the format expected by models
#             for feature in categorical_features:
#                 new_data[feature] = pd.Categorical(new_data[feature], categories=categorical_features[feature])

#             # Generate predictions for each model
#             for model_name, model in models.items():
#                 predictions[model_name] = model.predict(new_data)[0]

#         except ValueError as e:
#             error_message = str(e)
#         except Exception as e:
#             error_message = "An error occurred while processing your request. Please try again."

#     return render(
#         request,
#         "predict.html",
#         {
#             "categorical_features": categorical_features,
#             "numerical_features": numerical_features,
#             "predictions": predictions,
#             "input_data": input_data,
#             "error_message": error_message,
#         },
#     )



from django.shortcuts import render
import joblib
import pandas as pd
from sklearn.model_selection import KFold
from django.conf import settings
import os

# Load the raw dataset
dataset_path = os.path.join(settings.BASE_DIR, "data", "HRDataset_v14.csv")
raw_df = pd.read_csv(dataset_path)

# Preprocessing for the second instance
preprocessed_df = raw_df.copy()

# Preprocessing steps
preprocessed_df['DOB'] = pd.to_datetime(preprocessed_df['DOB'], format='%Y-%m-%d', errors='coerce')
preprocessed_df['LastPerformanceReview_Date'] = pd.to_datetime(
    preprocessed_df['LastPerformanceReview_Date'], format='%Y-%m-%d', errors='coerce'
)

# Add the 'Age' feature
preprocessed_df['Age'] = (preprocessed_df['LastPerformanceReview_Date'] - preprocessed_df['DOB']).dt.days // 365

# Drop unnecessary columns (only drop if they exist in the DataFrame)
columns_to_drop = [
    'LastPerformanceReview_Date', 'ManagerID', 'PositionID', 'DeptID', 'EmpID',
    'MaritalStatusID', 'GenderID', 'PerfScoreID', 'EmpStatusID', 'Zip',
    'Employee_Name', 'Termd', 'DOB', 'DateofHire', 'DateofTermination',
    'TermReason', 'EmploymentStatus'
]
preprocessed_df = preprocessed_df.drop(columns=[col for col in columns_to_drop if col in preprocessed_df.columns])

# Convert object columns to categorical
col_cat = list(preprocessed_df.select_dtypes(include=['object']).columns)
for col in col_cat:
    if col != 'PerformanceScore':
        preprocessed_df[col] = preprocessed_df[col].astype('category')
col_cat = list(preprocessed_df.select_dtypes(include=['category']).columns)

# Encode 'PerformanceScore'
performance_score_mapping = {
    "PIP": 0,
    "Needs Improvement": 1,
    "Fully Meets": 2,
    "Exceeds": 3
}
if 'PerformanceScore' in preprocessed_df.columns:
    preprocessed_df['PerformanceScore'] = preprocessed_df['PerformanceScore'].map(performance_score_mapping)
    preprocessed_df['PerformanceScore'] = pd.to_numeric(preprocessed_df['PerformanceScore'], errors='coerce')

# Extract categorical features and their unique values
categorical_features = {col: preprocessed_df[col].cat.categories.tolist() for col in col_cat}
numerical_features = list(preprocessed_df.select_dtypes(include=['number']).columns)

if 'PerformanceScore' in numerical_features:
    numerical_features.remove('PerformanceScore')  # Assuming 'PerformanceScore' is the target column

# Models setup
model_paths = {
    "Decision Tree": os.path.join(settings.BASE_DIR, "dump", "DecisionTreeClassifier.pkl"),
    "K-Nearest Neighbors": os.path.join(settings.BASE_DIR, "dump", "KNeighborsClassifier.pkl"),
    "Logistic Regression": os.path.join(settings.BASE_DIR, "dump", "LogisticRegression.pkl"),
    "Random Forest": os.path.join(settings.BASE_DIR, "dump", "RandomForestClassifier.pkl"),
    "Stacking Classifier": os.path.join(settings.BASE_DIR, "dump", "StackingClassifier.pkl"),
}

models = {}
for name, path in model_paths.items():
    try:
        models[name] = joblib.load(path)
    except FileNotFoundError:
        print(f"Error: {name} model file not found at {path}")


def prediction_view(request):
    predictions = {}  # To store predictions from each model
    input_data = {feature: "" for feature in numerical_features + list(categorical_features.keys())}

    # Convert input_data to a dot-accessible object
    class DotAccessibleDict(dict):
        def __getattr__(self, attr):
            return self.get(attr, "")

    input_data = DotAccessibleDict(input_data)

    error_message = None

    if request.method == "POST":
        try:
            # Collect and validate form data
            for feature in numerical_features:
                value = request.POST.get(feature)
                if not value or value.strip() == "":
                    raise ValueError(f"Missing value for {feature}")
                input_data[feature] = float(value)

            for feature, categories in categorical_features.items():
                value = request.POST.get(feature)
                if value not in categories:
                    raise ValueError(f"Invalid value for {feature}")
                input_data[feature] = value

            # Prepare DataFrame for prediction
            new_data = pd.DataFrame([input_data])

            # Encode categorical features as expected by models
            for feature in categorical_features:
                new_data[feature] = pd.Categorical(new_data[feature], categories=categorical_features[feature])

            # Generate predictions
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
            "categorical_features": categorical_features,
            "numerical_features": numerical_features,
            "predictions": predictions,
            "input_data": input_data,
            "error_message": error_message,
        },
    )
