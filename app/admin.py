from django.contrib import admin
from django.contrib import admin
from .models import ResumeTemplate,PersonalInfo,Experience,Skill
from .models import CoverLetterTemplate, SavedCoverLetter

# Register your models here.

admin.site.register(ResumeTemplate)
admin.site.register(PersonalInfo)
admin.site.register(Experience)
admin.site.register(Skill)
admin.site.register(CoverLetterTemplate)
admin.site.register(SavedCoverLetter)