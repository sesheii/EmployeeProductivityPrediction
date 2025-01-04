from django.shortcuts import render
from django import forms
import pandas as pd
import os
from datetime import date


def unique_df(df, column):
    return sorted([i for i in df[f"{column}"].unique()])

original_dataset = pd.read_csv(os.path.join("data/HRDataset_v14.csv"))


def calculate_age(dob, reference_date):
    if not isinstance(dob, date) or not isinstance(reference_date, date):
        raise ValueError("Both DOB and reference_date must be datetime.date objects")

    if dob > reference_date:
        raise ValueError("Date of Birth cannot be after the reference date")

    # Calculate age based on the reference date
    age = reference_date.year - dob.year - ((reference_date.month, reference_date.day) < (dob.month, dob.day))
    return age


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
        if field_name == "Married":
            if value == "Yes":
                results["MarriedID"] = 1
            else:
                results["MarriedID"] = 0

        if field_name in ["Salary", "EmpSatisfaction", "SpecialProjectsCount", "DaysLateLast30", "Absences"]:
            results[field_name] = int(value)

        if field_name == "Salary":
            results["Salary"] = int(value)

        if field_name == "Salary":
            results["Salary"] = int(value)


        elif field_name not in ["DOB", "LastPerformanceReview_Date"]:
            results[field_name] = f"{value}"

    return results


def dynamic_form_view(request):
    fields_config = [
        {
            "name": "DOB",
            "type": "date",
            "label": "DateOfBirth",
            "required": True,
            "choices": [],
        },
        {
            "name": "LastPerformanceReview_Date",
            "type": "date",
            "label": "LastPerformanceReview_Date",
            "required": True,
            "choices": [],
        },
        {
            "name": "Married",
            "type": "category",
            "label": "MarriedID",
            "required": True,
            "choices": ["Yes", "No"],
        },
        {
            "name": "Salary",
            "type": "number",
            "label": "Salary",
            "required": True,
            "choices": unique_df(original_dataset, "Salary"),
        },
        # {
        #     "name": "PerformanceScore",
        #     "type": "category",
        #     "label": "PerformanceScore",
        #     "required": True,
        #     "choices": unique_df(original_dataset, "PerformanceScore"),
        # },
        {
            "name": "EmpSatisfaction",
            "type": "category",
            "label": "EmpSatisfaction",
            "required": True,
            "choices": unique_df(original_dataset, "EmpSatisfaction"),
        },
        {
            "name": "SpecialProjectsCount",
            "type": "number",
            "label": "SpecialProjectsCount",
            "required": True,
            "choices": unique_df(original_dataset, "SpecialProjectsCount"),
        },
        {
            "name": "DaysLateLast30",
            "type": "number",
            "label": "DaysLateLast30",
            "required": True,
            "choices": unique_df(original_dataset, "DaysLateLast30"),
        },
        {
            "name": "Absences",
            "type": "number",
            "label": "Absences",
            "required": True,
            "choices": unique_df(original_dataset, "Absences"),
        },
        {
            "name": "Position_encoded", # encode
            "type": "category",
            "label": "Position_encoded",
            "required": True,
            "choices": unique_df(original_dataset, "Position"),
        },
        {
            "name": "State_encoded", # encode
            "type": "category",
            "label": "State_encoded",
            "required": True,
            "choices": unique_df(original_dataset, "State"),
        },
        {
            "name": "Sex_encoded", # encode
            "type": "category",
            "label": "Sex_encoded",
            "required": True,
            "choices": unique_df(original_dataset, "Sex"),
        },
        {
            "name": "RaceDesc_encoded", # encode
            "type": "category",
            "label": "RaceDesc_encoded",
            "required": True,
            "choices": unique_df(original_dataset, "RaceDesc"),
        },
        {
            "name": "Department_encoded", # encode
            "type": "category",
            "label": "Department_encoded",
            "required": True,
            "choices": unique_df(original_dataset, "Department"),
        },
        {
            "name": "RecruitmentSource_encoded", # encode
            "type": "category",
            "label": "RecruitmentSource_encoded",
            "required": True,
            "choices": unique_df(original_dataset, "RecruitmentSource"),
        },
        {
            "name": "MaritalDesc_encoded", # encode
            "type": "category",
            "label": "MaritalDesc_encoded",
            "required": True,
            "choices": unique_df(original_dataset, "MaritalDesc"),
        },
        {
            "name": "CitizenDesc_encoded", # encode
            "type": "category",
            "label": "CitizenDesc_encoded",
            "required": True,
            "choices": unique_df(original_dataset, "CitizenDesc"),
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

                if field_type == "category" and choices:
                    self.fields[field_name] = forms.ChoiceField(
                        label=label,
                        required=required,
                        choices=[(choice, choice) for choice in choices],
                        widget=forms.Select,
                    )
                elif choices:
                    self.fields[field_name] = forms.CharField(
                        label=label,
                        required=required,
                        widget=forms.TextInput(attrs={
                            "list": f"options-{field_name}",
                            "choices": choices,
                            "autocomplete": "off",
                        })
                    )
                elif field_type == "text":
                    self.fields[field_name] = forms.CharField(label=label, required=required)
                elif field_type == "number":
                    self.fields[field_name] = forms.IntegerField(label=label, required=required)
                elif field_type == "date":
                    self.fields[field_name] = forms.DateField(
                        label=label,
                        required=required,
                        widget=forms.DateInput(attrs={"type": "date"})
                    )

    response_message = None

    if request.method == "POST":
        form = DynamicForm(fields_config, request.POST)
        if form.is_valid():
            form_data = {field: form.cleaned_data[field] for field in form.cleaned_data}
            results = process_form_data(form_data)
            # print(f"Form Data: {form_data}")  # Debugging
            response_message = " ".join(str(results.values()))
        else:
            response_message = "There were errors in the form. Please correct them."
    else:
        form = DynamicForm(fields_config)

    return render(request, "dynamic_form.html", {
        "form": form,
        "response_message": response_message,
    })
