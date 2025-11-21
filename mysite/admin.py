from django.contrib import admin
from .models import Teacher, News, SocialMedia, SchoolInfo, Category

admin.site.register(Teacher)
admin.site.register(News)
admin.site.register(SocialMedia)
admin.site.register(SchoolInfo)
admin.site.register(Category)