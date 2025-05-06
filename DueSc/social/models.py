from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.shortcuts import render, redirect
from pyexpat.errors import messages


# Mô hình Người dùng (NguoiDung)
class NguoiDung(models.Model):
    ma_nguoi_dung = models.AutoField(primary_key=True)
    ma_tai_khoan = models.IntegerField(unique=True, null=True)  # Chỉ giữ một định nghĩa
    ho_ten = models.CharField(max_length=100, blank=True, null=True,
    help_text="Họ tên người dùng")  # Thêm trường ho_ten
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
       max_length=3,  # Đổi thành 3 để chứa giá trị như "III"
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
    MaNguoiDung = models.ForeignKey('TaiKhoan', on_delete=models.CASCADE, verbose_name="Mã người dùng")  # Sửa từ User thành TaiKhoan
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

# Mô hình HoiThoai (HoiThoai)
class HoiThoai(models.Model):
   MaHoiThoai = models.AutoField(primary_key=True)
   TenHoiThoai = models.CharField(max_length=200)
   ThoiGianTao = models.DateTimeField(auto_now_add=True)
   LoaiHoiThoai = models.CharField(max_length=50)
   ThanhVien = models.ManyToManyField('TaiKhoan', related_name='hoi_thoai')


   def __str__(self):
       return self.TenHoiThoai


# Mô hình TinNhan (TinNhan)
class TinNhan(models.Model):
   MaTinNhan = models.AutoField(primary_key=True)
   NoiDung = models.TextField()
   ThoiGian = models.DateTimeField(auto_now_add=True)  # Tự động thêm thời gian gửi
   MaHoiThoai = models.ForeignKey(HoiThoai, on_delete=models.CASCADE, related_name='tin_nhan')
   MaNguoiGui = models.ForeignKey('TaiKhoan', on_delete=models.CASCADE, related_name='tin_nhan_gui')


   def __str__(self):
       return f"Tin nhắn từ {self.MaNguoiGui} trong {self.MaHoiThoai}"


# Mô hình TaiKhoan (TaiKhoan)
class TaiKhoan(models.Model):
    MaTaiKhoan = models.AutoField(primary_key=True)
    Email = models.EmailField(unique=True)
    MatKhau = models.CharField(max_length=255)
    MaNguoiDung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='nguoi_dung')
    is_active = models.BooleanField(default=True)
    is_sinhvien = models.BooleanField(default=False)  # Thêm trường
    is_giangvien = models.BooleanField(default=False)  # Thêm trường
    is_quantrivien_nhom = models.BooleanField(default=False)  # Thêm trường

    def __str__(self):
        return self.Email

    @property
    def is_authenticated(self):
        return True  # User đã đăng nhập

    @property
    def is_anonymous(self):
        return False  # Không phải AnonymousUser

# Mô hình BaiViet (BaiViet)
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


# Mô hình CamXuc (CamXuc)
class CamXuc(models.Model):
   MaBaiViet = models.ForeignKey(BaiViet, on_delete=models.CASCADE, related_name='cam_xuc')
   MaNguoiDung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='cam_xuc')
   LoaiCamXuc = models.CharField(max_length=50)
   ThoiGian = models.DateTimeField(default=timezone.now)


   class Meta:
       unique_together = ('MaBaiViet', 'MaNguoiDung')


   def __str__(self):
       return f"Cảm xúc của {self.MaNguoiDung.ho_ten} - {self.MaBaiViet.NoiDung}"


# Mô hình BinhLuan (BinhLuan)
class BinhLuan(models.Model):
   MaBinhLuan = models.AutoField(primary_key=True)
   MaBaiViet = models.ForeignKey(BaiViet, on_delete=models.CASCADE, related_name='binh_luan')
   MaNguoiDung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='binh_luan')
   NoiDung = models.TextField()
   ThoiGianDang = models.DateTimeField(default=timezone.now)


   def __str__(self):
       return f"Bình luận của {self.MaNguoiDung.ho_ten} lúc {self.ThoiGianDang}"


