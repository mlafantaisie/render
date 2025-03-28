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

def site_list(request):
    sites = Site.objects.all()
    return render(request, 'site_list.html', {'sites': sites})

def upload_view(request):
    if request.method == 'POST':
        form = UploadAccessDBForm(request.POST, request.FILES)
        if form.is_valid():
            site_code = form.cleaned_data['site_code']
            file = form.cleaned_data['accdb_file']
            original_name = file.name.lower()

            # Determine new filename
            if original_name.endswith('.r5c'):
                new_filename = f"{site_code}.accdb"
            elif original_name.endswith('.accdb'):
                new_filename = file.name
            else:
                # Reject unsupported file types
                form.add_error('accdb_file', 'Unsupported file type. Please upload a .r5c or .accdb file.')
                return render(request, 'upload.html', {'form': form})

            # Save file to /tmp (or your media directory)
            upload_path = os.path.join('/tmp', new_filename)
            with open(upload_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Create site record if not exists
            Site.objects.get_or_create(site_code=site_code, defaults={
                'site_name': site_code.capitalize(),
                'description': f'Uploaded {new_filename}',
            })

            # TODO: Process this file into PostgreSQL
            return redirect('site_list')
    else:
        form = UploadAccessDBForm()

    return render(request, 'upload.html', {'form': form})


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
    try:
        # Get all data from the database
        data = DataEntry.objects.all().values("name", "value")
        
        # Check if data exists
        if not data:
            return render(request, "dashboard.html", {"error": "No data available for visualization."})
        
        df = pd.DataFrame.from_records(data)

        # Ensure there is at least one valid data row
        if df.empty:
            return render(request, "dashboard.html", {"error": "No valid data found."})

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

    except Exception as e:
        # Log the error (optional: print to logs for debugging)
        print(f"Dashboard error: {e}")

        # Display an error message instead of crashing the server
        return render(request, "dashboard.html", {"error": "An error occurred while generating the dashboard."})

