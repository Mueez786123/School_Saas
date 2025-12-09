from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core.views import dashboard, subscription_expired

from students.views import (
    student_admission, student_list, student_edit, 
    generate_id_card, bulk_upload_students,
    student_profile, student_fee_ledger, # 👈New Imports
    print_admission_form,
)
from expenses.views import expense_list, delete_expense # 👈 Add
from fees.views import collect_fees, payment_receipt
from attendance.views import take_attendance
from exams.views import enter_marks, generate_report_card, result_list 


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Core & Students
    path('', dashboard, name='dashboard'),
    path('admission/new/', student_admission, name='student_admission'),
    path('students/', student_list, name='student_list'),
    path('student/edit/<int:pk>/', student_edit, name='student_edit'),

    # Fees (This was the issue)
    path('fees/collect/', collect_fees, name='collect_fees'), 
    path('fees/receipt/<int:pk>/', payment_receipt, name='payment_receipt'), # 👈 New URL
    path('attendance/take/', take_attendance, name='take_attendance'), # 👈 New URL
    path('exams/marks/', enter_marks, name='enter_marks'), # 👈 New Path
    path('exams/results/', result_list, name='result_list'),
    path('exams/report/<int:student_id>/<int:exam_id>/', generate_report_card, name='student_report_card'),
    path('student/id-card/<int:pk>/', generate_id_card, name='generate_id_card'), # 👈 New URL
    path('students/bulk-upload/', bulk_upload_students, name='bulk_upload_students'), # 👈 New URL
    path('subscription-expired/', subscription_expired, name='subscription_expired'), # 👈 New URL
    path('student/profile/<int:pk>/', student_profile, name='student_profile'),
    path('student/ledger/<int:pk>/', student_fee_ledger, name='student_fee_ledger'),
    path('student/print-form/<int:pk>/', print_admission_form, name='print_admission_form'), # 👈 NEW URL
    path('expenses/', expense_list, name='expense_list'),
    path('expenses/delete/<int:pk>/', delete_expense, name='delete_expense'),
]
    


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    