from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField(verbose_name='Начало курса')
    end_year = models.DateField(verbose_name='Конец курса')

    def __str__(self):
        return "С " + str(self.start_year) + " до " + str(self.end_year)


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    GENDER = [("M", "Мужской"), ("Ж", "Женский")]
    username = None
    first_name = models.CharField(max_length=25, verbose_name='Имя', null=True)
    second_name=models.CharField( max_length=25, verbose_name='Фамилия', null=True)
    email = models.EmailField(unique=True, verbose_name='Почта')
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1,  verbose_name="Пол", choices=GENDER)
    profile_pic = models.ImageField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.last_name + " " + self.first_name


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Course(models.Model):
    name = models.CharField(max_length=120, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False, verbose_name='Курс')
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True, verbose_name='Длительность курса')

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Staff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, verbose_name='Курс')
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name


class Subject(models.Model):
    name = models.CharField(max_length=120, verbose_name='Название')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name='Преподаватель')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Предмет')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, verbose_name='Продолжительность курса')
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING, verbose_name='Предмет')
    date = models.DateField(verbose_name='Дата')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, verbose_name='Ученик')
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, verbose_name='Дата')
    status = models.BooleanField(default=False, verbose_name='Посещение')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Ученик')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    exam = models.FloatField(default=0,  verbose_name='Экзамен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CourseEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Ученик')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.staff.save()
    if instance.user_type == 3:
        instance.student.save()
