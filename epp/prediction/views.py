from django.shortcuts import render
from django import forms
import pandas as pd
import os
from datetime import date
import hashlib
import json
from sklearn.model_selection import KFold
import joblib
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def hash_map_with_md5(data: dict) -> str:
    json_data = json.dumps(data, sort_keys=True)
    md5_hash = hashlib.md5()
    md5_hash.update(json_data.encode('utf-8'))
    return md5_hash.hexdigest()


def unique_df(df, column):
    return sorted([i for i in df[f"{column}"].unique()])

original_dataset = pd.read_csv(os.path.join("data/HRDataset_v14.csv"))
pd.set_option('display.max_columns', None)


def calculate_age(dob, reference_date):
    if not isinstance(dob, date) or not isinstance(reference_date, date):
        raise ValueError("Both DOB and reference_date must be datetime.date objects")

    if dob > reference_date:
        raise ValueError("Date of Birth cannot be after the reference date")

    age = reference_date.year - dob.year - ((reference_date.month, reference_date.day) < (dob.month, dob.day))
    return age


def kfold_target_encoding_weighted_mean(df, categorical_cols, target_col, n_splits=7, m=10):
    df_encoded = df.copy()
    global_mean = df[target_col].mean()

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    for col in categorical_cols:
        df_encoded[f'{col}_encoded'] = 0.0
        for train_idx, val_idx in kf.split(df):
            train_data, val_data = df.iloc[train_idx], df.iloc[val_idx]

            category_means = train_data.groupby(col, observed=False)[target_col].mean()
            category_counts = train_data.groupby(col, observed=False)[target_col].count()

            smoothed_means = (category_means * category_counts + global_mean * m) / (category_counts + m)

            test = val_data[col].map(smoothed_means)
            has_nan = test.isnull().any()
            if has_nan:
                val_encoded = val_data[col].map(smoothed_means).fillna(global_mean)
            else:
                val_encoded = val_data[col].map(smoothed_means)

            df_encoded.loc[val_idx, f'{col}_encoded'] = val_encoded.astype(float)

    return df_encoded


def process_form_data(form_data):
    results = {}
    dob = None
    last_review_date = None

    for field_name, value in form_data.items():
        if field_name == "DOB":
            dob = value
        elif field_name == "LastPerformanceReview_Date":
            last_review_date = value

    if dob and last_review_date:
        try:
            age = calculate_age(dob, last_review_date)
            results["Age"] = f"{age}"
        except ValueError as e:
            results["Age"] = str(e)
    else:
        results["Age"] = "Both DOB and LastPerformanceReview_Date are required for age calculation"

    for field_name, value in form_data.items():
        if field_name == "MarriedID":
            if value == "Yes":
                results["MarriedID"] = 1
            else:
                results["MarriedID"] = 0

        if field_name in ["Age", "Salary", "EngagementSurvey", "EmpSatisfaction", "SpecialProjectsCount", "DaysLateLast30", "Absences"]:
            results[field_name] = int(value)

        if field_name in ["Position", "State", "Sex", "RaceDesc", "ManagerName", "Department", "RecruitmentSource", "MaritalDesc", "CitizenDesc"]:
            results[field_name] = value

        # elif field_name not in ["DOB", "LastPerformanceReview_Date"]:
        #     results[field_name] = f"{value}"

    hash_hex = hash_map_with_md5(results)
    hash_decimal = int(hash_hex, 16)
    results["EmpID"] = hash_decimal
    # results["PerformanceScore"] = "Exceeds"
    results["PerformanceScore"] = "Fully Meets"


    selected_columns = ["EmpID", "DOB", "LastPerformanceReview_Date", "MarriedID", "Salary", "EngagementSurvey", "EmpSatisfaction",
                        "SpecialProjectsCount", "DaysLateLast30", "Absences", "Position", "State", "Sex", "RaceDesc",
                        "ManagerName", "Department", "RecruitmentSource", "MaritalDesc", "CitizenDesc", "PerformanceScore"]
    df = original_dataset[selected_columns].copy()

    df["DOB"] = pd.to_datetime(df["DOB"], errors="coerce")
    df["LastPerformanceReview_Date"] = pd.to_datetime(df["LastPerformanceReview_Date"], errors="raise", format='%m/%d/%Y')
    df['Age'] = (df['LastPerformanceReview_Date'] - df['DOB']).dt.days // 365
    df = df.drop(columns=[
        "DOB", "LastPerformanceReview_Date"
    ])

    new_record_df = pd.DataFrame([results])
    df = pd.concat([df, new_record_df], ignore_index=True)
    df['EmpID'] = pd.to_numeric(df['EmpID'], errors='coerce')
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')

    col_cat = list(df.select_dtypes(include=['object']).columns)
    for i in col_cat:
        if i != 'PerformanceScore':
            df[i] = df[i].astype('category')
    col_cat = list(df.select_dtypes(include=['category']).columns)

    performance_score_mapping = {
        "PIP": 0,
        "Needs Improvement": 1,
        "Fully Meets": 2,
        "Exceeds": 3
    }

    df['PerformanceScore'] = df['PerformanceScore'].map(performance_score_mapping)
    df['PerformanceScore'] = pd.to_numeric(df['PerformanceScore'], errors='coerce')

    df_encoded = kfold_target_encoding_weighted_mean(df, col_cat, target_col='PerformanceScore', n_splits=5, m=10)
    df_encoded = df_encoded.drop(columns=col_cat)

    encoded_record = df_encoded[df_encoded["EmpID"] == hash_decimal].iloc[0]
    encoded_record = pd.DataFrame([encoded_record.drop(["EmpID", "PerformanceScore"])])


    clf = joblib.load("dump/RandomForestClassifier.pkl")
    expected_features = clf.feature_names_in_
    # print("Expected features:", expected_features)

    encoded_record = encoded_record[clf.feature_names_in_]
    results_array = clf.predict(encoded_record)
    results_scalar = results_array[0]

    reverse_performance_score_mapping = {
        0: "PIP",
        1: "Needs Improvement",
        2: "Fully Meets",
        3: "Exceeds",
    }
    # print(encoded_record.columns)
    # print(encoded_record.info())
    # print(df[df["EmpID"] == hash_decimal])
    # print(df_encoded[df_encoded["EmpID"] == hash_decimal])
    # print(df.info())
    # print(df_encoded.info())
    # print(df.head())
    # print(str(results))
    return reverse_performance_score_mapping.get(results_scalar)


