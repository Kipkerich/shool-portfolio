from django.test import TestCase
from django.urls import reverse
from .models import Blog, FAQ, Course, ApplicationField, ApplicationSubmission
import datetime

class WTIPagesTestCase(TestCase):
    def setUp(self):
        # Create mock Blog posts
        Blog.objects.create(
            title="Admissions Officially Open for Next Intake",
            category="Announcements",
            date=datetime.date(2026, 3, 12),
            content="Applications are now actively being processed...",
            image_path="images/blog-1.jpg"
        )

        # Create mock FAQs
        FAQ.objects.create(
            question="Is Wama Training Institute registered and accredited?",
            answer="Yes, Wama Training Institute (WTI) is fully registered and accredited...",
            order=1
        )
        FAQ.objects.create(
            question="Where is Wama Training Institute located?",
            answer="We are conveniently located in Ongata Rongai...",
            order=2
        )

        # Create mock Course
        self.course = Course.objects.create(
            title="Perioperative Theatre Technology",
            description="Sterile setups and patient preparation...",
            level="Level 5 & 6",
            image_path="images/perioperative-img.jpg",
            application_fee=1500.00,
            paystack_public_key="pk_test_12345",
            fees_structure_text="Tuition is KES 45,000"
        )

        # Create mock Application Fields
        self.field_name = ApplicationField.objects.create(
            label="Full Name",
            field_type="text",
            required=True,
            order=1
        )
        self.field_email = ApplicationField.objects.create(
            label="Email Address",
            field_type="email",
            required=True,
            order=2
        )

    def test_home_page_status_code(self):
        """Test that the homepage returns status code 200 and uses correct template."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
        self.assertTemplateUsed(response, 'core/base.html')

    def test_about_page_status_code(self):
        """Test that the about page returns status code 200."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_courses_page_status_code(self):
        """Test that the courses page returns status code 200."""
        response = self.client.get(reverse('courses'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page_status_code(self):
        """Test that the contact page returns status code 200."""
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_blog_page_status_code_and_template(self):
        """Test that the new blog page returns status code 200 and uses blog.html."""
        response = self.client.get(reverse('blog'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/blog.html')
        self.assertTemplateUsed(response, 'core/base.html')

    def test_homepage_contains_faq_section(self):
        """Test that the homepage contains the FAQ section and its questions."""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Frequently Asked Questions')
        self.assertContains(response, 'Is Wama Training Institute registered and accredited?')
        self.assertContains(response, 'Where is Wama Training Institute located?')

    def test_homepage_contains_news_horizontal_layout(self):
        """Test that the homepage has horizontal news cards."""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'news-horizontal-card')
        self.assertContains(response, 'Admissions Officially Open for Next Intake')

    def test_course_detail_page(self):
        """Test that course detail page displays information successfully."""
        response = self.client.get(reverse('course_detail', kwargs={'course_id': self.course.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/course_detail.html')
        self.assertContains(response, self.course.title)
        self.assertContains(response, "Tuition is KES 45,000")

    def test_apply_page_get(self):
        """Test that applying displays the dynamic fields on GET request."""
        response = self.client.get(reverse('apply', kwargs={'course_id': self.course.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/apply.html')
        self.assertContains(response, "Full Name")
        self.assertContains(response, "Email Address")

    def test_apply_page_post_and_payment_page(self):
        """Test that submitting the application form saves a submission and redirects to paystack payment."""
        form_data = {
            f'field_{self.field_name.id}': 'John Doe',
            f'field_{self.field_email.id}': 'john@example.com'
        }
        response = self.client.post(reverse('apply', kwargs={'course_id': self.course.id}), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/payment_paystack.html')

        # Check that submission was created
        submission = ApplicationSubmission.objects.get(course=self.course)
        self.assertEqual(submission.data["Full Name"], "John Doe")
        self.assertEqual(submission.data["Email Address"], "john@example.com")
        self.assertFalse(submission.paid)
