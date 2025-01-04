from django.shortcuts import render
from django import forms


def process_form_data(form_data):
    results = {}
    for field_name, value in form_data.items():
        if field_name == "username":
            results[field_name] = f"Hello, {value.upper()}!"
        elif field_name == "age":
            results[field_name] = f"You are {int(value) + 10} years old in the future."
        elif field_name == "birth_date":
            results[field_name] = f"You were born on {value.strftime('%A, %B %d, %Y')}."
        elif field_name == "shit date":
            results[field_name] = f"The selected date is {value.isoformat()}."
        else:
            results[field_name] = f"Value: {value}"
    return results


def dynamic_form_view(request):
    fields_config = [
        {
            "name": "MarriedID",
            "type": "category",
            "label": "MarriedID",
            "required": True,
            "choices": [0, 1],
        },
        {
            "name": "Salary",
            "type": "number",
            "label": "Salary",
            "required": True,
            "choices": [49999, 75000, 99999],
        },
        {
            "name": "PerformanceScore",
            "type": "category",
            "label": "Performance Score",
            "required": True,
            "choices": ["PIP", "Needs Improvement", "Fully Meets", "Exceeds"],
        },
        {
            "name": "EmpSatisfaction",
            "type": "category",
            "label": "EmpSatisfaction",
            "required": True,
            "choices": [1, 2, 3, 4],
        },
        {
            "name": "SpecialProjectsCount",
            "type": "number",
            "label": "SpecialProjectsCount",
            "required": True,
            "choices": [],
        },
        {
            "name": "DaysLateLast30",
            "type": "number",
            "label": "DaysLateLast30",
            "required": True,
            "choices": [],
        },
        {
            "name": "Absences",
            "type": "number",
            "label": "Absences",
            "required": True,
            "choices": [],
        },
        {
            "name": "Age",
            "type": "number",
            "label": "Age",
            "required": True,
            "choices": [],
        },
        {
            "name": "Sex_encoded",
            "type": "category",
            "label": "Sex_encoded",
            "required": True,
            "choices": ["1"],
        },
        {
            "name": "Age",
            "type": "number",
            "label": "Age",
            "required": True,
            "choices": [],
        },
        {
            "name": "Age",
            "type": "number",
            "label": "Age",
            "required": True,
            "choices": [],
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
            response_message = " ".join(results.values())
        else:
            response_message = "There were errors in the form. Please correct them."
    else:
        form = DynamicForm(fields_config)

    return render(request, "dynamic_form.html", {
        "form": form,
        "response_message": response_message,
    })
