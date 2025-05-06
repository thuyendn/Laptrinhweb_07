# your_app/forms.py
from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Chọn file để import dữ liệu")


from django import forms


# Giả sử bạn có các model sau
# from .models import Group, Post

class GroupForm(forms.ModelForm):
    """Form để tạo và chỉnh sửa nhóm"""

    class Meta:
        # model = Group
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
        # model = Post
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
        # Lấy danh sách user từ kwargs
        users = kwargs.pop('users', None)
        super().__init__(*args, **kwargs)

        if users:
            # Tạo choices từ danh sách user
            self.fields['user_ids'].choices = [(user.id, user.username) for user in users]

# NGOẠI KHOÁ
from django import forms
from django.core.exceptions import ValidationError
from .models import HoatDongNgoaiKhoa
from datetime import datetime

class ExtracurricularForm(forms.ModelForm):
    # Định nghĩa ChoiceField cho muc_diem_nk
    muc_diem_nk = forms.ChoiceField(
        choices=[
            ('I', 'I'),
            ('II', 'II'),
            ('III', 'III'),
            ('IV', 'IV'),
        ],
        label='Mục điểm',
        widget=forms.Select(attrs={'class': 'border rounded px-2 py-1'})
    )
    diem_hd_nk = forms.IntegerField(
        label='Điểm',
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'w-16 border rounded-md px-2 py-1'})
    )

    class Meta:
        model = HoatDongNgoaiKhoa
        fields = ['ten_hd_nk', 'thoi_gian', 'dia_diem', 'mo_ta_hd_nk', 'so_luong', 'diem_hd_nk', 'muc_diem_nk']
        labels = {
            'ten_hd_nk': 'Tên ngoại khóa',
            'diem_hd_nk': 'Điểm',
            'muc_diem_nk': 'Mục điểm',
            'thoi_gian': 'Thời gian',
            'dia_diem': 'Địa điểm',
            'so_luong': 'Số lượng',
            'mo_ta_hd_nk': 'Thông tin chi tiết',
        }
        widgets = {
            'mo_ta_hd_nk': forms.Textarea(attrs={'rows': 5, 'class': 'w-full border rounded-md px-4 py-2'}),
            'thoi_gian': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'flex-1 border rounded-md px-4 py-2'}),
            'ten_hd_nk': forms.TextInput(attrs={'class': 'flex-1 border rounded-md px-4 py-2'}),
            'dia_diem': forms.TextInput(attrs={'class': 'flex-1 border rounded-md px-4 py-2'}),
            'so_luong': forms.NumberInput(attrs={'class': 'flex-1 border rounded-md px-4 py-2'}),
            'diem_hd_nk': forms.NumberInput(attrs={'class': 'w-16 border rounded-md px-2 py-1'}),
        }

