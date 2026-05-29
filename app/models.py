from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ResumeTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image= models.ImageField(null=True, blank=True)
    button_color = models.CharField(max_length=20)

    def __str__(self):
        return self.name
        
class PersonalInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    linkedin = models.URLField(blank=True, null=True)
    summary = models.TextField() 

    def __str__(self):
        return f"{self.user.username}'s Contact Info"   
    
class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.job_title} at {self.company}"
    
class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    passing_year = models.CharField(max_length=4) 

    def __str__(self):
        return f"{self.degree} from {self.school}"    

class Skill(models.Model):
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill_name = models.CharField(max_length=50)
    proficiency = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Intermediate')

    def __str__(self):
        return self.skill_name    

class AdditionalDetail(models.Model):
    CATEGORY_CHOICES = [
        ('Project', 'Project'),
        ('Certification', 'Certification'),
        ('Tool', 'Tool / Software'),
        ('Soft Skill', 'Soft Skill'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Project')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.category}: {self.title}"
    
class CoverLetterTemplate(models.Model):
    """
    Stores metadata for each designed cover letter layout styling.
    """
    name = models.CharField(max_length=100, help_text="e.g., Modern Minimalist, Tech Corporate")
    description = models.TextField(blank=True, null=True, help_text="Short detail about layout focus.")
    
    # FIXED LINE HERE:
    image = models.ImageField(upload_to='cl_templates/thumbnails/', blank=True, null=True)
    
    file_path = models.CharField(max_length=255, help_text="The internal template file path, e.g., cl_layouts/modern.html")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SavedCoverLetter(models.Model):
    """
    Captures all textual data submitted by a specific user for a target cover letter document.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cover_letters')
    template = models.ForeignKey(CoverLetterTemplate, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, default="My Cover Letter", help_text="Internal title name for dashboard tracking")
    sender_name = models.CharField(max_length=150)
    sender_email = models.EmailField()
    sender_phone = models.CharField(max_length=20, blank=True, null=True)
    sender_location = models.CharField(max_length=255, blank=True, null=True)
    recipient_name = models.CharField(max_length=150, blank=True, null=True, help_text="e.g., Hiring Manager, HR Team")
    company_name = models.CharField(max_length=150)
    job_title = models.CharField(max_length=150, help_text="The designation you're targeted towards")
    letter_body = models.TextField()
    signature_data = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_updated']

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.company_name})"        

