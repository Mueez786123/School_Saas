from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentAdmissionForm
from django.db.models import Q 
from .models import Student, ClassGrade, Section
import pandas as pd
from django.conf import settings
import os 
from django.utils import timezone

from fees.models import FeePayment, FeeStructure
from django.db.models import Sum


@login_required(login_url='login')
def student_admission(request):
    # Security Check: Kya user ke paas school hai?
    if not request.user.school:
        return render(request, 'core/error.html', {'message': "You are not assigned to any school."})

    if request.method == 'POST':
        # Form mein user pass kar rahe hain taaki dropdown filter ho sake
        form = StudentAdmissionForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = request.user.school  # 🔒 Auto-assign School
            student.save()
            
            messages.success(request, f"Success! {student.first_name} ka admission ho gaya.")
            return redirect('dashboard') # Admission ke baad dashboard par bhejo
    else:
        form = StudentAdmissionForm(request.user)

    return render(request, 'students/admission_form.html', {'form': form})

@login_required(login_url='login')
def student_list(request):
    # 1. Security Check: User ke paas school hona chahiye
    if not request.user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    # 2. Base Query: Sirf logged-in user ke school ka data
    # select_related use kiya taaki database queries kam ho jayein (Performance Optimization)
    students = Student.objects.filter(school=request.user.school).select_related('current_class', 'section')

    # 3. Search Logic
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(admission_no__icontains=search_query) |
            Q(father_mobile__icontains=search_query)
        )

    context = {
        'students': students,
        'search_query': search_query
    }
    return render(request, 'students/student_list.html', context)

@login_required(login_url='login')
def student_edit(request, pk):
    # 1. Student dhundo (Security: Sirf apne school ka)
    student = get_object_or_404(Student, pk=pk, school=request.user.school)

    if request.method == 'POST':
        form = StudentAdmissionForm(request.user, request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student details updated successfully!")
            return redirect('student_list')
    else:
        # Form ko student ke purane data ke saath load karo
        form = StudentAdmissionForm(request.user, instance=student)

    return render(request, 'students/edit_student.html', {'form': form, 'student': student})


# students/views.py

@login_required(login_url='login')
def generate_id_card(request, pk):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    # Sirf apne school ka student fetch karo
    student = get_object_or_404(Student, pk=pk, school=user.school)
    
    context = {
        'student': student,
        'school': user.school
    }
    return render(request, 'students/id_card.html', context)


@login_required(login_url='login')
def bulk_upload_students(request):
    user = request.user
    if not user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, "Please upload a valid Excel file.")
            return redirect('bulk_upload_students')

        try:
            # Pandas se file padho
            df = pd.read_excel(excel_file, dtype=str)
            df.columns = df.columns.str.strip() # Headers ke spaces hatao
            
            # Zaroori Columns check karo
            required_columns = ['First Name', 'Admission No', 'Class', 'Father Name', 'Mobile']
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                messages.error(request, f"Excel me ye zaroori columns nahi hain: {', '.join(missing_cols)}")
                return redirect('bulk_upload_students')

            success_count = 0
            skipped_rows = []

            for index, row in df.iterrows():
                row_num = index + 2
                
                # Helper function to clean data
                def clean_val(val):
                    if pd.isna(val) or str(val).lower() == 'nan': return ''
                    return str(val).strip()

                # --- 1. Excel se Data Nikalo ---
                first_name = clean_val(row.get('First Name'))
                last_name = clean_val(row.get('Last Name'))
                adm_no = clean_val(row.get('Admission No'))
                class_name = clean_val(row.get('Class'))
                section_name = clean_val(row.get('Section'))
                roll_no_str = clean_val(row.get('Roll Number'))
                
                # Parents
                father_name = clean_val(row.get('Father Name'))
                mother_name = clean_val(row.get('Mother Name'))
                father_mobile = clean_val(row.get('Mobile'))
                
                # Details
                gender_raw = clean_val(row.get('Gender')) # Male/Female
                aadhar = clean_val(row.get('Aadhar No'))
                category = clean_val(row.get('Category')) # OBC, General etc.
                religion = clean_val(row.get('Religion')) # Islam, Hindu etc.
                blood_group = clean_val(row.get('Blood Group'))

                # Basic Validation
                if not first_name or not adm_no or not class_name:
                    skipped_rows.append(f"Row {row_num}: Name, Class ya Admission No missing hai.")
                    continue

                try:
                    # --- 2. Class aur Section Match Karo ---
                    # Dhyan rahe: Excel me '9th' likha hai to Admin panel me bhi '9th' hona chahiye
                    # Ya agar Admin panel me 'Class 9' hai to Excel me bhi 'Class 9' likho.
                    class_obj = ClassGrade.objects.filter(school=user.school, name__iexact=class_name).first()
                    
                    if not class_obj:
                        skipped_rows.append(f"Row {row_num}: Class '{class_name}' software me nahi mili. Spelling check karein.")
                        continue

                    section_obj = None
                    if section_name:
                        section_obj = Section.objects.filter(school=user.school, name__iexact=section_name, class_grade=class_obj).first()

                    # --- 3. Gender Format Fix (Male -> M) ---
                    gender_code = 'M' # Default
                    if gender_raw:
                        if gender_raw.lower().startswith('f'): gender_code = 'F'
                        elif gender_raw.lower().startswith('o'): gender_code = 'O'
                        elif gender_raw.lower().startswith('m'): gender_code = 'M'

                    # --- 4. Roll Number Fix ---
                    roll_number = None
                    if roll_no_str and roll_no_str.isdigit():
                        roll_number = int(roll_no_str)

                    # --- 5. Save Student ---
                    student, created = Student.objects.update_or_create(
                        school=user.school,
                        admission_no=adm_no,
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'roll_number': roll_number,
                            'current_class': class_obj,
                            'section': section_obj,
                            
                            # Parents
                            'father_name': father_name,
                            'mother_name': mother_name,
                            'father_mobile': father_mobile,
                            
                            # Extra Details
                            'gender': gender_code,
                            'aadhar_no': aadhar,
                            'category': category,
                            'religion': religion,
                            'blood_group': blood_group,
                            
                            # Defaults
                            'admission_date': timezone.now().date(),
                            'address': 'Address Update Pending'
                        }
                    )
                    success_count += 1

                except Exception as e:
                    skipped_rows.append(f"Row {row_num} Error: {str(e)}")

            # --- Result ---
            if success_count > 0:
                messages.success(request, f"Successfully imported {success_count} students with full details!")
            
            if skipped_rows:
                # Sirf pehle 10 errors dikhao taaki screen na bhare
                messages.warning(request, "Kuch students skip huye:<br>" + "<br>".join(skipped_rows[:10]))

            return redirect('student_list')

        except Exception as e:
            messages.error(request, f"Critical Error: {str(e)}")
            return redirect('bulk_upload_students')

    return render(request, 'students/bulk_upload.html')

@login_required(login_url='login')
def student_profile(request, pk):
    # Student Data
    student = get_object_or_404(Student, pk=pk, school=request.user.school)
    return render(request, 'students/student_profile.html', {'student': student})

@login_required(login_url='login')
def student_fee_ledger(request, pk):
    # Student Fees History
    student = get_object_or_404(Student, pk=pk, school=request.user.school)
    
    # History
    payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
    total_paid = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    # Total Payable (Structure se)
    structures = FeeStructure.objects.filter(class_grade=student.current_class, school=request.user.school)
    total_payable = structures.aggregate(Sum('amount'))['amount__sum'] or 0
    
    balance = total_payable - total_paid

    context = {
        'student': student,
        'payments': payments,
        'total_paid': total_paid,
        'total_payable': total_payable,
        'balance': balance
    }
    return render(request, 'students/student_ledger.html', context)



@login_required(login_url='login')
def print_admission_form(request, pk):
    # Security: Sirf apne school ka student
    student = get_object_or_404(Student, pk=pk, school=request.user.school)
    return render(request, 'students/print_admission_form.html', {'student': student})