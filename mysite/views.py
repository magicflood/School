from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from .models import Teacher, SchoolInfo, News, Category
from .forms import SchoolInfoForm, TeacherForm, NewsForm, CategoryForm
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db.models import Case, When, Value, IntegerField


def send_contact(request):
    if request.method == "POST": 
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        full_message = f"Ism: {name}\nEmail: {email}\nXabar:\n{message}"

        send_mail(
            subject="Sahifadan yangi kontakt",
            message=full_message,
            from_email=email,
            recipient_list=["proectest@gmail.com"],
        )

        return JsonResponse({"status": "ok"})
    
    return JsonResponse({"status": "error"}, status=400)

class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Сначала пытаемся взять учителей категории Rahbariyat
        rahbariyat_category = Category.objects.filter(name="Rahbariyat").first()
        teachers = []

        if rahbariyat_category:
            rahbariyat_teachers = list(Teacher.objects.filter(category=rahbariyat_category))
            teachers.extend(rahbariyat_teachers[:4])  # берем максимум 4
       
        # Если после этого меньше 4, дополняем другими учителями
        remaining = 4 - len(teachers)
        if remaining > 0:
            # Берем всех учителей, кроме уже выбранных
            other_teachers = Teacher.objects.exclude(id__in=[t.id for t in teachers])[:remaining]
            teachers.extend(other_teachers)

        context['teachers'] = teachers
        context['news'] = News.objects.order_by('-created_at')[:3]
        context['info'] = SchoolInfo.objects.first()
        return context

def news_detail(request, pk):
    news = News.objects.filter(id=pk).first()
    print(news)
    recent_news = News.objects.all()

    data = {
        'news': news,
        'recent_news': recent_news,
    }
    return render(request, 'detail.html', context=data)


def admin_dashboard(request):
    teachers_count = Teacher.objects.count()
    news_count = News.objects.count()
    info = SchoolInfo.objects.first()
    return render(request, 'admin_panel/dashboard.html', {
        'teachers_count': teachers_count,
        'news_count': news_count,
        'info': info
    })

def admin_school_info(request):
    info = SchoolInfo.objects.first()
    if not info:
        info = SchoolInfo.objects.create()
    if request.method == 'POST':
        form = SchoolInfoForm(request.POST, instance=info)
        if form.is_valid():
            form.save()
            messages.success(request, "Maktab ma'lumotlari saqlandi!")
            return redirect('admin_dashboard')
    else:
        form = SchoolInfoForm(instance=info)
    return render(request, 'admin_panel/school_info.html', {'form': form})

def admin_teachers(request):
    teachers = Teacher.objects.select_related('category').all()

    form = TeacherForm()

    return render(request, 'admin_panel/teachers.html', {
        'teachers': teachers,
        'form': form
    })

# def admin_categories(request):
#     category = Category.objects.all() 
#     form = CategoryForm()
#     return render(request, 'admin_panel/category.html', {'category': category, 'form': form})

def admin_add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "O'qituvchi qo'shildi!")
            return redirect('admin_teachers')
    return redirect('admin_teachers')

def admin_edit_teacher(request, teacher_id):
    teacher = Teacher.objects.filter(id=teacher_id).first()
    if not teacher:
        return redirect('admin_teachers')
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "O'qituvchi muvaffaqiyatli yangilandi!")
            return redirect('admin_teachers')
    else:
        form = TeacherForm(instance=teacher)

    return render(request, 'admin_panel/edit_teacher.html', {'form': form, 'teacher': teacher})


def admin_edit_news(request, news_id):
    news = News.objects.filter(id=news_id).first()
    if not news:
        return redirect('admin_news')
    
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, "Yangilik muvaffaqiyatli yangilandi!")
            return redirect('admin_news')
    else:
        form = NewsForm(instance=news)

    return render(request, 'admin_panel/edit_news.html', {'form': form, 'news': news})

# def admin_add_category(request):
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Категория добавлена!")
#             return redirect('admin_categories')
#     return redirect('admin_categories')

def admin_news(request):
    news_list = News.objects.all()
    form = NewsForm()
    return render(request, 'admin_panel/news.html', {'news_list': news_list, 'form': form})

def admin_add_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Yangiliklar qo'shildi!")
            return redirect('admin_news')
    return redirect('admin_news')

def news_view(request):
    news = News.objects.all()
    return render(request, 'news.html', {
        'news': news,
    })

def teachers_view(request):
    CATEGORY_ORDER = ["Rahbariyat", "Fan o'qituvchisi", "Boshlang'ich sinf o'qituvchisi"]

    cases = [When(name=name, then=Value(index)) for index, name in enumerate(CATEGORY_ORDER)]

    categories = Category.objects.annotate(
        custom_order=Case(
            *cases,
            default=Value(999),
            output_field=IntegerField()
        )
    ).prefetch_related('teachers').order_by('custom_order')

    teachers_grouped = []

    for category in categories:
        teachers_in_category = category.teachers.all()

        if not teachers_in_category.exists():
            continue  

        teachers_grouped.append({
            'category': category,
            'teachers': teachers_in_category
        })

    return render(request, 'teachers_list.html', {
        'teachers_grouped': teachers_grouped,
    })



def admin_delete_teacher(request, teacher_id):
    teacher = Teacher.objects.filter(id=teacher_id).first()
    if teacher:
        teacher.delete()
    return redirect('admin_teachers')

def admin_delete_news(request, news_id):
    news = News.objects.filter(id=news_id).first()
    if news:
        news.delete()
    return redirect('admin_news')

# def admin_delete_category(request, category_id):
#     category = Category.objects.filter(id=category_id).first()
#     if category:
#         category.delete()
#     return redirect('admin_categories')
