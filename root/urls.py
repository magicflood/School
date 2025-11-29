from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from mysite.views import (
    HomeView, news_view, admin_dashboard, admin_school_info, admin_add_teacher,
    admin_add_news, admin_news, admin_teachers, admin_delete_teacher, news_detail,
    admin_delete_news, teachers_view, send_contact, admin_edit_teacher, admin_edit_news,
    admin_login, admin_logout, admin_panel_redirect
)

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Главная и публичные страницы
    path('', HomeView.as_view(), name='home'),
    path('yangiliklar/', news_view, name='news'),
    path('oqituvchilar/', teachers_view, name='teachers'),
    path('detail/<int:pk>/', news_detail, name='detail'),

    # Админка
    path('admin-panel/login/', admin_login, name='admin_login'),
    path('admin-panel/logout/', admin_logout, name='admin_logout'),
    path('admin-panel/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/school-info/', admin_school_info, name='admin_school_info'),
    path('admin-panel/add-teacher/', admin_add_teacher, name='admin_add_teacher'),
    path('admin-panel/add-news/', admin_add_news, name='admin_add_news'),
    path('admin-panel/teachers/', admin_teachers, name='admin_teachers'),
    path('admin-panel/news/', admin_news, name='admin_news'),
    path('admin-panel/delete-teacher/<int:teacher_id>/', admin_delete_teacher, name='admin_delete_teacher'),
    path('admin-panel/delete-news/<int:news_id>/', admin_delete_news, name='admin_delete_news'),
    path('admin-panel/edit-teacher/<int:teacher_id>/', admin_edit_teacher, name='admin_edit_teacher'),
    path('admin-panel/edit-news/<int:news_id>/', admin_edit_news, name='admin_edit_news'),
    path('admin-panel/', admin_panel_redirect, name='admin_panel'),


    # Контактная форма
    path("send-contact/", send_contact, name="send_contact"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
