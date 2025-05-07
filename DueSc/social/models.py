from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import random
import string
from datetime import timedelta

from django.shortcuts import render, redirect
from pyexpat.errors import messages

# Mô hình Người dùng (NguoiDung)
class NguoiDung(models.Model):
    ma_nguoi_dung = models.AutoField(primary_key=True)
    ho_ten = models.CharField(max_length=100, blank=True, null=True, help_text="Họ tên người dùng")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, help_text="Ảnh đại diện")
    def __str__(self):
        return self.ho_ten if self.ho_ten else f"Người dùng {self.ma_nguoi_dung}"

# Mô hình Hoạt động ngoại khóa (HoatDongNgoaiKhoa)
class HoatDongNgoaiKhoa(models.Model):
    class MucDiemChoices(models.TextChoices):
        I = "I", "I"
        II = "II", "II"
        III = "III", "III"
        IV = "IV", "IV"

    ma_nk = models.AutoField(primary_key=True)
    ten_hd_nk = models.CharField(max_length=255, help_text="Tên ngoại khóa.")
    thoi_gian = models.DateTimeField(help_text="Thời gian diễn ra hoạt động.")
    dia_diem = models.CharField(max_length=255, help_text="Địa điểm tổ chức hoạt động.")
    mo_ta_hd_nk = models.TextField(blank=True, null=True, help_text="Mô tả chi tiết về hoạt động.")
    so_luong = models.IntegerField(default=0, help_text="Số lượng người tham gia hoạt động.")
    diem_hd_nk = models.FloatField(default=0, help_text="Điểm số của hoạt động ngoại khóa.")
    muc_diem_nk = models.CharField(
        max_length=3,
        choices=MucDiemChoices.choices,
        help_text="Mức điểm đạt được (I, II, III, IV)."
    )
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, help_text="Người tạo ngoại khoá.")

    def __str__(self):
        return f"{self.ten_hd_nk} - {self.nguoi_dung.ho_ten}"

# Mô hình Đăng ký Hoạt động Ngoại khóa (DKNgoaiKhoa)
class DKNgoaiKhoa(models.Model):
    class TrangThai(models.TextChoices):
        DA_THAM_GIA = "DA_THAM_GIA", "Đã tham gia"
        KHONG_THAM_GIA = "KHONG_THAM_GIA", "Không tham gia"

    ma_hd_nk = models.ForeignKey(HoatDongNgoaiKhoa, on_delete=models.CASCADE, help_text="Mã hoạt động ngoại khóa.")
    ma_sv = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, help_text="Mã sinh viên đăng ký hoạt động.")
    thoi_gian_dk = models.DateTimeField(auto_now_add=True, help_text="Thời gian sinh viên đăng ký hoạt động.")
    trang_thai = models.CharField(max_length=20, choices=TrangThai.choices, help_text="Trạng thái đăng ký hoạt động.")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ma_hd_nk', 'ma_sv'], name='unique_dk_hoatdong')
        ]

    def __str__(self):
        return f"{self.ma_sv.ho_ten} - {self.ma_hd_nk.ten_hd_nk} ({self.get_trang_thai_display()})"

# Mô hình Dịch vụ công (DichVuCong)
class DichVuCong(models.Model):
    MaDV = models.AutoField(primary_key=True)
    TenDichVu = models.CharField(max_length=255, verbose_name="Tên dịch vụ")

    def __str__(self):
        return self.TenDichVu

# Mô hình Đặt lịch (DatLich)
class DatLich(models.Model):
    class TrangThaiChoices(models.TextChoices):
        DA_DUYET = "Đã duyệt", "Đã duyệt"
        TU_CHOI = "Từ chối", "Từ chối"

    MaDatLich = models.AutoField(primary_key=True)
    MaNguoiDung = models.ForeignKey('TaiKhoan', on_delete=models.CASCADE, verbose_name="Mã người dùng")
    NgayDatLich = models.DateField(verbose_name="Ngày đặt lịch")
    GioDatLich = models.TimeField(verbose_name="Giờ đặt lịch")
    TrangThai = models.CharField(max_length=20, choices=TrangThaiChoices.choices, verbose_name="Trạng thái")
    MaDV = models.ForeignKey(DichVuCong, on_delete=models.CASCADE, verbose_name="Mã dịch vụ")

    def save(self, *args, **kwargs):
        existing_schedule = DatLich.objects.filter(NgayDatLich=self.NgayDatLich, GioDatLich=self.GioDatLich).exists()
        if existing_schedule:
            self.TrangThai = self.TrangThaiChoices.TU_CHOI
        else:
            self.TrangThai = self.TrangThaiChoices.DA_DUYET
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Lịch {self.MaDatLich} - {self.MaNguoiDung.Email}"

