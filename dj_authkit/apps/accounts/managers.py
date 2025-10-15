from django.conf import settings
from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email: str, password: str, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError(_("The Email must be provided."))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str = None, password: str = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str = None, password: str = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("user_type", "Owner")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def create_staff(self, email: str = None, password: str = None, **extra_fields):
        extra_fields.setdefault("user_type", "Staff")
        extra_fields.setdefault("is_staff", True)
        return self._create_user(email, password, **extra_fields)

    def create_staff_user(
        self, email: str = None, password: str = None, **extra_fields
    ):
        extra_fields.setdefault("user_type", "Staff")
        return self._create_user(email, password, **extra_fields)

    def create_owner(self, email: str = None, password: str = None, **extra_fields):
        extra_fields.setdefault("user_type", "Owner")
        if settings.DEBUG:
            extra_fields.setdefault("is_staff", True)
            extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)

    def create_customer(self, email: str = None, password: str = None, **extra_fields):
        extra_fields.setdefault("user_type", "Customer")
        return self._create_user(email, password, **extra_fields)

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()
