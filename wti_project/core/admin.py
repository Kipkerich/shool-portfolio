from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import escape
from .models import Blog, FAQ, Course, ApplicationField, ApplicationSubmission

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

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'application_fee')
    search_fields = ('title', 'description', 'level')
    fieldsets = (
        ('General Details', {
            'fields': ('title', 'level', 'description')
        }),
        ('Images & Fallbacks', {
            'fields': ('image', 'image_path'),
            'description': 'Upload a high-quality course image or reference a static asset path.'
        }),
        ('Fees & Paystack Configuration', {
            'fields': ('application_fee', 'paystack_public_key'),
            'description': 'Specify the application fee and the Paystack public key to accept applicant fee payments.'
        }),
        ('School Fees Structure & Materials', {
            'fields': ('fees_structure_pdf', 'fees_structure_text'),
            'description': 'Upload a PDF of the school fees structure or write text manually.'
        }),
    )

@admin.register(ApplicationField)
class ApplicationFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'field_type', 'required', 'order')
    list_filter = ('field_type', 'required')
    search_fields = ('label',)
    ordering = ('order', 'id')

@admin.register(ApplicationSubmission)
class ApplicationSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'submitted_at', 'paid', 'amount_paid', 'payment_reference')
    list_filter = ('paid', 'course', 'submitted_at')
    search_fields = ('payment_reference', 'data')
    readonly_fields = ('course', 'submitted_at', 'formatted_data', 'paid', 'payment_reference', 'amount_paid')
    exclude = ('data',)

    def formatted_data(self, obj):
        if not obj.data:
            return "No data submitted"
        html = '<table style="width:100%; border-collapse:collapse; border: 1px solid #eee;">'
        for key, value in obj.data.items():
            escaped_key = escape(str(key))
            escaped_value = escape(str(value))
            html += f'<tr style="border-bottom: 1px solid #eee;"><td style="padding:8px; font-weight:bold; width:30%; background-color:#f9f9f9;">{escaped_key}:</td><td style="padding:8px;">{escaped_value}</td></tr>'
        html += '</table>'
        return mark_safe(html)
    formatted_data.short_description = "Submitted Form Details"
