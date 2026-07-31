from django.contrib import admin
from .models import Blog, FAQ

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
