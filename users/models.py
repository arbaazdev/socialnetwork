from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    Manager class for custom User model. Provides helper methods to create
    users and superusers.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.

        Args:
            email (str): The user's email.
            password (str): The user's password.
            extra_fields (dict): Additional fields to be added to the user.

        Returns:
            User: The created user object.
        """
        if not email:
            raise ValueError('Email must be provided')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.

        Args:
            email (str): The superuser's email.
            password (str): The superuser's password.
            extra_fields (dict): Additional fields to be added to the superuser.

        Returns:
            User: The created superuser object.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model extending Django's AbstractBaseUser.

    Attributes:
        email (EmailField): The user's unique email.
        name (CharField): The user's name.
        is_active (BooleanField): Determines whether the user is active.
        is_staff (BooleanField): Determines whether the user has staff privileges.
    """

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ['id']


class FriendRequest(models.Model):
    """
    Model to represent a friend request between two users.

    Attributes:
        from_user (ForeignKey): The user who sent the friend request.
        to_user (ForeignKey): The user who received the friend request.
        status (CharField): The status of the friend request (pending, accepted, rejected).
        created_at (DateTimeField): The timestamp when the friend request was created.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending'
        ACCEPTED = 'accepted'
        REJECTED = 'rejected'
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"Friend request from {self.from_user} to {self.to_user}"
