from django import forms
from .models import TinNhan, Nhom, BaiViet, BinhLuan, HoatDongNgoaiKhoa, NguoiDung

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Chọn file để import dữ liệu")

class GroupForm(forms.ModelForm):
    """Form để tạo và chỉnh sửa nhóm"""
    class Meta:
        model = Nhom
        fields = ['ten_nhom', 'mo_ta']  # Đổi 'TenNhom' thành 'ten_nhom', 'MoTa' thành 'mo_ta'
        widgets = {
            'ten_nhom': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'mo_ta': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 4}),
        }

from django import forms
from .models import BaiViet

class PostForm(forms.ModelForm):
    """Form để tạo bài viết"""
    class Meta:
        model = BaiViet
        fields = ['noi_dung', 'image', 'video', 'file']
        widgets = {
            'noi_dung': forms.Textarea(
                attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 3, 'placeholder': 'Hãy đăng bài viết!'}
            ),
        }




class BinhLuanForm(forms.ModelForm):
    """Form để bình luận"""
    class Meta:
        model = BinhLuan
        fields = ['noi_dung']  # Đổi 'NoiDung' thành 'noi_dung'
        widgets = {
            'noi_dung': forms.Textarea(
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
            self.fields['user_ids'].choices = [(user.user.id, user.email) for user in users]  # Đổi 'MaTaiKhoan' thành 'user.id', 'Email' thành 'email'

class TinNhanForm(forms.ModelForm):
    """Form để gửi tin nhắn"""
    class Meta:
        model = TinNhan
        fields = ['noi_dung']
        widgets = {
            'noi_dung': forms.Textarea(attrs={'placeholder': 'Aa', 'class': 'flex-1 bg-transparent px-3 py-2 focus:outline-none'}),
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

from django import forms
from .models import HoatDongNgoaiKhoa
from django.utils import timezone
from django.core.exceptions import ValidationError


from django.utils import timezone

class ExtracurricularForm(forms.ModelForm):
    class Meta:
        model = HoatDongNgoaiKhoa
        fields = ['ten_hd_nk', 'quyen_loi', 'muc', 'thoi_gian', 'dia_diem', 'so_luong', 'thong_tin_chi_tiet']
        labels = {
            'ten_hd_nk': 'Tên ngoại khóa',
            'quyen_loi': 'Điểm',
            'muc': 'Mục điểm',
            'thoi_gian': 'Thời gian',
            'dia_diem': 'Địa điểm',
            'so_luong': 'Số lượng',
            'thong_tin_chi_tiet': 'Thông tin chi tiết',
        }
        widgets = {
            'ten_hd_nk': forms.TextInput(attrs={'class': 'flex-1 border rounded-md px-4 py-2'}),
            'quyen_loi': forms.Select(attrs={'class': 'w-32 border rounded-md px-2 py-1'}),
            'muc': forms.Select(attrs={'class': 'border rounded-md px-2 py-1'}),
            'thoi_gian': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'flex-1 border rounded-md px-4 py-2'}),
            'dia_diem': forms.TextInput(attrs={'class': 'flex-1 border rounded-md px-4 py-2'}),
            'so_luong': forms.NumberInput(attrs={'class': 'flex-1 border rounded-md px-4 py-2'}),
            'thong_tin_chi_tiet': forms.Textarea(attrs={'rows': 5, 'class': 'w-full border rounded-md px-4 py-2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now_local = timezone.localtime(timezone.now()).strftime("%Y-%m-%dT%H:%M")
        self.fields['thoi_gian'].widget.attrs['min'] = now_local



