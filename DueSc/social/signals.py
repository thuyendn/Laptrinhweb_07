# social/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission, update_last_login
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import user_logged_in
from .models import TaiKhoan, ThanhVienNhom

# Ngắt kết nối handler update_last_login mặc định
user_logged_in.disconnect(update_last_login)
print("Disconnected default update_last_login signal")

@receiver(user_logged_in)
def disable_update_last_login(sender, user, request, **kwargs):
    print("Signal user_logged_in received, skipping update_last_login")
    pass

@receiver(post_save, sender=TaiKhoan)
def add_user_to_group(sender, instance, created, **kwargs):
    """
    Khi một user được tạo, thêm vào nhóm tương ứng dựa trên vai trò
    """
    if created:
        # Tạo các nhóm nếu chưa tồn tại
        sinhvien_group, created = Group.objects.get_or_create(name='SinhVien')
        giangvien_group, created = Group.objects.get_or_create(name='GiangVien')
        quantrivien_nhom_group, created = Group.objects.get_or_create(name='QuanTriVienNhom')

        # Lấy content type cho model TaiKhoan
        content_type = ContentType.objects.get_for_model(TaiKhoan)

        # Lấy hoặc tạo các quyền
        can_approve_group, created = Permission.objects.get_or_create(
            codename='can_approve_group',
            name='Có thể duyệt tạo nhóm',
            content_type=content_type,
        )

        can_approve_schedule, created = Permission.objects.get_or_create(
            codename='can_approve_schedule',
            name='Có thể duyệt lịch',
            content_type=content_type,
        )

        can_post_activities, created = Permission.objects.get_or_create(
            codename='can_post_activities',
            name='Có thể đăng hoạt động ngoại khóa',
            content_type=content_type,
        )

        can_manage_group_members, created = Permission.objects.get_or_create(
            codename='can_manage_group_members',
            name='Có thể quản lý thành viên nhóm',
            content_type=content_type,
        )

        # Gán quyền cho các nhóm
        if hasattr(instance, 'is_sinhvien') and instance.is_sinhvien:
            instance.user.groups.add(sinhvien_group)

        if hasattr(instance, 'is_giangvien') and instance.is_giangvien:
            instance.user.groups.add(giangvien_group)
            instance.user.user_permissions.add(can_approve_group)
            instance.user.user_permissions.add(can_approve_schedule)
            instance.user.user_permissions.add(can_post_activities)

        if hasattr(instance, 'is_quantrivien_nhom') and instance.is_quantrivien_nhom:
            instance.user.groups.add(quantrivien_nhom_group)
            instance.user.user_permissions.add(can_manage_group_members)

@receiver(post_save, sender=ThanhVienNhom)
def update_group_admin_status(sender, instance, created, **kwargs):
    """
    Khi một sinh viên trở thành quản trị viên nhóm, cập nhật trạng thái is_quantrivien_nhom
    """
    if instance.vai_tro == 'Quản trị viên' and instance.trang_thai == 'Được duyệt':
        # Lấy TaiKhoan từ NguoiDung thông qua MaNguoiDung
        nguoi_dung = instance.ma_nguoi_dung
        user = TaiKhoan.objects.get(MaNguoiDung=nguoi_dung)

        # Kiểm tra xem user có trường is_quantrivien_nhom không trước khi gán
        if hasattr(user, 'is_quantrivien_nhom'):
            user.is_quantrivien_nhom = True
            user.save()

            # Thêm vào nhóm QuanTriVienNhom
            quantrivien_nhom_group = Group.objects.get(name='QuanTriVienNhom')
            user.user.groups.add(quantrivien_nhom_group)

            # Gán quyền quản lý thành viên nhóm
            content_type = ContentType.objects.get_for_model(TaiKhoan)
            can_manage_group_members = Permission.objects.get(
                codename='can_manage_group_members',
                content_type=content_type,
            )
            user.user.user_permissions.add(can_manage_group_members)