from django.db import models
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?\d[\d\s]{6,20}$',
    message="Raqam faqat '+' belgisi, raqam va bo'shliqlardan iborat bo'lishi kerak."
)

class Category(models.Model):
    name = models.CharField(max_length=155)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    name = models.CharField(max_length=155, verbose_name="Ism")
    surname = models.CharField(max_length=100, null=True, blank=True, verbose_name="Familiya")
    image = models.ImageField(upload_to='images/', verbose_name="Rasm")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers',
        verbose_name="Ustozlar guruhi"
    )
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lavozim")

    def __str__(self):
        return f"{self.name} {self.surname}"

class News(models.Model):
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    description = models.TextField(verbose_name="Tavsif")
    image = models.ImageField(upload_to='images/', verbose_name="Rasm")
    created_at = models.DateTimeField(auto_now_add=True)

class SocialMedia(models.Model):
    PLATFORM_CHOICES = [
        ('FB', 'Facebook'),
        ('IG', 'Instagram'),
        ('TG', 'Telegram'),
    ]
    platform = models.CharField(max_length=2, choices=PLATFORM_CHOICES, unique=True)
    url = models.URLField()

    def __str__(self):
        return self.get_platform_display()

class SchoolInfo(models.Model):
    teachers_count = models.PositiveIntegerField(default=0, verbose_name="O'qituvchilar soni")
    students_count = models.PositiveIntegerField(default=0, verbose_name="O'quvchilar soni")
    classes_count = models.PositiveIntegerField(default=0, verbose_name="Sinflar soni")
    sciences_count = models.PositiveIntegerField(default=0, verbose_name="Fanlar soni")
    phone = models.CharField(max_length=20, blank=True, null=True, validators=[phone_validator], verbose_name="Maktab telefon raqami")
    email = models.EmailField(blank=True, null=True, verbose_name="Maktab email adresi")

    def __str__(self):
        return "School Info"
