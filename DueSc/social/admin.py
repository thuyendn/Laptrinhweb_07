from django.contrib import admin
from .models import NguoiDung, BaiViet, CamXuc, BinhLuan, HoiThoai, TinNhan, Nhom, ThanhVienNhom, LoiMoiNhom, San, DatLich, HoatDongNgoaiKhoa, DKNgoaiKhoa, ThongBao

# Đăng ký các model với admin
admin.site.register(NguoiDung)
admin.site.register(BaiViet)
admin.site.register(CamXuc)
admin.site.register(BinhLuan)
admin.site.register(HoiThoai)
admin.site.register(TinNhan)
admin.site.register(Nhom)
admin.site.register(ThanhVienNhom)
admin.site.register(LoiMoiNhom)
admin.site.register(San)  # Đổi từ Stadium thành San
admin.site.register(DatLich)
admin.site.register(HoatDongNgoaiKhoa)
admin.site.register(DKNgoaiKhoa)
admin.site.register(ThongBao)