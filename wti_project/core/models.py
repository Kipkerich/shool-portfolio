from django.db import models

class Blog(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, default='General')
    date = models.DateField(null=True, blank=True)
    content = models.TextField()
    image = models.FileField(upload_to='blogs/', null=True, blank=True, help_text="Upload blog image")
    image_path = models.CharField(max_length=200, blank=True, null=True, help_text="Path to static image (optional, e.g. 'images/blog-1.jpg')")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date']

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.IntegerField(default=0, help_text="Order of display (ascending)")

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['order', 'id']
