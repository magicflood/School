from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from .models import Teacher, SchoolInfo, News, Category
from .forms import SchoolInfoForm, TeacherForm, NewsForm
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db.models import Case, When, Value, IntegerField
from config import ADMIN_PASSWORD

# -------------------------
# Вход в админку
# -------------------------
def admin_login(request):
    if request.session.get('admin_logged'):
        return redirect('admin_dashboard')

    if request.method == "POST":
        if request.POST.get("password") == ADMIN_PASSWORD:
            request.session['admin_logged'] = True
            return redirect('admin_dashboard')
        return render(request, "admin_panel/login.html", {"error": "Неправильный пароль"})

    return render(request, "admin_panel/login.html")


# -------------------------
# Декоратор проверки админа
# -------------------------
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_logged'):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_panel_redirect(request):
    return redirect('admin_dashboard')

# -------------------------
# Главная страница сайта
# -------------------------
class HomeView(TemplateView):
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.session.get('admin_logged'):
            request.session.flush()
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        priority_categories = ["Rahbariyat", "Maktab direktori"]
        teachers = list(Teacher.objects.filter(category__name__in=priority_categories)[:4])
        remaining = 4 - len(teachers)
        if remaining > 0:
            other_teachers = Teacher.objects.exclude(id__in=[t.id for t in teachers])[:remaining]
            teachers.extend(other_teachers)
        context['teachers'] = teachers
        context['news'] = News.objects.order_by('-created_at')[:3]
        context['info'] = SchoolInfo.objects.first()
        return context


# -------------------------
# Контактная форма
# -------------------------
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


# -------------------------
# Новости
# -------------------------
def news_view(request):
    news = News.objects.all()
    return render(request, 'news.html', {'news': news})


def news_detail(request, pk):
    news = News.objects.filter(id=pk).first()
    recent_news = News.objects.all()
    return render(request, 'detail.html', {'news': news, 'recent_news': recent_news})


# -------------------------
# Учителя
# -------------------------
def teachers_view(request):
    CATEGORY_ORDER = ["Maktab direktori", "Rahbariyat", "Fan o'qituvchisi", "Boshlang'ich sinf o'qituvchisi"]
    cases = [When(name=name, then=Value(i)) for i, name in enumerate(CATEGORY_ORDER)]
    categories = Category.objects.annotate(
        custom_order=Case(*cases, default=Value(999), output_field=IntegerField())
    ).prefetch_related('teachers').order_by('custom_order')
    grouped = [{'category': c, 'teachers': c.teachers.all()} for c in categories if c.teachers.exists()]
    return render(request, 'teachers_list.html', {'teachers_grouped': grouped})


# -------------------------
# Админка
# -------------------------
@admin_required
def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html', {
        'teachers_count': Teacher.objects.count(),
        'news_count': News.objects.count(),
        'info': SchoolInfo.objects.first()
    })


@admin_required
def admin_school_info(request):
    info = SchoolInfo.objects.first() or SchoolInfo.objects.create()
    if request.method == 'POST':
        form = SchoolInfoForm(request.POST, instance=info)
        if form.is_valid():
            form.save()
            messages.success(request, "Сохранено!")
            return redirect('admin_dashboard')
    else:
        form = SchoolInfoForm(instance=info)
    return render(request, 'admin_panel/school_info.html', {'form': form})


@admin_required
def admin_teachers(request):
    return render(request, 'admin_panel/teachers.html', {
        'teachers': Teacher.objects.select_related('category').all(),
        'form': TeacherForm(),
        'categories': Category.objects.all(),
    })


@admin_required
def admin_add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return redirect('admin_teachers')


@admin_required
def admin_edit_teacher(request, teacher_id):
    t = Teacher.objects.filter(id=teacher_id).first()
    if not t: 
        return redirect('admin_teachers')
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=t)
        if form.is_valid():
            form.save()
            return redirect('admin_teachers')
    else:
        form = TeacherForm(instance=t)
    return render(request, 'admin_panel/edit_teacher.html', {'form': form, 'teacher': t})


@admin_required
def admin_delete_teacher(request, teacher_id):
    t = Teacher.objects.filter(id=teacher_id).first()
    if t: t.delete()
    return redirect('admin_teachers')


@admin_required
def admin_news(request):
    return render(request, 'admin_panel/news.html', {
        'news_list': News.objects.all(),
        'form': NewsForm(),
    })


@admin_required
def admin_add_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return redirect('admin_news')


@admin_required
def admin_edit_news(request, news_id):
    n = News.objects.filter(id=news_id).first()
    if not n: return redirect('admin_news')
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=n)
        if form.is_valid():
            form.save()
            return redirect('admin_news')
    else:
        form = NewsForm(instance=n)
    return render(request, 'admin_panel/edit_news.html', {'form': form, 'news': n})


@admin_required
def admin_delete_news(request, news_id):
    n = News.objects.filter(id=news_id).first()
    if n: n.delete()
    return redirect('admin_news')

def admin_logout(request):
    request.session.flush()
    request.session.clear_expired()
    return redirect('admin_login')
