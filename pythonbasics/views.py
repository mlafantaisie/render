import pandas as pd
import matplotlib.pyplot as plt
from django.shortcuts import render
from .models import DataEntry
from .forms import UploadFileForm
import io
import urllib, base64

def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def upload_data(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Read the uploaded CSV file
                df = pd.read_csv(request.FILES["file"])

                # Check if required columns exist
                required_columns = {"name", "value"}
                if not required_columns.issubset(df.columns):
                    return render(request, "upload.html", {"form": form, "error": "Invalid CSV format. Ensure 'name' and 'value' columns exist."})

                # Clean and Save Data
                for _, row in df.iterrows():
                    DataEntry.objects.create(name=row["name"], value=row["value"])

                return render(request, "upload_success.html")  # Show success page

            except Exception as e:
                return render(request, "upload.html", {"form": form, "error": f"Error processing file: {str(e)}"})
    
    else:
        form = UploadFileForm()

    return render(request, "upload.html", {"form": form})

def data_dashboard(request):
    # Get all data from the database
    data = DataEntry.objects.all().values("name", "value")
    df = pd.DataFrame.from_records(data)

    # Generate a chart
    plt.figure(figsize=(6, 4))
    df.plot(kind="bar", x="name", y="value")

    # Convert to image
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    string = base64.b64encode(buffer.read()).decode("utf-8")
    image_uri = "data:image/png;base64," + string

    return render(request, "dashboard.html", {"chart": image_uri})
