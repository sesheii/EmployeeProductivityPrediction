from django.shortcuts import render
from django import forms

def dynamic_form_view(request):
    # Define fields and their handling logic
    fields_config = [
        {
            "name": "username",
            "type": "text",
            "label": "Username",
            "required": True,
            "handler": lambda value: f"Hello, {value.upper()}!"  # Example: Greet the user
        },
        {
            "name": "age",
            "type": "number",
            "label": "Age",
            "required": False,
            "handler": lambda value: f"You are {value + 10} years old in the future."  # Add 10 to the age
        },
        {
            "name": "birth_date",
            "type": "date",
            "label": "Birth Date",
            "required": True,
            "handler": lambda value: f"You were born on {value.strftime('%A, %B %d, %Y')}."  # Format date
        },
        {
            "name": "shit date",
            "type": "date",
            "label": "Date",
            "required": True,
            "handler": lambda value: f"Hello, {value}!"  # Example: Greet the user
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

                if field_type == "text":
                    self.fields[field_name] = forms.CharField(label=label, required=required)
                elif field_type == "number":
                    self.fields[field_name] = forms.IntegerField(label=label, required=required)
                elif field_type == "date":
                    self.fields[field_name] = forms.DateField(
                        label=label,
                        required=required,
                        widget=forms.DateInput(attrs={"type": "date"})  # Enable browser's date picker
                    )

    response_message = None

    if request.method == "POST":
        form = DynamicForm(fields_config, request.POST)
        if form.is_valid():
            # Handle each field individually
            results = {}
            for field in fields_config:
                field_name = field["name"]
                handler = field["handler"]
                field_value = form.cleaned_data[field_name]
                results[field_name] = handler(field_value)  # Apply the handler function

            # Generate a response message
            response_message = " ".join(results.values())
    else:
        form = DynamicForm(fields_config)

    return render(request, "dynamic_form.html", {"form": form, "response_message": response_message})
