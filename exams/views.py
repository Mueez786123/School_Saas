from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academics.models import ClassGrade, Subject
from students.models import Student
from .models import Exam, StudentResult
from django.db.models import Sum

@login_required(login_url='login')
def enter_marks(request):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    # Dropdown Data fetch karo
    exams = Exam.objects.filter(school=user.school)
    classes = ClassGrade.objects.filter(school=user.school)
    subjects = Subject.objects.filter(school=user.school)

    # User ne kya select kiya?
    selected_exam_id = request.GET.get('exam')
    selected_class_id = request.GET.get('class_grade')
    selected_subject_id = request.GET.get('subject')

    students_data = []

    if selected_exam_id and selected_class_id and selected_subject_id:
        # Students fetch karo
        students = Student.objects.filter(
            school=user.school,
            current_class_id=selected_class_id,
            status='active'
        ).order_by('roll_number', 'first_name')

        # Har student ke liye check karo ki pehle se marks hain ya nahi
        for std in students:
            result = StudentResult.objects.filter(
                exam_id=selected_exam_id,
                student=std,
                subject_id=selected_subject_id
            ).first()
            
            students_data.append({
                'student': std,
                'marks': result.marks_obtained if result else '' # Agar marks hain toh dikhao, nahi to khali
            })

    # --- SAVE LOGIC (POST Request) ---
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        subject_id = request.POST.get('subject_id')
        
        # Loop through all input fields
        for key, value in request.POST.items():
            if key.startswith('marks_'): # Input name format: marks_STUDENTID
                student_id = key.split('_')[1]
                marks = value

                if marks: # Agar teacher ne kuch likha hai
                    StudentResult.objects.update_or_create(
                        school=user.school,
                        exam_id=exam_id,
                        subject_id=subject_id,
                        student_id=student_id,
                        defaults={'marks_obtained': marks}
                    )

        messages.success(request, "Marks saved successfully!")
        return redirect(request.get_full_path()) # Wapas wahi page reload karo

    context = {
        'exams': exams,
        'classes': classes,
        'subjects': subjects,
        'students_data': students_data,
        'sel_exam': int(selected_exam_id) if selected_exam_id else None,
        'sel_class': int(selected_class_id) if selected_class_id else None,
        'sel_subject': int(selected_subject_id) if selected_subject_id else None,
    }
    return render(request, 'exams/enter_marks.html', context)


@login_required(login_url='login')
def result_list(request):
    """
    Step 1: Exam aur Class select karo, phir bacchon ki list dikhao
    jinke result ban chuke hain.
    """
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    exams = Exam.objects.filter(school=user.school)
    classes = ClassGrade.objects.filter(school=user.school)
    
    selected_exam_id = request.GET.get('exam')
    selected_class_id = request.GET.get('class_grade')
    
    students = []
    
    if selected_exam_id and selected_class_id:
        # Sirf wo students lao jinka kam se kam ek subject ka result ban gaya hai
        students = Student.objects.filter(
            school=user.school,
            current_class_id=selected_class_id,
            status='active'
        ).order_by('roll_number')

    context = {
        'exams': exams,
        'classes': classes,
        'students': students,
        'sel_exam': int(selected_exam_id) if selected_exam_id else None,
        'sel_class': int(selected_class_id) if selected_class_id else None,
    }
    return render(request, 'exams/result_list.html', context)


@login_required(login_url='login')
def generate_report_card(request, student_id, exam_id):
    """
    Step 2: Final Report Card Generate karo
    """
    student = get_object_or_404(Student, pk=student_id, school=request.user.school)
    exam = get_object_or_404(Exam, pk=exam_id, school=request.user.school)
    
    # Saare subjects ke marks nikalo
    results = StudentResult.objects.filter(student=student, exam=exam).select_related('subject')
    
    total_marks_obtained = 0
    total_max_marks = 0
    subjects_data = []
    
    for res in results:
        subjects_data.append(res)
        total_marks_obtained += res.marks_obtained
        total_max_marks += res.subject.total_marks if res.subject else 100

    # Percentage Calculation
    percentage = 0
    if total_max_marks > 0:
        percentage = round((total_marks_obtained / total_max_marks) * 100, 2)

    # Grade Calculation (Simple Logic)
    grade = 'F'
    if percentage >= 90: grade = 'A+'
    elif percentage >= 80: grade = 'A'
    elif percentage >= 70: grade = 'B+'
    elif percentage >= 60: grade = 'B'
    elif percentage >= 50: grade = 'C'
    elif percentage >= 33: grade = 'D'
    
    status = "PASS" if grade != 'F' else "FAIL"

    context = {
        'student': student,
        'exam': exam,
        'results': subjects_data,
        'total_obtained': total_marks_obtained,
        'total_max': total_max_marks,
        'percentage': percentage,
        'grade': grade,
        'status': status,
    }
    return render(request, 'exams/report_card.html', context)