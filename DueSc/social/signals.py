from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import TaiKhoan, ThanhVienNhom


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
        if instance.is_sinhvien:
            instance.groups.add(sinhvien_group)

        if instance.is_giangvien:
            instance.groups.add(giangvien_group)
            # Gán quyền cho giảng viên
            instance.user_permissions.add(can_approve_group)
            instance.user_permissions.add(can_approve_schedule)
            instance.user_permissions.add(can_post_activities)

        if instance.is_quantrivien_nhom:
            instance.groups.add(quantrivien_nhom_group)
            # Gán quyền cho quản trị viên nhóm
            instance.user_permissions.add(can_manage_group_members)


@receiver(post_save, sender=ThanhVienNhom)
def update_group_admin_status(sender, instance, created, **kwargs):
    """
    Khi một sinh viên trở thành quản trị viên nhóm, cập nhật trạng thái is_quantrivien_nhom
    """
    if instance.VaiTro == 'QUAN_TRI' and instance.TrangThai == 'DA_DUYET':
        user = instance.MaNguoiDung.TaiKhoan
        user.is_quantrivien_nhom = True
        user.save()

        # Thêm vào nhóm QuanTriVienNhom
        quantrivien_nhom_group = Group.objects.get(name='QuanTriVienNhom')
        user.groups.add(quantrivien_nhom_group)

        # Gán quyền quản lý thành viên nhóm
        content_type = ContentType.objects.get_for_model(TaiKhoan)
        can_manage_group_members = Permission.objects.get(
            codename='can_manage_group_members',
            content_type=content_type,
        )
        user.user_permissions.add(can_manage_group_members)