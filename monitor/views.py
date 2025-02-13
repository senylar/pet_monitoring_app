# views.py
import csv
from django.shortcuts import render, redirect
from .forms import UploadCSVForm
from .models import Server

def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            for row in reader:
                Server.objects.create(name=row[0], endpoint=row[1])
            return redirect('success_url')  # Замените 'success_url' на ваш URL
    else:
        form = UploadCSVForm()
    return render(request, 'servers/upload_csv.html', {'form': form})