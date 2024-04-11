# Generated by Django 4.2.7 on 2024-03-11 16:24

import accounts.models
import ckeditor_uploader.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_subject_template_theme_teacherrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacherrequest',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='requests', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teacherrequest',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='teacherrequest',
            name='pdf_file',
            field=models.FileField(null=True, upload_to=accounts.models.pdf_file_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
    ]
