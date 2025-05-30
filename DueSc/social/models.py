from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import random
import string

# Validator để kiểm tra email
def validate_email_domain(email):
    if email.endswith('@gmail.com') or email.endswith('@due.udn.vn'):
        return email
    raise ValidationError('Email phải có đuôi @gmail.com (admin) hoặc @due.udn.vn (sinh viên).')

# Validator để kiểm tra email sinh viên
def validate_student_email(email):
    if not email.endswith('@due.udn.vn'):
        raise ValidationError('Chỉ chấp nhận email sinh viên (@due.udn.vn) để đăng ký.')

# Model cho người dùng
class NguoiDung(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    ho_ten = models.CharField(max_length=100, blank=False)
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(), validate_email_domain]
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    diem_ngoai_khoa = models.PositiveIntegerField(default=0, blank=True, null=True)
    diem_muc_i = models.PositiveIntegerField(default=0, blank=True, null=True)
    diem_muc_ii = models.PositiveIntegerField(default=0, blank=True, null=True)
    diem_muc_iii = models.PositiveIntegerField(default=0, blank=True, null=True)
    diem_muc_iv = models.PositiveIntegerField(default=0, blank=True, null=True)
    vai_tro = models.CharField(
        max_length=20,
        choices=[('Admin', 'Admin'), ('SinhVien', 'Sinh viên')],
        blank=True
    )

    def save(self, *args, **kwargs):
        if self.email.endswith('@gmail.com'):
            self.vai_tro = 'Admin'
            self.diem_ngoai_khoa = None
            self.diem_muc_i = None
            self.diem_muc_ii = None
            self.diem_muc_iii = None
            self.diem_muc_iv = None
        elif self.email.endswith('@due.udn.vn'):
            self.vai_tro = 'SinhVien'
            if self.diem_ngoai_khoa is None:
                self.diem_ngoai_khoa = 0
            if self.diem_muc_i is None:
                self.diem_muc_i = 0
            if self.diem_muc_ii is None:
                self.diem_muc_ii = 0
            if self.diem_muc_iii is None:
                self.diem_muc_iii = 0
            if self.diem_muc_iv is None:
                self.diem_muc_iv = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ho_ten} ({self.email})"

# Model cho đăng ký tạm thời
class PendingRegistration(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    ho_ten = models.CharField(max_length=100, blank=False)
    otp_code = models.CharField(max_length=4, default=''.join(random.choices(string.digits, k=4)))
    expires_at = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=10))
    is_verified = models.BooleanField(default=False)

    def is_valid(self):
        return timezone.now() <= self.expires_at and not self.is_verified

    def verify_and_create_user(self):
        if self.is_valid():
            self.is_verified = True
            self.save()

            user, created = User.objects.get_or_create(username=self.email, defaults={'email': self.email})
            user.set_password(self.password)  # Đặt mật khẩu cho user
            user.save()
            nguoi_dung, nguoi_created = NguoiDung.objects.get_or_create(
                user=user,
                defaults={
                    'ho_ten': self.ho_ten,  # Lấy ho_ten từ PendingRegistration
                    'email': self.email
                }
            )
            if not nguoi_created:
                nguoi_dung.ho_ten = self.ho_ten  # Cập nhật ho_ten nếu đã tồn tại
                nguoi_dung.save()
            return user
        return None

    def __str__(self):
        return f"Đăng ký tạm thời cho {self.email}"

# Tín hiệu để xử lý khi is_verified thay đổi
@receiver(post_save, sender=PendingRegistration)
def create_user_from_pending(sender, instance, **kwargs):
    if instance.is_verified:
        instance.verify_and_create_user()

