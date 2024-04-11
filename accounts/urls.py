from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    CustomUserCreateView, get_themes, green_page, home, material_detail, rejections, teacher_request_detail_generate_pdf, 
    verify_material, reject_material, my_materials, 
    add_to_favorites, remove_from_favorites, favorite_materials, room, teacher_requests, teacher_request_detail
)

urlpatterns = [
    path('', home, name='home'),
    path('green-page', green_page, name='green_page'),
    path('my-materials', my_materials, name='my_materials'),
    path('requests', teacher_requests, name='teacher_requests'),
    path('requests/<int:pk>/', teacher_request_detail, name='teacher_request_detail'),
    path('requests/<int:pk>/download-pdf/', teacher_request_detail_generate_pdf, name='teacher_request_detail_generate_pdf'),
    path('rejections', rejections, name='rejections'),
    path('signup/', CustomUserCreateView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-material/<int:material_pk>/', verify_material, name='verify_material'),
    path('reject-material/<int:material_pk>/', reject_material, name='reject_material'),
    path('material/<int:pk>/', material_detail, name='material_detail'),
    path('material/<int:pk>/add_to_favorites/', add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:favorite_material_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('favorite-materials/', favorite_materials, name='favorite_materials'),
    path('rooms/', room, name='room'),
    path('get_themes/', get_themes, name='get_themes'),
]