def dynamic_form_view(request):
    fields_config = [
        # {
        #     "name": "DOB",
        #     "type": "date",
        #     "label": "DateOfBirth",
        #     "required": True,
        #     "choices": [],
        #     "desc": "Дата народження.",
        # },
        # {
        #     "name": "LastPerformanceReview_Date",
        #     "type": "date",
        #     "label": "LastPerformanceReview_Date",
        #     "required": True,
        #     "choices": [],
        #     "desc": "Дата останнього проведення оцінки продуктивності.",
        # },
        {
            "name": "Age",
            "type": "number",
            "label": "Age",
            "required": True,
            "choices": [],
            "desc": "Вік працівника.",
        },
        {
            "name": "MarriedID",
            "type": "category",
            "label": "MarriedID",
            "required": True,
            "choices": ["Yes", "No"],
            "desc": "Ідентифікатор сімейного стану.",
        },
        {
            "name": "Salary",
            "type": "number",
            "label": "Salary",
            "required": True,
            "choices": unique_df(original_dataset, "Salary"),
            "desc": "Заробітна плата у USD/рік.",
        },
        # {
        #     "name": "PerformanceScore",
        #     "type": "category",
        #     "label": "PerformanceScore",
        #     "required": True,
        #     "choices": unique_df(original_dataset, "PerformanceScore"),
        # },
        {
            "name": "EngagementSurvey",
            "type": "text",
            "label": "EngagementSurvey",
            "required": True,
            "choices": unique_df(original_dataset, "EngagementSurvey"),
            "desc": "Значення від 1 до 5 включно. Результати опитування залученості працівника.",
        },
        {
            "name": "EmpSatisfaction",
            "type": "category",
            "label": "EmpSatisfaction",
            "required": True,
            "choices": unique_df(original_dataset, "EmpSatisfaction"),
            "desc": "Рівень задоволення працівника роботою.",
        },
        {
            "name": "SpecialProjectsCount",
            "type": "number",
            "label": "SpecialProjectsCount",
            "required": True,
            "choices": unique_df(original_dataset, "SpecialProjectsCount"),
            "desc": "Кількість проєктів, у яких брав участь працівник за останні 6 місяців.",
        },
        {
            "name": "DaysLateLast30",
            "type": "number",
            "label": "DaysLateLast30",
            "required": True,
            "choices": unique_df(original_dataset, "DaysLateLast30"),
            "desc": "Кількість днів, коли працівник спізнився за останні 30 днів.",
        },
        {
            "name": "Absences",
            "type": "number",
            "label": "Absences",
            "required": True,
            "choices": unique_df(original_dataset, "Absences"),
            "desc": "Загальна кількість відсутностей працівника.",
        },
        {
            "name": "Position", # _encoded
            "type": "category",
            "label": "Position",
            "required": True,
            "choices": unique_df(original_dataset, "Position"),
            "desc": "Посада працівника.",
        },
        {
            "name": "State", # _encoded
            "type": "category",
            "label": "State",
            "required": True,
            "choices": unique_df(original_dataset, "State"),
            "desc": "Штат, де живе людина.",
        },
        {
            "name": "Sex", # _encoded
            "type": "category",
            "label": "Sex",
            "required": True,
            "choices": unique_df(original_dataset, "Sex"),
            "desc": "Стать працівника.",
        },
        {
            "name": "RaceDesc", # _encoded
            "type": "category",
            "label": "RaceDesc",
            "required": True,
            "choices": unique_df(original_dataset, "RaceDesc"),
            "desc": "опис раси, до якої людина себе відносить.",
        },
        {
            "name": "ManagerName", # _encoded
            "type": "category",
            "label": "ManagerName",
            "required": True,
            "choices": unique_df(original_dataset, "ManagerName"),
            "desc": "Ім'я менеджера, який відповідає за працівника.",
        },
        {
            "name": "Department", # _encoded
            "type": "category",
            "label": "Department",
            "required": True,
            "choices": unique_df(original_dataset, "Department"),
            "desc": "Відділ, у якому працює працівник.",
        },
        {
            "name": "RecruitmentSource", # _encoded
            "type": "category",
            "label": "RecruitmentSource",
            "required": True,
            "choices": unique_df(original_dataset, "RecruitmentSource"),
            "desc": "Джерело, через яке працівник був найнятий.",
        },
        {
            "name": "MaritalDesc", # _encoded
            "type": "category",
            "label": "MaritalDesc",
            "required": True,
            "choices": unique_df(original_dataset, "MaritalDesc"),
            "desc": "Сімейний стан працівника.",
        },
        {
            "name": "CitizenDesc", # _encoded
            "type": "category",
            "label": "CitizenDesc",
            "required": True,
            "choices": unique_df(original_dataset, "CitizenDesc"),
            "desc": "Позначка про те, чи є особа громадянином або негромадянином, який має право на отримання допомоги.",
        },

    ]

    class DynamicForm(forms.Form):
        def __init__(self, fields, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in fields:
                field_name = field["name"]
                field_type = field["type"]
                label = field["label"]
                required = field["required"]
                choices = field.get("choices", None)
                desc = field.get("desc", "")

                if field_type == "category" and choices:
                    self.fields[field_name] = forms.ChoiceField(
                        label=label,
                        required=required,
                        choices=[(choice, choice) for choice in choices],
                        widget=forms.Select(attrs={"desc": desc}),
                    )
                elif choices:
                    self.fields[field_name] = forms.CharField(
                        label=label,
                        required=required,
                        widget=forms.TextInput(attrs={
                            "list": f"options-{field_name}",
                            "choices": choices,
                            "autocomplete": "off",
                            "desc": desc,
                        })
                    )
                elif field_type == "text":
                    self.fields[field_name] = forms.CharField(
                        label=label,
                        required=required,
                        widget=forms.TextInput(attrs={"desc": desc}),
                    )
                elif field_type == "number":
                    self.fields[field_name] = forms.IntegerField(
                        label=label,
                        required=required,
                        widget=forms.NumberInput(attrs={"desc": desc}),
                    )
                elif field_type == "date":
                    self.fields[field_name] = forms.DateField(
                        label=label,
                        required=required,
                        widget=forms.DateInput(attrs={"type": "date", "desc": desc}),
                    )


    response_message = None

    if request.method == "POST":
            form = DynamicForm(fields_config, request.POST)
            if form.is_valid():
                form_data = {field: form.cleaned_data[field] for field in form.cleaned_data}
                results = process_form_data(form_data)
                # response_message = " ".join(str(results))
                response_message = str(results)
            else:
                response_message = "There were errors in the form. Please correct them."
    else:
        form = DynamicForm(fields_config)

    return render(request, "dynamic_form.html", {
        "form": form,
        "response_message": response_message,
    })