class BaiViet(models.Model):
    ma_nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='bai_viet')
    noi_dung = models.TextField()
    thoi_gian_dang = models.DateTimeField(auto_now_add=True)
    ma_nhom = models.ForeignKey('Nhom', on_delete=models.CASCADE, null=True, blank=True, related_name='bai_viet')
    trang_thai = models.CharField(
        max_length=20,
        choices=[('ChoDuyet', 'Chờ duyệt'), ('DaDuyet', 'Đã duyệt')],
        default='DaDuyet'  # Bài viết công khai mặc định đã duyệt
    )
    post_type = models.CharField(
        max_length=20,
        choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video'), ('file', 'File'), ('poll', 'Poll')],
        default='text'
    )
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    video = models.FileField(upload_to='post_videos/', null=True, blank=True)
    file = models.FileField(upload_to='post_files/', null=True, blank=True)

    def __str__(self):
        return f"Bài viết của {self.ma_nguoi_dung.ho_ten} tại {self.thoi_gian_dang}"
#lưu trữ các lựa chọn
class PollOption(models.Model):
    bai_viet = models.ForeignKey(BaiViet, on_delete=models.CASCADE, related_name='poll_options')
    text = models.CharField(max_length=200)
    votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.text} ({self.votes} votes)"
#lưu trữ thông tin về lượt vote
class PollVote(models.Model):
    bai_viet = models.ForeignKey(BaiViet, on_delete=models.CASCADE, related_name='poll_votes')
    ma_nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)

# Model cho cảm xúc (like)
class CamXuc(models.Model):
    ma_bai_viet = models.ForeignKey(BaiViet, on_delete=models.CASCADE, related_name='cam_xuc')
    ma_nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    thoi_gian = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ma_bai_viet', 'ma_nguoi_dung')

    def __str__(self):
        return f"{self.ma_nguoi_dung.ho_ten} thích bài viết {self.ma_bai_viet.id}"

# Model cho bình luận
class BinhLuan(models.Model):
    ma_bai_viet = models.ForeignKey(BaiViet, on_delete=models.CASCADE, related_name='binh_luan')
    ma_nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    noi_dung = models.TextField()
    thoi_gian = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bình luận của {self.ma_nguoi_dung.ho_ten} trên bài viết {self.ma_bai_viet.id}"

# Model cho hội thoại (tin nhắn)
class HoiThoai(models.Model):
    ten_hoi_thoai = models.CharField(max_length=100, blank=True)
    la_nhom = models.BooleanField(default=False)
    thanh_vien = models.ManyToManyField(NguoiDung, related_name='hoi_thoai')
    cap_nhat_thoi_gian = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.ten_hoi_thoai or f"Hội thoại {self.id}"

# Model cho tin nhắn
class TinNhan(models.Model):
    ma_hoi_thoai = models.ForeignKey(HoiThoai, on_delete=models.CASCADE, related_name='tin_nhan')
    ma_nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    noi_dung = models.TextField()
    thoi_gian = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tin nhắn của {self.ma_nguoi_dung.ho_ten} trong hội thoại {self.ma_hoi_thoai.id}"

# Model cho nhóm
class Nhom(models.Model):
    ten_nhom = models.CharField(max_length=100)
    mo_ta = models.TextField(blank=True)
    trang_thai = models.CharField(
        max_length=20,
        choices=[('ChoDuyet', 'Chờ duyệt'), ('DaDuyet', 'Đã duyệt')],
        default='ChoDuyet'
    )
    trang_thai_nhom = models.CharField(
        max_length=20,
        choices=[('CongKhai', 'Công khai'), ('RiengTu', 'Riêng tư')],
        default='RiengTu'
    )
    ngay_tao = models.DateTimeField(auto_now_add=True)
    nguoi_tao = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='nhom_tao')
    avatar = models.ImageField(upload_to='group_avatars/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='group_covers/', null=True, blank=True)

    def __str__(self):
        return self.ten_nhom

# Model cho thành viên nhóm
class ThanhVienNhom(models.Model):
    ma_nhom = models.ForeignKey(Nhom, on_delete=models.CASCADE, related_name='thanh_vien')
    ma_nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    trang_thai = models.CharField(
        max_length=20,
        choices=[('ChoDuyet', 'Chờ duyệt'), ('DuocDuyet', 'Được duyệt')],
        default='ChoDuyet'
    )
    la_quan_tri_vien = models.BooleanField(default=False)

    class Meta:
        unique_together = ('ma_nhom', 'ma_nguoi_dung')

    def __str__(self):
        return f"{self.ma_nguoi_dung.ho_ten} trong nhóm {self.ma_nhom.ten_nhom}"

# Model cho lời mời tham gia nhóm
class LoiMoiNhom(models.Model):
    ma_nhom = models.ForeignKey(Nhom, on_delete=models.CASCADE, related_name='loi_moi')
    ma_nguoi_gui = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='loi_moi_gui')
    ma_nguoi_nhan = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='loi_moi_nhan')
    trang_thai = models.CharField(
        max_length=20,
        choices=[('ChoDuyet', 'Chờ duyệt'), ('DaDuyet', 'Đã duyệt'), ('TuChoi', 'Từ chối')],
        default='ChoDuyet'
    )
    thoi_gian_gui = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ma_nhom', 'ma_nguoi_nhan')

    def __str__(self):
        return f"Lời mời từ {self.ma_nguoi_gui.ho_ten} đến {self.ma_nguoi_nhan.ho_ten} cho nhóm {self.ma_nhom.ten_nhom}"

