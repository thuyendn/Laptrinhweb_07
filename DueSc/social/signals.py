from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import NguoiDung, ThanhVienNhom, Nhom

@receiver(post_save, sender=User)
def create_nguoi_dung(sender, instance, created, **kwargs):
    if created:
        # Tạo NguoiDung khi User được tạo
        NguoiDung.objects.create(
            user=instance,
            ho_ten=instance.username,  # Hoặc lấy từ dữ liệu khác nếu có
            email=instance.email
        )

@receiver(post_save, sender=NguoiDung)
def add_to_default_group(sender, instance, created, **kwargs):
    if created:
        # Tự động thêm người dùng vào một nhóm mặc định (nếu có)
        default_group = Nhom.objects.filter(ten_nhom='Nhóm mặc định').first()
        if default_group:
            ThanhVienNhom.objects.create(
                ma_nhom=default_group,
                ma_nguoi_dung=instance,
                trang_thai='DuocDuyet'
            )