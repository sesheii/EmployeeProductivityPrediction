from django import forms

class DynamicForm(forms.Form):
    def __init__(self, fields_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field_properties in fields_config.items():
            field_type = field_properties.get("type", "text")  # Default to text field
            label = field_properties.get("label", field_name)

            if field_type == "text":
                self.fields[field_name] = forms.CharField(label=label, required=field_properties.get("required", True))
            elif field_type == "number":
                self.fields[field_name] = forms.IntegerField(label=label, required=field_properties.get("required", True))
            elif field_type == "date":
                self.fields[field_name] = forms.DateField(label=label, required=field_properties.get("required", True))
            # Add more field types as needed
