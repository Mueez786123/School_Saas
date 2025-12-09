from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academics.models import ClassGrade, Section
from students.models import Student
from .models import AttendanceSession, StudentAttendance
from django.utils import timezone

@login_required(login_url='login')
def take_attendance(request):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    # Dropdowns ke liye data
    classes = ClassGrade.objects.filter(school=user.school)
    sections = Section.objects.filter(school=user.school)
    
    selected_class_id = request.GET.get('class_grade')
    selected_section_id = request.GET.get('section')
    selected_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))

    students_data = []
    session_obj = None

    # Agar Class aur Section select kiya hai, toh students fetch karo
    if selected_class_id and selected_section_id:
        # Check karo kya is din ki attendance pehle se hai?
        session_obj = AttendanceSession.objects.filter(
            school=user.school,
            class_grade_id=selected_class_id,
            section_id=selected_section_id,
            date=selected_date
        ).first()

        if session_obj:
            # Edit Mode: Purana record dikhao
            students_data = StudentAttendance.objects.filter(session=session_obj).select_related('student')
        else:
            # Create Mode: Sare students fetch karo
            students = Student.objects.filter(
                school=user.school,
                current_class_id=selected_class_id,
                section_id=selected_section_id,
                status='active'
            )
            # Temporary list bana rahe hain display ke liye
            for std in students:
                students_data.append({'student': std, 'status': 'P'}) # Default Present

    # --- SAVE LOGIC (POST Request) ---
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        section_id = request.POST.get('section_id')
        date = request.POST.get('date')

        # 1. Session Create/Get karo
        session, created = AttendanceSession.objects.get_or_create(
            school=user.school,
            class_grade_id=class_id,
            section_id=section_id,
            date=date,
            defaults={'taken_by': user}
        )

        # 2. Har student ka status save karo
        students = Student.objects.filter(school=user.school, current_class_id=class_id, section_id=section_id, status='active')
        
        for std in students:
            status = request.POST.get(f'status_{std.id}') # HTML se status milega
            
            # Update or Create record
            StudentAttendance.objects.update_or_create(
                session=session,
                student=std,
                defaults={'status': status}
            )
        
        messages.success(request, f"Attendance saved for {date}!")
        return redirect('dashboard')

    context = {
        'classes': classes,
        'sections': sections,
        'students_data': students_data,
        'session_obj': session_obj,
        'selected_class_id': int(selected_class_id) if selected_class_id else None,
        'selected_section_id': int(selected_section_id) if selected_section_id else None,
        'selected_date': selected_date
    }
    return render(request, 'attendance/take_attendance.html', context)