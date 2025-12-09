from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Expense, ExpenseCategory
from .forms import ExpenseForm

@login_required(login_url='login')
def expense_list(request):
    if not request.user.school:
        return render(request, 'core/error.html', {'message': "Restricted Access"})

    expenses = Expense.objects.filter(school=request.user.school).order_by('-date')
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Add Expense Logic (Modal ya Page ke liye)
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.school = request.user.school
            exp.added_by = request.user
            exp.save()
            messages.success(request, "Expense Added Successfully!")
            return redirect('expense_list')
        else:
            messages.error(request, "Error adding expense.")
    else:
        form = ExpenseForm(request.user)

    context = {
        'expenses': expenses,
        'total_expense': total_expense,
        'form': form
    }
    return render(request, 'expenses/expense_list.html', context)

@login_required(login_url='login')
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, school=request.user.school)
    expense.delete()
    messages.success(request, "Expense Deleted.")
    return redirect('expense_list')