from django.contrib import admin
from .models import Blog, FAQ, Course, ApplicationField, ApplicationSubmission

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'application_fee')
    search_fields = ('title', 'description')
    list_filter = ('level',)

@admin.register(ApplicationField)
class ApplicationFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'field_type', 'required', 'order')
    search_fields = ('label',)
    list_filter = ('field_type', 'required')
    ordering = ('order', 'id')

@admin.register(ApplicationSubmission)
class ApplicationSubmissionAdmin(admin.ModelAdmin):
    list_display = ('course', 'submitted_at', 'paid', 'payment_reference', 'amount_paid')
    list_filter = ('paid', 'submitted_at', 'course')
    search_fields = ('payment_reference', 'data')
    readonly_fields = ('submitted_at',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date')
    list_filter = ('category', 'date')
    search_fields = ('title', 'category', 'content')
    date_hierarchy = 'date'
    ordering = ('-date',)
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'category', 'date', 'content')
        }),
        ('Media & Static References', {
            'fields': ('image', 'image_path'),
            'description': 'Upload a new blog image OR provide a static path reference.'
        }),
    )

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order')
    search_fields = ('question', 'answer')
    ordering = ('order', 'id')
