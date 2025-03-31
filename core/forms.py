from django import forms

class UploadAccessDBForm(forms.Form):
    site_code = forms.CharField(label='Site Code', max_length=50, required=False)
    accdb_file = forms.FileField(label='Access DB File (.accdb)', required=False)
    offset = forms.IntegerField(label='Inspect Offset (Optional)', required=False, min_value=0)
    chunk_size = forms.IntegerField(
        label='Bytes to Read (Optional)', required=False, min_value=16, max_value=512
    )
    
