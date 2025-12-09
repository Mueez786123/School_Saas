from django import forms
from .models import Student
from academics.models import ClassGrade, Section

class StudentAdmissionForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'admission_no', 'roll_number',   'admission_date',
            'gender', 'dob', 
            'blood_group', 'religion', 'category', 'aadhar_no',  # 👈 New Fields
            'father_name', 'father_occupation', 'mother_name', 'father_mobile', # 👈 Parents Info
            'address', 'current_class', 'section', 'photo'
        ]
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        """
        SaaS Magic: Form initialize hote waqt logged-in user ka school check karo
        aur sirf ussi school ki classes/sections dikhao.
        """
        super(StudentAdmissionForm, self).__init__(*args, **kwargs)
        
        # Dropdowns ko Bootstrap look dene ke liye loop
        for field in self.fields:
            if field not in ['admission_date', 'dob']: # Inka widget upar set hai
                self.fields[field].widget.attrs.update({'class': 'form-control'})

        # 🛡️ DATA ISOLATION LOGIC
        if user.school:
            self.fields['current_class'].queryset = ClassGrade.objects.filter(school=user.school)
            self.fields['section'].queryset = Section.objects.filter(school=user.school)
        else:
            # Agar user ke paas school nahi hai (safety fallback)
            self.fields['current_class'].queryset = ClassGrade.objects.none()
            self.fields['section'].queryset = Section.objects.none()