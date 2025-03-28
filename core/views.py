import os
from django.shortcuts import render
from .forms import UploadAccessDBForm
import io
import urllib, base64
from .accdb_parser import AccdbParser

def home(request):
    context = {}

    if request.method == 'POST':
        form = UploadAccessDBForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['accdb_file']
            filename = file.name.lower()

            if not filename.endswith(('.accdb', '.r5c')):
                form.add_error('accdb_file', 'Unsupported file type.')
                return render(request, 'upload.html', {'form': form})

            # Save file
            file_path = os.path.join('/tmp', 'uploaded.accdb')
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Parse it
            parser = AccdbParser(file_path)
            results = parser.parse()

            context['results'] = results

    else:
        form = UploadAccessDBForm()

    context['form'] = form
    return render(request, 'home.html', context)
    
