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
            offset = form.cleaned_data.get('offset') or 217814  # default if not entered

            file_path = os.path.join('/tmp', 'uploaded.accdb')
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            parser = AccdbParser(file_path)
            results = parser.parse(offset=offset)

            context['results'] = results

    else:
        form = UploadAccessDBForm()

    context['form'] = form
    return render(request, 'home.html', context)
    
