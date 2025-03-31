import os
from django.shortcuts import render
from .forms import UploadAccessDBForm
from .accdb_parser import AccdbParser

def home(request):
    context = {}

    file_path = request.session.get("uploaded_file_path")

    if request.method == 'POST':
        form = UploadAccessDBForm(request.POST, request.FILES)

        if form.is_valid():
            # Handle file upload if provided
            if 'accdb_file' in request.FILES:
                file = form.cleaned_data['accdb_file']
                site_code = form.cleaned_data['site_code']
                file_path = f"/tmp/{site_code}.accdb"

                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                request.session["uploaded_file_path"] = file_path

            # Handle offset
            offset = form.cleaned_data.get("offset")
            if not offset and request.session.get("last_offset"):
                offset = request.session["last_offset"]
            else:
                offset = offset or 217814
                request.session["last_offset"] = offset

            # Handle chunk size
            window = form.cleaned_data.get("chunk_size")
            if not window and request.session.get("last_window"):
                window = request.session["last_window"]
            else:
                window = window or 64
                request.session["last_window"] = window  # <- 🔧 you were missing assignment here!

            # Run parser
            parser = AccdbParser(file_path)
            results = parser.parse(offset=offset, window=window)
            context['results'] = results

        else:
            context['form'] = form
            return render(request, 'home.html', context)

    else:
        form = UploadAccessDBForm()

    context['form'] = form
    return render(request, 'home.html', context)
