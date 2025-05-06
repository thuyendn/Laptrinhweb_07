from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AnonymousUser
from DueSc.social.models import TaiKhoan

class TaiKhoanBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            tai_khoan = TaiKhoan.objects.get(Email=username)
            if check_password(password, tai_khoan.MatKhau):
                print(f"Authenticated user: {tai_khoan.Email}")
                return tai_khoan
            print("Password check failed")
            return None
        except TaiKhoan.DoesNotExist:
            print("User not found")
            return None

    def get_user(self, user_id):
        try:
            user = TaiKhoan.objects.get(MaTaiKhoan=user_id)
            print(f"Retrieved user: {user.Email}")
            return user
        except TaiKhoan.DoesNotExist:
            print("User not found by ID")
            return None

    def has_perm(self, user_obj, perm, obj=None):
        # Kiểm tra quyền của user
        return user_obj.is_authenticated and user_obj.is_active