import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field


from django.contrib.auth.models import AbstractUser
from django.db import models

def pdf_file_path(instance, filename):
    # This function generates the file path for the PDF files
    return f'media/pdf_files/{filename}'

class User(AbstractUser):
    class Role(models.IntegerChoices):
        EXPERT = 1, "moderaot"
        CUSTOMER = 2, 'customer'
    
    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=15)


    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name}'
    
    @property
    def is_customer(self):
        return self.role == User.Role.CUSTOMER
    
    @property
    def is_expert(self):
        return self.role == User.Role.EXPERT
    
    def __str__(self):
        return self.username
    

class Material(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    author = models.ForeignKey(User, related_name='materials', on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_('title'), max_length=128)
    description = models.TextField(verbose_name=_('description'), )
    pdf_file = models.FileField(verbose_name=_('pdf_file'), 
        upload_to=pdf_file_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    subject = models.CharField(verbose_name=_('subject'), max_length=20, default='algebra')
    grade = models.CharField(verbose_name=_('grade'), max_length=2)
    rating = models.DecimalField(verbose_name=_('rating'), max_digits=3, decimal_places=1, default=0)
    status = models.CharField(verbose_name=_('status'), 
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        return os.path.basename(self.pdf_file.name)
    
    @property
    def is_new(self):
        return self.status == Material.Status.NEW
    
    @property
    def created_at_with_timezone(self):
        return self.created_at.astimezone(timezone.get_current_timezone()).strftime('%d.%m.%Y %H:%M')
    
    def __str__(self) -> str:
        return self.title
    
class FavoriteMaterial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_materials')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'material')    

class MaterialInfo(models.Model):
    material = models.ForeignKey('Material', related_name='infos', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='material_infos', on_delete=models.CASCADE)
    user_rating = models.PositiveSmallIntegerField(verbose_name=_('user_rating'), null=True, blank=True)
    user_comment = models.TextField(verbose_name=_('user_comment'), null=True, blank=True)
    commented_at = models.DateTimeField(verbose_name=_('commented_at'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['material', 'user']]

    def __str__(self):
        return f"Info for Material: {self.material.title}"
    
    @property
    def created_at_with_timezone(self):
        return self.created_at.astimezone(timezone.get_current_timezone()).strftime('%d.%m.%Y %H:%M')
    

class MaterialRejection(models.Model):
    material = models.ForeignKey(Material, verbose_name=_('material'), on_delete=models.CASCADE, related_name='rejections')
    expert = models.ForeignKey(User, verbose_name=_('expert'), related_name='material_rejections', on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name=_('created_at'), auto_now_add=True)
    description = models.TextField(verbose_name=_('description'), )

    class Meta:
        unique_together = [['material', 'expert']]

    def __str__(self):
        return f"Rejection for Material: {self.material.title}"
    
    @property
    def created_at_with_timezone(self):
        return self.created_at.astimezone(timezone.get_current_timezone()).strftime('%d.%m.%Y %H:%M')
    
    
class FavoriteMaterial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)


class Room(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_rooms')
    name = models.CharField(max_length=100, null=True, blank=True)


class RoomMessage(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    body = models.TextField(verbose_name=_('body'), )
    response_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Subject(models.Model):
    name_en = models.CharField(_('Name (English)'), max_length=100)
    name_kk = models.CharField(_('Name (Kazakh)'), max_length=100)
    name_ru = models.CharField(_('Name (Russian)'), max_length=100)

    @property
    def name(self):
        lang_code = get_language() 
        if lang_code == 'kk':
            return self.name_kk
        elif lang_code == 'ru':
            return self.name_ru
        else:
            return self.name_en

    def __str__(self):
        lang_code = get_language()  # Get the current language code
        # Choose the appropriate name based on the current language
        if lang_code == 'kk':
            return self.name_kk
        elif lang_code == 'ru':
            return self.name_ru
        else:
            return self.name_en

class Theme(models.Model):
    name_en = models.CharField(_('Name (English)'), max_length=100)
    name_kk = models.CharField(_('Name (Kazakh)'), max_length=100)
    name_ru = models.CharField(_('Name (Russian)'), max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='themes')

    @property
    def name(self):
        lang_code = get_language() 
        if lang_code == 'kk':
            return self.name_kk
        elif lang_code == 'ru':
            return self.name_ru
        else:
            return self.name_en

    def __str__(self):
        lang_code = get_language()  # Get the current language code
        # Choose the appropriate name based on the current language
        if lang_code == 'kk':
            return self.name_kk
        elif lang_code == 'ru':
            return self.name_ru
        else:
            return self.name_en


class Template(models.Model):
    name_en = models.CharField(_('Name (English)'), max_length=100)
    name_kk = models.CharField(_('Name (Kazakh)'), max_length=100)
    name_ru = models.CharField(_('Name (Russian)'), max_length=100)
    prompt = models.TextField()

    @property
    def name(self):
        lang_code = get_language() 
        if lang_code == 'kk':
            return self.name_kk
        elif lang_code == 'ru':
            return self.name_ru
        else:
            return self.name_en

    def __str__(self):
        lang_code = get_language()  # Get the current language code
        # Choose the appropriate name based on the current language
        if lang_code == 'kk':
            return self.name_kk
        elif lang_code == 'ru':
            return self.name_ru
        else:
            return self.name_en


class TeacherRequest(models.Model):
    subject = models.ForeignKey(Subject,verbose_name=_('subject'), on_delete=models.CASCADE)
    grade = models.PositiveSmallIntegerField(verbose_name=_('grade'), choices=[(i, i) for i in range(1, 12)])
    theme = models.ForeignKey(Theme, verbose_name=_('theme'), on_delete=models.CASCADE)
    template = models.ForeignKey(Template, verbose_name=_('template'), on_delete=models.CASCADE)
    pdf_file = models.FileField(verbose_name=_('pdf_file'), 
        upload_to=pdf_file_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        null=True, blank=True
    )
    content = CKEditor5Field(verbose_name=_('content'), )
    author = models.ForeignKey(User, related_name='requests', on_delete=models.CASCADE)

    @property
    def filename(self):
        return os.path.basename(self.pdf_file.name)
