# your_app/forms.py
from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Chọn file để import dữ liệu")