class Stadium(models.Model):
    name = models.CharField(max_length=200)  # Tên sân bóng
    description = models.TextField()  # Mô tả sân bóng
    image = models.ImageField(upload_to='stadium_images/', null=True, blank=True)  # Hình ảnh sân

    def __str__(self):
        return self.name

class Booking(models.Model):
    date = models.DateField()
    time = models.TimeField()
    is_canceled = models.BooleanField(default=False)
    location = models.CharField(max_length=255)  # Thêm trường location

    def __str__(self):
        return f"{self.time.strftime('%H:%M')} - {self.date.strftime('%d/%m/%Y')} at {self.location}"

# Mô hình Hội thoại (HoiThoai)
class HoiThoai(models.Model):
    class LoaiHoiThoaiChoices(models.TextChoices):
        CA_NHAN = "Cá nhân", "Cá nhân"
        NHOM = "Nhóm", "Nhóm"

    MaHoiThoai = models.AutoField(primary_key=True)
    TenHoiThoai = models.CharField(max_length=200, blank=True)
    ThoiGianTao = models.DateTimeField(auto_now_add=True)
    LoaiHoiThoai = models.CharField(max_length=50, choices=LoaiHoiThoaiChoices.choices, default=LoaiHoiThoaiChoices.CA_NHAN)
    ThanhVien = models.ManyToManyField('TaiKhoan', related_name='hoi_thoai')

    def __str__(self):
        return self.TenHoiThoai or f"Hội thoại {self.MaHoiThoai}"

# Mô hình Tin nhắn (TinNhan)
class TinNhan(models.Model):
    MaTinNhan = models.AutoField(primary_key=True)
    NoiDung = models.TextField()
    ThoiGian = models.DateTimeField(auto_now_add=True)
    MaHoiThoai = models.ForeignKey(HoiThoai, on_delete=models.CASCADE, related_name='tin_nhan')
    MaNguoiGui = models.ForeignKey('TaiKhoan', on_delete=models.CASCADE, related_name='tin_nhan_gui')

    def __str__(self):
        return f"Tin nhắn từ {self.MaNguoiGui} trong {self.MaHoiThoai}"

# Mô hình Tài khoản (TaiKhoan)
class TaiKhoan(models.Model):
    MaTaiKhoan = models.AutoField(primary_key=True)
    Email = models.EmailField(unique=True)
    MatKhau = models.CharField(max_length=255)
    DiemHDNK = models.IntegerField(default=0)
    MaNguoiDung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='nguoi_dung')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    is_sinhvien = models.BooleanField(default=False)
    is_giangvien = models.BooleanField(default=False)
    is_quantrivien_nhom = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.Email

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

# Mô hình Bài viết (BaiViet)
class BaiViet(models.Model):
    MaBaiViet = models.AutoField(primary_key=True)
    NoiDung = models.TextField()
    ThoiGianDang = models.DateTimeField(default=timezone.now)
    SoLuongCamXuc = models.IntegerField(default=0)
    TrangThai = models.BooleanField(default=True)
    MaNhom = models.ForeignKey('Nhom', on_delete=models.SET_NULL, related_name='bai_viet', null=True, blank=True)
    MaNguoiDung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='bai_viet')

    def __str__(self):
        return f"Bài viết của {self.MaNguoiDung.ho_ten} lúc {self.ThoiGianDang}"

    def xoa_bai_viet(self):
        self.TrangThai = False
        self.save()

    def is_active(self):
        return self.TrangThai

# Mô hình Cảm xúc (CamXuc)
class CamXuc(models.Model):
    MaBaiViet = models.ForeignKey(BaiViet, on_delete=models.CASCADE, related_name='cam_xuc')
    MaNguoiDung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='cam_xuc')
    LoaiCamXuc = models.CharField(max_length=50)
    ThoiGian = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('MaBaiViet', 'MaNguoiDung')

    def __str__(self):
        return f"{self.MaNguoiDung.ho_ten} - {self.LoaiCamXuc} - {self.MaBaiViet}"

# Mô hình Bình luận (BinhLuan)
class BinhLuan(models.Model):
    MaBinhLuan = models.AutoField(primary_key=True)
    MaBaiViet = models.ForeignKey(BaiViet, on_delete=models.CASCADE, related_name='binh_luan')
    MaNguoiDung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='binh_luan')
    NoiDung = models.TextField()
    ThoiGianDang = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Bình luận của {self.MaNguoiDung.ho_ten} lúc {self.ThoiGianDang}"

# Mô hình Nhóm (Nhom)
class Nhom(models.Model):
    MaNhom = models.AutoField(primary_key=True)
    TenNhom = models.CharField(max_length=200)
    MoTa = models.TextField(blank=True, null=True)
    ThoiGianTao = models.DateTimeField(auto_now_add=True)
    QuanTriVien = models.ForeignKey('TaiKhoan', on_delete=models.CASCADE, related_name='nhom_quan_tri')
    ThanhVien = models.ManyToManyField('TaiKhoan', related_name='nhom_thanh_vien')

    def __str__(self):
        return self.TenNhom

# Mô hình Thành viên nhóm (ThanhVienNhom)
class ThanhVienNhom(models.Model):
    ma_nhom = models.ForeignKey(Nhom, on_delete=models.CASCADE)
    ma_nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    vai_tro = models.CharField(max_length=50, choices=[('Quản trị viên', 'Quản trị viên'), ('Thành viên', 'Thành viên')])
    thoi_gian_tham_gia = models.DateTimeField(auto_now_add=True)
    trang_thai = models.CharField(max_length=10, choices=[('Chờ duyệt', 'Chờ duyệt'), ('Được duyệt', 'Được duyệt'),
                                                          ('Từ chối', 'Từ chối'), ('Bị xóa', 'Bị xóa')])

    class Meta:
        unique_together = ('ma_nhom', 'ma_nguoi_dung')

    def __str__(self):
        return f"{self.ma_nguoi_dung.ho_ten} - {self.ma_nhom.TenNhom}"

# Mô hình Bài đăng (Post)
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    video = models.FileField(upload_to='post_videos/', null=True, blank=True)
    file = models.FileField(upload_to='post_files/', null=True, blank=True)
    post_type = models.CharField(max_length=20, default='text')

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"

    def get_time_display(self):
        from django.utils.timesince import timesince
        return timesince(self.created_at)

# Mô hình OTP
class OTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = ''.join(random.choices(string.digits, k=4))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def __str__(self):
        return f"OTP for {self.email}"

# Mô hình Đăng ký chờ (PendingRegistration)
class PendingRegistration(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    ho_ten = models.CharField(max_length=100, blank=True, null=True)
    otp_code = models.CharField(max_length=4)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = ''.join(random.choices(string.digits, k=4))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=30)
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_verified and timezone.now() <= self.expires_at

# Mô hình Lịch chờ duyệt (PendingSchedule)
class PendingSchedule(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"{self.name} - {self.location}"

# Mô hình Lịch đã xác nhận (ConfirmedSchedule)
class ConfirmedSchedule(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='confirmed')

    def __str__(self):
        return f"{self.name} - {self.location} (Confirmed)"

# Mô hình Thích (Like)
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} likes {self.post}"

# Mô hình Bình luận (Comment)
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"

# Mô hình Tùy chọn thăm dò (PollOption)
class PollOption(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.text} ({self.votes} votes)"

# Mô hình Thông báo (ThongBao)
class ThongBao(models.Model):
    NguoiNhan = models.ForeignKey('TaiKhoan', on_delete=models.CASCADE)
    NoiDung = models.TextField()
    ThoiGian = models.DateTimeField(auto_now_add=True)
    DaDoc = models.BooleanField(default=False)

    def __str__(self):
        return f"Thông báo cho {self.NguoiNhan.Email}: {self.NoiDung}"