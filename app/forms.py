# forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PersonalInfo, Experience, Education, Skill, AdditionalDetail

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomSignupForm(UserCreationForm):
    # 1. Explicitly declare these fields so we can force them to be required
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        # 2. Notice 'username' is NOT in this list. This hides it from the user!
        fields = ['first_name', 'last_name', 'email'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply your sleek CSS styling to all fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control rounded-pill'

    # 3. Ensure emails are unique (Django allows duplicate emails by default!)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    # 4. THE NINJA TRICK: Handle the missing username behind the scenes
    def save(self, commit=True):
        # Get the user object, but pause before saving to the database
        user = super().save(commit=False)
        
        # Secretly assign their email address to the required username field
        user.username = self.cleaned_data['email']
        
        # Now it is safe to save!
        if commit:
            user.save()
        return user


class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control rounded-pill'})
    )
    password = forms.CharField(
        required=True, 
        widget=forms.PasswordInput(attrs={'class': 'form-control rounded-pill'})
    )

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = ['full_name', 'phone', 'address', 'linkedin', 'summary']
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'e.g. John Doe'}),
            'phone': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'e.g. +91 234 567 8900'}),
            'address': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'City, State'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'https://linkedin.com/in/username'}),
            'summary': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 7, 'placeholder': 'A brief summary of your career...'})
        }  

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title','company','start_date','end_date','description']

        widgets={
            'job_title':forms.TextInput(attrs={'class':'form-control rounded-pill','placeholder':'e.g. Web Developer'}),
            'company':forms.TextInput(attrs={'class':'form-control rounded-pill','placeholder':'e.g. Google'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control rounded-pill', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control rounded-pill', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 5, 'placeholder': 'Describe your responsibilities...'})
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'school', 'passing_year']
        
        widgets = {
            'degree': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'e.g. B.Tech in Computer Science'}),
            'school': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'e.g. Uttaranchal College of Science and Technology'}),
            'passing_year': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'e.g. 2026'}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['skill_name', 'proficiency']
        
        widgets = {
            'skill_name': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'e.g. Python, Django, React...'}),
            'proficiency': forms.Select(attrs={'class': 'form-select rounded-pill'}),
        }

class AdditionalDetailForm(forms.ModelForm):
    class Meta:
        model = AdditionalDetail
        fields = ['category', 'title', 'link', 'description']
        
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select rounded-pill fw-bold'}),
            'title': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'e.g. Smart Study Planner, VS Code, or AWS Certified'}),
            'link': forms.URLInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'e.g. https://github.com/yourname/project (Optional)'}),
            'description': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 2, 'placeholder': 'e.g. Built a full-stack application using Django... (Optional)'}),
        }        