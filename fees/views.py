from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from students.models import Student
from urllib.parse import quote
from .models import FeeStructure, FeePayment

# 1. FEES COLLECT VIEW (Search + Calculate + Pay)
@login_required(login_url='login')
def collect_fees(request):
    student = None
    fee_structures = []
    total_fee = 0
    total_paid = 0
    balance = 0
    
    # URL se admission number lena (Search ke baad)
    search_adm_no = request.GET.get('admission_no')

    if search_adm_no:
        try:
            # 🔍 SEARCH LOGIC: Sirf apne school ka student
            student = Student.objects.get(admission_no=search_adm_no, school=request.user.school)
            
            # 🧮 CALCULATION LOGIC
            # Step A: Student ki class ki Total Fees nikalo
            structures = FeeStructure.objects.filter(class_grade=student.current_class, school=request.user.school)
            fee_structures = structures  # List dikhane ke liye
            
            # Aggregate function use karke sum nikalo
            total_fee_data = structures.aggregate(Sum('amount'))
            total_fee = total_fee_data['amount__sum'] or 0  # Agar None hai to 0 maano

            # Step B: Ab tak kitna pay kiya hai wo nikalo
            paid_data = FeePayment.objects.filter(student=student).aggregate(Sum('amount_paid'))
            total_paid = paid_data['amount_paid__sum'] or 0

            # Step C: Balance = Total - Paid
            balance = total_fee - total_paid

        except Student.DoesNotExist:
            messages.error(request, "Student not found with this Admission Number!")

    # 💸 PAYMENT LOGIC (Form Submit hone par)
    if request.method == 'POST' and student:
        try:
            amount = float(request.POST.get('amount'))
            mode = request.POST.get('mode')
            remarks = request.POST.get('remarks')
            date = request.POST.get('date')

            if amount > 0:
                # Payment Record Save karo
                payment = FeePayment.objects.create(
                    school=request.user.school,
                    student=student,
                    amount_paid=amount,
                    payment_date=date,
                    mode=mode,
                    remarks=remarks
                )
                
                messages.success(request, f"Success! ₹{amount} collected.")
                
                # 🖨️ Redirect to Receipt Page (New Logic)
                return redirect('payment_receipt', pk=payment.pk)
                
        except ValueError:
            messages.error(request, "Invalid Amount Entered!")

    context = {
        'student': student,
        'fee_structures': fee_structures,
        'total_fee': total_fee,
        'total_paid': total_paid,
        'balance': balance,
        'search_adm_no': search_adm_no
    }
    return render(request, 'fees/collect_fees.html', context)

# 2. RECEIPT VIEW (Payment hone ke baad yahan aayega)
@login_required(login_url='login')
def payment_receipt(request, pk):
    # Sirf apne school ki receipt dekh sakein
    payment = get_object_or_404(FeePayment, pk=pk, school=request.user.school)
    return render(request, 'fees/receipt.html', {'payment': payment})




@login_required(login_url='login')
def payment_receipt(request, pk):
    # Security: Sirf apne school ki receipt dekh sakein
    payment = get_object_or_404(FeePayment, pk=pk, school=request.user.school)
    
    # --- 📲 WHATSAPP LOGIC START ---
    student = payment.student
    school_name = payment.school.name
    
    # 1. Message Taiyar Karo
    message = (
        f"✅ Fees Received!\n\n"
        f"Dear Parent,\n"
        f"We have received ₹{payment.amount_paid} for {student.first_name} {student.last_name}.\n"
        f"Receipt No: #{payment.id}\n"
        f"Date: {payment.payment_date}\n\n"
        f"Thank you,\n"
        f"*{school_name}*"
    )
    
    # 2. URL Safe Banao (Spaces ko %20 me badalna padta hai)
    encoded_message = quote(message)
    
    # 3. Mobile Number Format Karo (India ke liye 91 lagana zaroori hai)
    mobile = str(student.father_mobile).strip()
    if not mobile.startswith("91") and not mobile.startswith("+91"):
        mobile = "91" + mobile  # Default India Code
    
    # 4. Final Link
    whatsapp_url = f"https://wa.me/{mobile}?text={encoded_message}"
    # --- WHATSAPP LOGIC END ---

    return render(request, 'fees/receipt.html', {
        'payment': payment,
        'whatsapp_url': whatsapp_url  # 👈 Template ko bhejo
    })