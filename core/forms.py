from django import forms

class UploadAccessDBForm(forms.Form):
    accdb_file = forms.FileField(
        label='Access DB File (.accdb or .r5c)',
        help_text='Upload a Microsoft Access database file for parsing.'
    )
