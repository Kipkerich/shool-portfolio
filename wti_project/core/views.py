from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from .models import Blog, FAQ, Course, ApplicationField, ApplicationSubmission

def home_view(request):
    blogs = Blog.objects.all()[:3]  # original static page had exactly 3 blogs on the home page
    faqs = FAQ.objects.all()
    return render(request, 'core/index.html', {'blogs': blogs, 'faqs': faqs})

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

def contact_view(request):
    return render(request, 'core/contact.html')