# Model cho sân thể thao
class San(models.Model):
    ten_san = models.CharField(max_length=100)
    mo_ta = models.TextField(blank=True)
    hinh_anh = models.ImageField(upload_to='san/', null=True, blank=True)

    def __str__(self):
        return self.ten_san

# Model cho lịch đặt sân
class DatLich(models.Model):
    ma_san = models.ForeignKey(San, on_delete=models.CASCADE, related_name='lich_dat')
    ma_nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    ngay = models.DateField()
    gio_bat_dau = models.TimeField()
    trang_thai = models.CharField(
        max_length=20,
        choices=[('ChoDuyet', 'Chờ duyệt'), ('XacNhan', 'Xác nhận'), ('Huy', 'Hủy')],
        default='ChoDuyet'
    )
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ma_san', 'ngay', 'gio_bat_dau')

    def clean(self):
        # Kiểm tra slot thời gian đã được đặt chưa
        if self.trang_thai != 'Huy':
            existing = DatLich.objects.filter(
                ma_san=self.ma_san,
                ngay=self.ngay,
                gio_bat_dau=self.gio_bat_dau,
                trang_thai__in=['ChoDuyet', 'XacNhan']
            ).exclude(id=self.id)
            if existing.exists():
                raise ValidationError('Slot thời gian này đã được đặt.')

    def __str__(self):
        return f"Lịch đặt {self.ma_san.ten_san} bởi {self.ma_nguoi_dung.ho_ten} vào {self.ngay} {self.gio_bat_dau}"

# Model cho hoạt động ngoại khóa
class HoatDongNgoaiKhoa(models.Model):
    ten_hd_nk = models.CharField(max_length=200)
    quyen_loi = models.CharField(
        max_length=20,
        choices=[('Cong10', 'Cộng 10 điểm'), ('Cong15', 'Cộng 15 điểm'), ('Cong20', 'Cộng 20 điểm')]
    )
    muc = models.CharField(
        max_length=10,
        choices=[('I', 'Mục I'), ('II', 'Mục II'), ('III', 'Mục III'), ('IV', 'Mục IV')]
    )
    thoi_gian = models.DateTimeField()
    dia_diem = models.CharField(max_length=200)
    so_luong = models.PositiveIntegerField()
    thong_tin_chi_tiet = models.TextField()
    nguoi_tao = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='hoat_dong_tao')

    def clean(self):
        # Kiểm tra số lượng đăng ký không vượt quá số lượng tối đa
        if self.id:
            so_luong_dk = DKNgoaiKhoa.objects.filter(ma_hd_nk=self, trang_thai='DangKy').count()
            if so_luong_dk > self.so_luong:
                raise ValidationError('Số lượng đăng ký đã vượt quá số lượng tối đa.')

    def __str__(self):
        return self.ten_hd_nk

