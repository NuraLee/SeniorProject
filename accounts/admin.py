from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Material, MaterialRejection, Subject, Theme, Template, TeacherRequest


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    # inlines = (ProfileInline, )

    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'role')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        # (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'phone', 'email', 'role'),
        }),
    )
    list_display = ('username', 'email', 'phone', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author',)


@admin.register(MaterialRejection)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'material', 'expert',)


class ThemeInline(admin.TabularInline):
    model = Theme
    extra = 0


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    inlines = [ThemeInline]
    list_display = ('id', 'name_en', 'name_kk', 'name_ru')


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_en', 'name_kk', 'name_ru')


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_en', 'name_kk', 'name_ru', 'prompt')


@admin.register(TeacherRequest)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'grade', 'theme', 'author', 'template')
