from django import forms
from .models import TinNhan, Nhom, Post, TaiKhoan, BaiViet, BinhLuan, HoatDongNgoaiKhoa

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Chọn file để import dữ liệu")

class GroupForm(forms.ModelForm):
    """Form để tạo và chỉnh sửa nhóm"""
    class Meta:
        model = Nhom
        fields = ['TenNhom', 'MoTa']
        widgets = {
            'TenNhom': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'MoTa': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 4}),
        }

class PostForm(forms.ModelForm):
    """Form để tạo bài viết trong nhóm"""
    class Meta:
        model = Post
        fields = ['content', 'image', 'file']
        widgets = {
            'content': forms.Textarea(
                attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 3, 'placeholder': 'Hãy đăng bài viết!'}),
            'image': forms.FileInput(attrs={'class': 'hidden', 'id': 'image-upload'}),
            'file': forms.FileInput(attrs={'class': 'hidden', 'id': 'file-upload'}),
        }

class BaiVietForm(forms.ModelForm):
    """Form để tạo bài viết"""
    class Meta:
        model = BaiViet
        fields = ['NoiDung']
        widgets = {
            'NoiDung': forms.Textarea(
                attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 3, 'placeholder': 'Hãy đăng bài viết!'}),
        }

class BinhLuanForm(forms.ModelForm):
    """Form để bình luận"""
    class Meta:
        model = BinhLuan
        fields = ['NoiDung']
        widgets = {
            'NoiDung': forms.Textarea(
                attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 2, 'placeholder': 'Viết bình luận...'}),
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
            self.fields['user_ids'].choices = [(user.MaTaiKhoan, user.Email) for user in users]

class TinNhanForm(forms.ModelForm):
    """Form để gửi tin nhắn"""
    class Meta:
        model = TinNhan
        fields = ['NoiDung']
        widgets = {
            'NoiDung': forms.Textarea(attrs={'placeholder': 'Aa', 'class': 'flex-1 bg-transparent px-3 py-2 focus:outline-none'}),
        }

class LoginForm(forms.Form):
    """Form đăng nhập"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
    )

class RegisterForm(forms.Form):
    """Form đăng ký"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Xác nhận mật khẩu'
        })
    )
    ho_ten = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Họ tên'
        }),
        required=True,
        error_messages={'required': 'Vui lòng nhập họ tên.'}
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        ho_ten = cleaned_data.get('ho_ten')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Mật khẩu và xác nhận mật khẩu không khớp.")

        if ho_ten and len(ho_ten.strip()) == 0:
            raise forms.ValidationError("Họ tên không được để trống.")

        return cleaned_data

class ExtracurricularForm(forms.ModelForm):
    """Form để tạo và chỉnh sửa hoạt động ngoại khóa"""
    class Meta:
        model = HoatDongNgoaiKhoa
        fields = ['ten_hd_nk', 'thoi_gian', 'dia_diem', 'mo_ta_hd_nk', 'so_luong', 'diem_hd_nk', 'muc_diem_nk']
        widgets = {
            'ten_hd_nk': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'thoi_gian': forms.DateTimeInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'type': 'datetime-local'}),
            'dia_diem': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'mo_ta_hd_nk': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 4}),
            'so_luong': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'diem_hd_nk': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'muc_diem_nk': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }