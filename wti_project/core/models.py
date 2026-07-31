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

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=100, default='Level 5 & 6', help_text="e.g. Level 5 & 6, Short Course")
    image = models.FileField(upload_to='courses/', null=True, blank=True, help_text="Upload course image")
    image_path = models.CharField(max_length=200, blank=True, null=True, help_text="Path to static image (optional, e.g. 'images/perioperative-img.jpg')")
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Application fee amount")
    paystack_public_key = models.CharField(max_length=200, blank=True, null=True, help_text="Paystack Public Key for payment inline integration")
    fees_structure_pdf = models.FileField(upload_to='fees/', null=True, blank=True, help_text="Upload PDF of the school fees structure")
    fees_structure_text = models.TextField(blank=True, null=True, help_text="Manually write/update the school fees information")

    def __str__(self):
        return self.title

class ApplicationField(models.Model):
    label = models.CharField(max_length=200, help_text="The label of the field, e.g. 'Full Name', 'KCSE Mean Grade'")
    field_type = models.CharField(max_length=50, choices=[
        ('text', 'Short Text'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('textarea', 'Long Text')
    ], default='text', help_text="Type of the input field")
    required = models.BooleanField(default=True, help_text="Is this field required?")
    order = models.IntegerField(default=0, help_text="Display order of this field on the application form")

    def __str__(self):
        return f"{self.label} ({self.get_field_type_display()})"

    class Meta:
        ordering = ['order', 'id']

class ApplicationSubmission(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict, help_text="Dynamically filled fields stored as a JSON object")
    paid = models.BooleanField(default=False, help_text="Whether the application fee was successfully paid")
    payment_reference = models.CharField(max_length=100, blank=True, null=True, help_text="Paystack transaction reference")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Amount paid via Paystack")

    def __str__(self):
        return f"Submission #{self.id} for {self.course.title}"
