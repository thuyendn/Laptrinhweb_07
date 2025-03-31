from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Mô hình Người dùng (NguoiDung)
class NguoiDung(models.Model):
   ma_nguoi_dung = models.AutoField(primary_key=True)
   ho_ten = models.CharField(max_length=255)
   gioi_tinh = models.CharField(max_length=10, choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')])
   ngay_sinh = models.DateField()
   ma_tai_khoan = models.IntegerField(unique=True)


   def __str__(self):
       return self.ho_ten


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
   MaNguoiDung = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Mã người dùng")
   NgayDatLich = models.DateField(verbose_name="Ngày đặt lịch")
   GioDatLich = models.TimeField(verbose_name="Giờ đặt lịch")
   TrangThai = models.CharField(max_length=20, choices=TrangThaiChoices.choices, verbose_name="Trạng thái")
   MaDV = models.ForeignKey(DichVuCong, on_delete=models.CASCADE, verbose_name="Mã dịch vụ")


   def save(self, *args, **kwargs):
       # Kiểm tra nếu đã có lịch trong cùng ngày và giờ
       existing_schedule = DatLich.objects.filter(NgayDatLich=self.NgayDatLich, GioDatLich=self.GioDatLich).exists()
       if existing_schedule:
           self.TrangThai = self.TrangThaiChoices.TU_CHOI
       else:
           self.TrangThai = self.TrangThaiChoices.DA_DUYET
       super().save(*args, **kwargs)


   def __str__(self):
       return f"Lịch {self.MaDatLich} - {self.MaNguoiDung.username}"


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
   Email = models.EmailField()
   MatKhau = models.CharField(max_length=255)  # Đặt độ dài cho mật khẩu
   DiemHDNK = models.IntegerField(default=0.0)
   MaNguoiDung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='nguoi_dung')


   def __str__(self):
       return self.Email


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

