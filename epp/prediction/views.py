from django.shortcuts import render
from .ml_model import predict_productivity

def predict(request):
    result = None
    if request.method == 'POST':
        # Get data from the form
        data = {
            'experience': request.POST.get('experience'),
            'hours_worked': request.POST.get('hours_worked'),
        }
        # Use the ML model to predict productivity
        result = predict_productivity(data)

    return render(request, 'predict.html', {'result': result})