# Mô hình Nhom (Nhom)
class Nhom(models.Model):
   ma_nhom = models.AutoField(primary_key=True)
   ten_nhom = models.CharField(max_length=255)
   thoi_gian_tao = models.DateTimeField(auto_now_add=True)
   so_luong_thanh_vien = models.IntegerField(default=0)
   trang_thai_nhom = models.CharField(max_length=10, choices=[('Chờ duyệt', 'Chờ duyệt'), ('Được duyệt', 'Được duyệt'),
                                                        ('Từ chối', 'Từ chối'), ('Bị xóa', 'Bị xóa')])


   def __str__(self):
       return self.ten_nhom


# Mô hình ThanhVienNhom (ThanhVienNhom)
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
       return f"{self.ma_nguoi_dung.ho_ten} - {self.ma_nhom.ten_nhom}"


from django.db import models

class Stadium(models.Model):
    name = models.CharField(max_length=200)  # Tên sân bóng
    description = models.TextField()  # Mô tả sân bóng
    image = models.ImageField(upload_to='stadium_images/', null=True, blank=True)  # Hình ảnh sân


    def __str__(self):
        return self.name

from django.db import models


from django.db import models

class Booking(models.Model):
    date = models.DateField()
    time = models.TimeField()
    is_canceled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.time.strftime('%H:%M')} - {self.date.strftime('%d/%m/%Y')}"


# Thêm vào models.py
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    user = models.ForeignKey('TaiKhoan', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    video = models.FileField(upload_to='post_videos/', null=True, blank=True)
    file = models.FileField(upload_to='post_files/', null=True, blank=True)
    post_type = models.CharField(max_length=20, choices=[
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
        ('poll', 'Poll')
    ], default='text')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.MaNguoiDung.ho_ten}: {self.content[:50]}"

    def get_time_display(self):
        from django.utils.timesince import timesince
        return timesince(self.created_at)

# Login
import random
import string
from django.utils import timezone
from datetime import timedelta


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
# View xác thực OTP đăng ký
def verify_register_otp_view(request):
    if 'register_email' not in request.session:
        messages.error(request, 'Không tìm thấy thông tin đăng ký. Vui lòng đăng ký lại.')
        return redirect('register')

    if request.method == 'POST':
        otp_digits = [request.POST.get(f'otp{i}', '') for i in range(1, 5)]
        entered_otp = ''.join(otp_digits)

        try:
            pending_reg = PendingRegistration.objects.get(email=request.session['register_email'], is_verified=False)

            if not pending_reg.is_valid():
                messages.error(request, 'Mã OTP đã hết hạn. Vui lòng đăng ký lại.')
                pending_reg.delete()
                del request.session['register_email']
                return redirect('register')

            if pending_reg.otp_code != entered_otp:
                messages.error(request, 'Mã OTP không chính xác. Vui lòng thử lại.')
                return render(request, 'social/login/verify_register_otp.html')

            nguoi_dung = NguoiDung.objects.create(
                ma_tai_khoan=None
            )
            tai_khoan = TaiKhoan.objects.create(
                Email=pending_reg.email,
                MatKhau=pending_reg.password,
                MaNguoiDung=nguoi_dung
            )
            nguoi_dung.ma_tai_khoan = tai_khoan.MaTaiKhoan
            nguoi_dung.save()

            pending_reg.is_verified = True
            pending_reg.save()
            del request.session['register_email']
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect('login')

        except PendingRegistration.DoesNotExist:
            messages.error(request, 'Không tìm thấy thông tin đăng ký hoặc đã hết hạn.')
            return redirect('register')

    return render(request, 'social/login/verify_register_otp.html')
# đăng ký
from django.contrib.auth.hashers import make_password

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

# models.py
from django.db import models

class ConfirmedSchedule(models.Model):
    student_id = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='confirmed')

    def __str__(self):
        return f"{self.name} - {self.location} (Confirmed)"
class PendingSchedule(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    student_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.location}"


class Like(models.Model):
    user = models.ForeignKey('TaiKhoan', on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.MaNguoiDung.ho_ten} liked {self.post}"

class Comment(models.Model):
    user = models.ForeignKey('TaiKhoan', on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.MaNguoiDung.ho_ten} commented on {self.post}"



class PollOption(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='poll_options')
    text = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.text} ({self.votes} votes)"
