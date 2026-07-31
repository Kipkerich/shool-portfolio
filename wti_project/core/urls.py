from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('courses/', views.courses_view, name='courses'),
    path('courses/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('courses/<int:course_id>/apply/', views.apply_view, name='apply'),
    path('courses/<int:course_id>/apply/payment-callback/', views.payment_callback_view, name='payment_callback'),
    path('courses/<int:course_id>/apply/success/', views.application_success_view, name='application_success'),
    path('blog/', views.blog_view, name='blog'),
    path('contact/', views.contact_view, name='contact'),
]