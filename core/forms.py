from django import forms

class UploadAccessDBForm(forms.Form):
    site_code = forms.CharField(required=False, label='Site Code (optional)', max_length=50)
    accdb_file = forms.FileField(
        label='Access DB File (.accdb or .r5c)',
        help_text='Upload a Microsoft Access database file for parsing.'
    )
