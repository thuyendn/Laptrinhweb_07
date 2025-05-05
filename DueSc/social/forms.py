from django import forms
from .models import TinNhan

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Chọn file để import dữ liệu")

class GroupForm(forms.ModelForm):
    """Form để tạo và chỉnh sửa nhóm"""
    class Meta:
        fields = ['name', 'description', 'privacy', 'cover_photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 4}),
            'privacy': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'cover_photo': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }

class PostForm(forms.ModelForm):
    """Form để tạo bài viết trong nhóm"""
    class Meta:
        fields = ['content', 'image', 'file']
        widgets = {
            'content': forms.Textarea(
                attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 3, 'placeholder': 'Hãy đăng bài viết!'}),
            'image': forms.FileInput(attrs={'class': 'hidden', 'id': 'image-upload'}),
            'file': forms.FileInput(attrs={'class': 'hidden', 'id': 'file-upload'}),
        }

class InviteMembersForm(forms.Form):
    """Form để mời thành viên vào nhóm"""
    user_ids = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'w-5 h-5'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        users = kwargs.pop('users', None)
        super().__init__(*args, **kwargs)
        if users:
            self.fields['user_ids'].choices = [(user.id, user.username) for user in users]

class TinNhanForm(forms.ModelForm):
    """Form để gửi tin nhắn"""
    class Meta:
        model = TinNhan
        fields = ['NoiDung']
        widgets = {
            'NoiDung': forms.Textarea(attrs={'placeholder': 'Aa', 'class': 'flex-1 bg-transparent px-3 py-2 focus:outline-none'}),
        }