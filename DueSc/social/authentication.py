from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import NguoiDung

User = get_user_model()

import logging

logger = logging.getLogger(__name__)

class TaiKhoanBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Kiểm tra username không rỗng
        if not username:
            logger.warning("Authentication attempt with empty username")
            return None

        logger.debug(f"Attempting to authenticate user with email: {username}")
        try:
            # Tối ưu truy vấn bằng select_related và chỉ lấy trường cần thiết
            nguoi_dung = NguoiDung.objects.select_related('user').only('user').get(email=username)
            user = nguoi_dung.user

            # Kiểm tra user active
            if not user.is_active:
                logger.warning(f"User {username} is inactive")
                return None

            if user.check_password(password):
                logger.info(f"Successfully authenticated user: {username}")
                return user
            else:
                logger.warning(f"Password check failed for email: {username}")
                return None
        except NguoiDung.DoesNotExist:
            logger.warning(f"User with email {username} not found")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during authentication for {username}: {str(e)}")
            return None

    def get_user(self, user_id):
        if not user_id:
            logger.warning("Get user attempt with empty user_id")
            return None

        logger.debug(f"Retrieving user with ID: {user_id}")
        try:
            # Tối ưu truy vấn
            nguoi_dung = NguoiDung.objects.select_related('user').only('user').get(user__id=user_id)
            user = nguoi_dung.user

            # Kiểm tra user active
            if not user.is_active:
                logger.warning(f"User with ID {user_id} is inactive")
                return None

            logger.info(f"Successfully retrieved user: {nguoi_dung.email}")
            return user
        except NguoiDung.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during get_user for ID {user_id}: {str(e)}")
            return None