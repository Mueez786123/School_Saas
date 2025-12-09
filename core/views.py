from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from students.models import Student
from academics.models import ClassGrade
from fees.models import FeePayment

@login_required(login_url='login')
def dashboard(request):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    # 1. Basic Counters
    total_students = Student.objects.filter(school=user.school, status='active').count()
    total_classes = ClassGrade.objects.filter(school=user.school).count()
    
    # 2. Today's Collection
    today = timezone.now().date()
    todays_collection = FeePayment.objects.filter(
        school=user.school, 
        payment_date=today
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    # 3. Monthly Graph Data (Last 6 Months)
    # Hum pichle 6 mahine ka loop chalayenge aur data nikalenge
    labels = []
    data = []
    
    current_date = today
    for i in range(5, -1, -1): # 5 se 0 tak (6 mahine)
        # Mahine ka start aur end nikalna thoda complex hota hai, 
        # hum simple logic use kar rahe hain for MVP
        month_start = (current_date.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Query
        monthly_total = FeePayment.objects.filter(
            school=user.school,
            payment_date__range=[month_start, month_end]
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        labels.append(month_start.strftime("%B")) # e.g. "January"
        data.append(float(monthly_total))

    context = {
        'school_name': user.school.name,
        'total_students': total_students,
        'total_classes': total_classes,
        'todays_collection': todays_collection,
        'role': user.get_role_display(),
        # Chart Data
        'chart_labels': labels,
        'chart_data': data,
    }
    
    return render(request, 'core/dashboard.html', context)

def subscription_expired(request):
    return render(request, 'core/subscription_expired.html')