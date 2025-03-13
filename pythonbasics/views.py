import pandas as pd
from django.shortcuts import render
from .models import DataEntry
from .forms import UploadFileForm

def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def upload_data(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            df = pd.read_csv(request.FILES["file"])  # Read CSV file
            for index, row in df.iterrows():
                DataEntry.objects.create(name=row["name"], value=row["value"])
            return render(request, "upload_success.html")  # Show success page
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})