# Model cho đăng ký ngoại khóa
class DKNgoaiKhoa(models.Model):
    ma_hd_nk = models.ForeignKey(HoatDongNgoaiKhoa, on_delete=models.CASCADE, related_name='dang_ky')
    ma_nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    trang_thai = models.CharField(
        max_length=20,
        choices=[('DangKy', 'Đăng ký'), ('ThamGia', 'Tham gia')],
        default='DangKy'
    )
    thoi_gian_dk = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ma_hd_nk', 'ma_nguoi_dung')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_trang_thai = None
        if not is_new:
            old_trang_thai = type(self).objects.get(pk=self.pk).trang_thai

        # Cộng điểm khi:
        # 1. Tạo bản ghi mới với trạng thái 'ThamGia'
        # 2. Hoặc trạng thái thay đổi từ khác sang 'ThamGia'
        if self.trang_thai == 'ThamGia' and self.ma_nguoi_dung.vai_tro == 'SinhVien':
            if is_new or (old_trang_thai != 'ThamGia'):
                points = 0
                if self.ma_hd_nk.quyen_loi == 'Cong10':
                    points = 10
                elif self.ma_hd_nk.quyen_loi == 'Cong15':
                    points = 15
                elif self.ma_hd_nk.quyen_loi == 'Cong20':
                    points = 20

                self.ma_nguoi_dung.diem_ngoai_khoa += points
                # Cộng điểm vào mục tương ứng
                if self.ma_hd_nk.muc == 'I':
                    self.ma_nguoi_dung.diem_muc_i += points
                elif self.ma_hd_nk.muc == 'II':
                    self.ma_nguoi_dung.diem_muc_ii += points
                elif self.ma_hd_nk.muc == 'III':
                    self.ma_nguoi_dung.diem_muc_iii += points
                elif self.ma_hd_nk.muc == 'IV':
                    self.ma_nguoi_dung.diem_muc_iv += points
                self.ma_nguoi_dung.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ma_nguoi_dung.ho_ten} đăng ký {self.ma_hd_nk.ten_hd_nk}"

