from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from .models import Blog, FAQ, Course, ApplicationField, ApplicationSubmission

def home_view(request):
    blogs = Blog.objects.all()[:3]  # original static page had exactly 3 blogs on the home page
    faqs = FAQ.objects.all()
    courses = Course.objects.all()
    return render(request, 'core/index.html', {
        'blogs': blogs,
        'faqs': faqs,
        'courses': courses,
    })

def about_view(request):
    return render(request, 'core/about.html')

def courses_view(request):
    courses = Course.objects.all()
    return render(request, 'core/courses.html', {'courses': courses})

def course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'core/course_detail.html', {'course': course})

def apply_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    fields = ApplicationField.objects.all()

    if not course.is_open:
        return render(request, 'core/apply.html', {
            'course': course,
            'fields': fields,
            'error': "Applications for this course are currently closed."
        })

    if request.method == 'POST':
        # Gather all dynamic form field submissions
        data = {}
        for field in fields:
            value = request.POST.get(f'field_{field.id}', '').strip()
            data[field.label] = value

        # Save submission
        submission = ApplicationSubmission.objects.create(
            course=course,
            data=data,
            paid=False
        )

        # If application_fee is 0 or no paystack public key is set, mark as paid automatically and redirect
        if course.application_fee <= 0 or not course.paystack_public_key:
            submission.paid = True
            submission.save()
            return redirect('application_success', course_id=course.id)

        # Otherwise, render application payment transition page with Paystack inline variables
        student_email = data.get('Email Address') or data.get('Email') or 'applicant@wamatraininginstitute.ac.ke'
        return render(request, 'core/payment_paystack.html', {
            'course': course,
            'submission': submission,
            'student_email': student_email,
            'amount_kobo': int(course.application_fee * 100),
            'paystack_public_key': course.paystack_public_key
        })

    return render(request, 'core/apply.html', {'course': course, 'fields': fields})

def payment_callback_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    reference = request.GET.get('reference')
    submission_id = request.GET.get('submission_id')

    if not reference or not submission_id:
        return HttpResponseBadRequest("Missing reference or submission_id parameter.")

    submission = get_object_or_404(ApplicationSubmission, id=submission_id, course=course)
    submission.paid = True
    submission.payment_reference = reference
    submission.amount_paid = course.application_fee
    submission.save()

    return redirect('application_success', course_id=course.id)

def application_success_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'core/payment_success.html', {'course': course})

def blog_view(request):
    blogs = Blog.objects.all()
    return render(request, 'core/blog.html', {'blogs': blogs})

from django.core.mail import send_mail

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        subject_input = request.POST.get('subject', '').strip()
        message_input = request.POST.get('message', '').strip()

        if not name or not phone_number or not subject_input or not message_input:
            return render(request, 'core/contact.html', {
                'error': 'All fields are required.'
            })

        # Build email content
        subject = f"Contact Form Submission: {subject_input}"
        body = f"Name: {name}\nPhone Number: {phone_number}\n\nMessage:\n{message_input}"
        recipient_list = ['wamatraininginstitute@gmail.com']

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email='noreply@wamatraininginstitute.ac.ke',
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return render(request, 'core/contact.html', {'success': True})
        except Exception as e:
            return render(request, 'core/contact.html', {
                'error': f"An error occurred while sending your message: {str(e)}"
            })

    return render(request, 'core/contact.html')
