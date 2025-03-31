import os
from django.shortcuts import render
from .forms import UploadAccessDBForm
import io
import urllib, base64
from .accdb_parser import AccdbParser

def home(request):
    context = {}

    file_path = request.session.get("uploaded_file_path")  # Load existing session file
    offset = request.POST.get("offset", 217814)

    if request.method == 'POST':
        form = UploadAccessDBForm(request.POST, request.FILES)

        if form.is_valid():
            # If new file is uploaded, save it
            if 'accdb_file' in request.FILES:
                file = form.cleaned_data['accdb_file']
                site_code = form.cleaned_data['site_code']
                file_path = f"/tmp/{site_code}.accdb"

                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                request.session["uploaded_file_path"] = file_path  # Save path in session

            # Now run the parser
            parser = AccdbParser(file_path)
            results = parser.parse(offset=offset)
            context['results'] = results
        else:
            context['form'] = form
            return render(request, 'home.html', context)

    else:
        form = UploadAccessDBForm()

    context['form'] = form
    return render(request, 'home.html', context)
    
