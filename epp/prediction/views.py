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
            "type": "number",
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
            "type": "text",
            "label": "PerformanceScore",
            "required": True,
        },
        {
            "name": "shit date",
            "type": "date",
            "label": "Date",
            "required": True,
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

                if choices:  # If dropdown suggestions are specified
                    self.fields[field_name] = forms.CharField(
                        label=label,
                        required=required,
                        widget=forms.TextInput(attrs={
                            "list": f"options-{field_name}",  # Link to the datalist element
                            "choices": choices  # Pass the choices to the widget for use in the template
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
        form = DynamicForm(fields_config)

    return render(request, "dynamic_form.html", {"form": form, "response_message": response_message})
