from django import forms
from .models import SchoolInfo, Teacher, News, Category

class SchoolInfoForm(forms.ModelForm):
    class Meta:
        model = SchoolInfo
        fields = ['teachers_count', 'students_count', 'classes_count', 'sciences_count', 'phone', 'email']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'surname', 'image', 'category']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category 
        fields = ['name']

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'description', 'image']
