from django import forms

class UploadAccessDBForm(forms.Form):
    site_code = forms.CharField(label='Site Code', max_length=50)
    accdb_file = forms.FileField(label='Access DB File (.accdb)')