# Model cho thông báo
class ThongBao(models.Model):
    ma_nguoi_nhan = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='thong_bao')
    ma_nguoi_gui = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='thong_bao_gui', null=True,
                                     blank=True)
    noi_dung = models.TextField()
    loai = models.CharField(
        max_length=20,
        choices=[
            ('Like', 'Like'),
            ('Comment', 'Comment'),
            ('GroupJoin', 'Tham gia nhóm'),
            ('GroupInvite', 'Mời vào nhóm'),
            ('Activity', 'Hoạt động ngoại khóa'),
            ('Booking', 'Đặt lịch'),
        ]
    )
    da_doc = models.BooleanField(default=False)
    thoi_gian = models.DateTimeField(auto_now_add=True)
    lien_ket = models.CharField(max_length=200, blank=True)

    # Thêm các ForeignKey tùy chọn
    ma_bai_viet = models.ForeignKey('BaiViet', on_delete=models.CASCADE, null=True, blank=True)
    ma_nhom = models.ForeignKey('Nhom', on_delete=models.CASCADE, null=True, blank=True)
    ma_hoat_dong = models.ForeignKey('HoatDongNgoaiKhoa', on_delete=models.CASCADE, null=True, blank=True)
    ma_dat_lich = models.ForeignKey('DatLich', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Thông báo cho {self.ma_nguoi_nhan.ho_ten}: {self.noi_dung}"


class OTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        #kiểm tra OTP rỗng không
        if not self.otp_code:
            self.otp_code = ''.join(random.choices(string.digits, k=4))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def __str__(self):
        return f"OTP for {self.email}"

# Signals để tự động tạo thông báo
@receiver(post_save, sender=CamXuc)
def create_like_notification(sender, instance, created, **kwargs):
    if created and instance.ma_nguoi_dung != instance.ma_bai_viet.ma_nguoi_dung:
        ThongBao.objects.create(
            ma_nguoi_nhan=instance.ma_bai_viet.ma_nguoi_dung,
            ma_nguoi_gui=instance.ma_nguoi_dung,
            noi_dung=f"{instance.ma_nguoi_dung.ho_ten} đã thích bài viết của bạn",
            loai='Like',
            ma_bai_viet=instance.ma_bai_viet
        )

@receiver(post_save, sender=BinhLuan)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.ma_nguoi_dung != instance.ma_bai_viet.ma_nguoi_dung:
        ThongBao.objects.create(
            ma_nguoi_nhan=instance.ma_bai_viet.ma_nguoi_dung,
            ma_nguoi_gui=instance.ma_nguoi_dung,
            noi_dung=f"{instance.ma_nguoi_dung.ho_ten} đã bình luận về bài viết của bạn",
            loai='Comment',
            ma_bai_viet=instance.ma_bai_viet
        )

@receiver(post_save, sender=ThanhVienNhom)
def create_group_join_notification(sender, instance, created, **kwargs):
    if created and instance.trang_thai == 'ChoDuyet':
        # Thông báo cho các quản trị viên nhóm
        admins = ThanhVienNhom.objects.filter(
            ma_nhom=instance.ma_nhom,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        )
        for admin in admins:
            ThongBao.objects.create(
                ma_nguoi_nhan=admin.ma_nguoi_dung,
                ma_nguoi_gui=instance.ma_nguoi_dung,
                noi_dung=f"{instance.ma_nguoi_dung.ho_ten} yêu cầu tham gia nhóm {instance.ma_nhom.ten_nhom}",
                loai='GroupJoin',
                ma_nhom=instance.ma_nhom
            )

@receiver(post_save, sender=LoiMoiNhom)
def create_group_invite_notification(sender, instance, created, **kwargs):
    if created:
        ThongBao.objects.create(
            ma_nguoi_nhan=instance.ma_nguoi_nhan,
            ma_nguoi_gui=instance.ma_nguoi_gui,
            noi_dung=f"{instance.ma_nguoi_gui.ho_ten} đã mời bạn tham gia nhóm {instance.ma_nhom.ten_nhom}",
            loai='GroupInvite',
            ma_nhom=instance.ma_nhom
        )

@receiver(post_save, sender=HoatDongNgoaiKhoa)
def create_activity_notification(sender, instance, created, **kwargs):
    if created:
        # Thông báo cho tất cả sinh viên về hoạt động ngoại khóa mới
        sinh_vien = NguoiDung.objects.filter(vai_tro='SinhVien')
        for sv in sinh_vien:
            ThongBao.objects.create(
                ma_nguoi_nhan=sv,
                ma_nguoi_gui=instance.nguoi_tao,
                noi_dung=f"Hoạt động ngoại khóa mới: {instance.ten_hd_nk}",
                loai='Activity',
                ma_hoat_dong=instance
            )

@receiver(post_save, sender=DatLich)
def create_booking_notification(sender, instance, created, **kwargs):
    if created:
        # Thông báo cho admin về yêu cầu đặt lịch mới
        admins = NguoiDung.objects.filter(vai_tro='Admin')
        for admin in admins:
            ThongBao.objects.create(
                ma_nguoi_nhan=admin,
                ma_nguoi_gui=instance.ma_nguoi_dung,
                noi_dung=f"{instance.ma_nguoi_dung.ho_ten} yêu cầu đặt lịch {instance.ma_san.ten_san} vào {instance.ngay} {instance.gio_bat_dau}",
                loai='Booking',
                ma_dat_lich=instance
            )
    elif not created and instance.trang_thai in ['XacNhan', 'Huy']:
        # Thông báo cho người đặt lịch về trạng thái
        status_text = 'đã được xác nhận' if instance.trang_thai == 'XacNhan' else 'đã bị hủy'
        ThongBao.objects.create(
            ma_nguoi_nhan=instance.ma_nguoi_dung,
            noi_dung=f"Lịch đặt {instance.ma_san.ten_san} vào {instance.ngay} {instance.gio_bat_dau} {status_text}",
            loai='Booking',
            ma_dat_lich=instance
        )