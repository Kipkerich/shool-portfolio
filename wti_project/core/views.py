from django.shortcuts import render
from .models import Blog, FAQ

def home_view(request):
    blogs = Blog.objects.all()[:3]  # original static page had exactly 3 blogs on the home page
    faqs = FAQ.objects.all()
    return render(request, 'core/index.html', {'blogs': blogs, 'faqs': faqs})

def about_view(request):
    return render(request, 'core/about.html')

def courses_view(request):
    return render(request, 'core/courses.html')

def blog_view(request):
    blogs = Blog.objects.all()
    return render(request, 'core/blog.html', {'blogs': blogs})

def contact_view(request):
    return render(request, 'core/contact.html')
