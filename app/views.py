from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomSignupForm, EmailLoginForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import PersonalInfoForm, ExperienceForm, EducationForm, SkillForm, AdditionalDetailForm
from django.contrib.auth.decorators import login_required
from .models import ResumeTemplate, PersonalInfo, Experience, Education, Skill, AdditionalDetail
import json

import google.generativeai as legacy_genai
import base64
import PyPDF2
from io import BytesIO
from PIL import Image
from django.http import JsonResponse, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import CoverLetterTemplate, SavedCoverLetter
from django.views.decorators.csrf import csrf_exempt

from google import genai

import os
from dotenv import load_dotenv
load_dotenv()


client = genai.Client(api_key=os.getenv(api_key="AIzaSyA2JJqaqY2lPmTc2WKvURh5Nu08gwY3Ynw"))

def home(request):
    return render(request, 'home.html')

def nav(request):
    return render(request, 'nav.html')

def select_template(request):
    templates_from_db = ResumeTemplate.objects.all()
    return render(request, 'select_template.html', {'templates': templates_from_db})

def login(request):
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)   
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            try:
                user_obj = User.objects.get(email=email)               
                user = authenticate(username=user_obj.username, password=password)
                if user is not None:
                    auth_login(request, user)
                    messages.success(request, f"Welcome back! 👋")
                    return redirect('/')
                else:
                    messages.error(request, "Invalid email or password.")  
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
            except User.MultipleObjectsReturned:
                messages.error(request, "Account error. Please contact support.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmailLoginForm()
    return render(request, 'login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created successfully ✅")
            return redirect('/')
        else:
            messages.error(request, "Something went wrong ❌ Please check details")
    else:
        form = CustomSignupForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('/login')

# --- STEP 1: PERSONAL INFO ---
@login_required(login_url='/login/')
def resume_builder(request, template_id):
    selected_template = get_object_or_404(ResumeTemplate, id=template_id)
    info, created = PersonalInfo.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, instance=info)
        if form.is_valid():
            form.save()
            return redirect('add_experience', template_id=template_id)   
    else:
        form = PersonalInfoForm(instance=info)        
    return render(request, 'resume_builder.html', {'form': form, 'template': selected_template})

# --- STEP 2: EXPERIENCE ---
@login_required(login_url='/login/')
def add_experience(request, template_id):
    selected_template = get_object_or_404(ResumeTemplate, id=template_id)
    user_jobs = Experience.objects.filter(user=request.user).order_by('-start_date')
    user_resume = PersonalInfo.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            return redirect('add_experience', template_id=template_id)       
    else:
        form = ExperienceForm()
        
    context = {
        'form': form, 
        'template': selected_template, 
        'jobs': user_jobs,
        'resume': user_resume
    }
    return render(request, 'add_experience.html', context)        

@login_required(login_url='/login/')
def delete_experience(request, template_id, job_id):
    job_to_delete = get_object_or_404(Experience, id=job_id, user=request.user)
    job_to_delete.delete()
    return redirect('add_experience', template_id=template_id)

# --- STEP 3: EDUCATION (FIXED!) ---
@login_required(login_url='/login/')
def add_education(request, template_id):
    selected_template = get_object_or_404(ResumeTemplate, id=template_id)
    user_education = Education.objects.filter(user=request.user).order_by('-passing_year')
    user_resume = PersonalInfo.objects.filter(user=request.user).first()
    user_experience = Experience.objects.filter(user=request.user).order_by('-start_date')

    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.user = request.user
            edu.save()
            return redirect('add_education', template_id=template_id)
    else:
        form = EducationForm()
        
    context = {
        'form': form, 
        'template': selected_template, 
        'education_list': user_education,
        'resume': user_resume,
        'experience_list': user_experience
    }
    return render(request, 'add_education.html', context) # FIXED: Now passing the complete context dictionary

@login_required(login_url='/login/')
def delete_education(request, template_id, edu_id):
    edu_to_delete = get_object_or_404(Education, id=edu_id, user=request.user)
    edu_to_delete.delete()
    return redirect('add_education', template_id=template_id)

# --- STEP 4: SKILLS ---
@login_required(login_url='/login/')
def add_skill(request, template_id):
    selected_template = get_object_or_404(ResumeTemplate, id=template_id)
    user_skills = Skill.objects.filter(user=request.user)

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            return redirect('add_skill', template_id=template_id)
    else:
        form = SkillForm()
    return render(request, 'add_skill.html', {'form': form, 'template': selected_template, 'skills': user_skills})

@login_required(login_url='/login/')
def delete_skill(request, template_id, skill_id):
    skill_to_delete = get_object_or_404(Skill, id=skill_id, user=request.user)
    skill_to_delete.delete()
    return redirect('add_skill', template_id=template_id)

# --- STEP 5: ADDITIONAL DETAILS ---
@login_required(login_url='/login/')
def add_details(request, template_id):
    selected_template = get_object_or_404(ResumeTemplate, id=template_id)
    user_details = AdditionalDetail.objects.filter(user=request.user).order_by('category')

    if request.method == 'POST':
        form = AdditionalDetailForm(request.POST)
        if form.is_valid():
            detail = form.save(commit=False)
            detail.user = request.user
            detail.save()
            return redirect('add_details', template_id=template_id)
    else:
        form = AdditionalDetailForm()

    return render(request, 'add_details.html', {'form': form, 'template': selected_template, 'details': user_details})

@login_required(login_url='/login/')
def delete_detail(request, template_id, detail_id):
    detail_to_delete = get_object_or_404(AdditionalDetail, id=detail_id, user=request.user)
    detail_to_delete.delete()
    return redirect('add_details', template_id=template_id)  

@login_required(login_url='/login/')
def resume_preview(request, template_id):
    selected_template = get_object_or_404(ResumeTemplate, id=template_id)
    
    info = PersonalInfo.objects.filter(user=request.user).first()
    experience = Experience.objects.filter(user=request.user).order_by('-start_date')
    education = Education.objects.filter(user=request.user).order_by('-passing_year')
    skills = Skill.objects.filter(user=request.user)
    extras = AdditionalDetail.objects.filter(user=request.user)
    
    context = {
        'template': selected_template,
        'info': info,
        'experience': experience,
        'education': education,
        'skills': skills,
        'extras': extras
    }

    if selected_template.id == 1:
        return render(request, 'resumes/resume_samira.html', context)
    elif selected_template.id == 2:
        return render(request, 'resumes/resume_isabel.html', context)
    elif selected_template.id == 3:
        return render(request, 'resumes/resume_laurice.html', context)
    elif selected_template.id == 4:
        return render(request, 'resumes/resume_olivia.html', context)
    elif selected_template.id == 5:
        return render(request, 'resumes/resume_jacqueline.html', context)
    elif selected_template.id == 6:
        return render(request, 'resumes/resume_pragya.html', context)
    elif selected_template.id == 11:
        return render(request, 'resumes/resume_lorna.html', context)
    elif selected_template.id == 12:
        return render(request, 'resumes/resume_hannah.html', context)
    elif selected_template.id == 13:
        return render(request, 'resumes/resume_seema.html', context)
    elif selected_template.id == 14:
        return render(request, 'resumes/resume_emaa.html', context)
    else:
        return render(request, 'resume_preview.html', context)

# --- EXPORT GRAPHICS ENGINE CONVERTERS ---
@login_required(login_url='/login/')
def save_export(request, template_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('image_data')
        
        request.session['export_image'] = image_data
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required(login_url='/login/')
def download_png(request, template_id):
    image_data = request.session.get('export_image')
    if not image_data:
        return HttpResponse("No image data found", status=404)

    format, imgstr = image_data.split(';base64,')
    img_bytes = base64.b64decode(imgstr)

    response = HttpResponse(img_bytes, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="Resume.png"'
    return response

@login_required(login_url='/login/')
def download_pdf(request, template_id):
    image_data = request.session.get('export_image')
    if not image_data:
        return HttpResponse("No image data found", status=404)

    format, imgstr = image_data.split(';base64,')
    img_bytes = base64.b64decode(imgstr)

    image = Image.open(BytesIO(img_bytes))
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    pdf_bytes = BytesIO()
    image.save(pdf_bytes, format='PDF', resolution=100.0)

    response = HttpResponse(pdf_bytes.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Resume.pdf"'
    return response

# --- ENGINE AI HANDLERS ---
@login_required(login_url='/login/')
def enhance_bullet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            raw_text = data.get('text', '')

            prompt = f"""
            Act as an expert resume writer. Rewrite the following job duty to be highly professional, impactful, and action-oriented.
            
            CRITICAL RULES:
            1. Provide EXACTLY ONE polished sentence.
            2. Do NOT provide multiple options.
            3. Do NOT include any introductory text, greetings, or conversational filler.
            4. Do NOT include explanations of why it is effective.
            5. Do NOT start the sentence with a bullet point symbol (* or -).
            
            Return ONLY the final rewritten text.
            
            Original Text: {raw_text}
            """

            model = legacy_genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return JsonResponse({'status': 'success', 'enhanced_text': response.text.strip()})
            
        except Exception as e:
            print(f"\n🚨 GOOGLE AI ERROR: {str(e)}\n") 
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required(login_url='/login/')
def ats_scanner(request):
    if request.method == 'POST':
        try:
            job_description = request.POST.get('job_description', '')
            uploaded_file = request.FILES.get('resume_pdf')

            if not job_description or not uploaded_file:
                return JsonResponse({'status': 'error', 'message': 'Missing job description or PDF file.'}, status=400)

            resume_text = ""
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                resume_text += page.extract_text() + "\n"

            prompt = f"""
            Act as an Applicant Tracking System (ATS) software. 
            Compare the user's Resume against the Job Description.
            
            CRITICAL RULES:
            1. Return ONLY a valid JSON object. Do not include markdown tags like ```json.
            2. The JSON must have exactly two keys: "score" (an integer from 0 to 100) and "missing_keywords" (a list of up to 5 short string keywords).
            
            Example output format:
            {{"score": 75, "missing_keywords": ["Docker", "Agile", "AWS"]}}        
            Resume: {resume_text}            
            Job Description: {job_description}
            """
            model = legacy_genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            raw_output = response.text.strip().replace('```json', '').replace('```', '')
            ats_data = json.loads(raw_output)
            return JsonResponse({'status': 'success', 'data': ats_data})
            
        except Exception as e:
            error_message = str(e)
            print(f"\n🚨 ATS ERROR: {error_message}\n") 
            if "429" in error_message or "Quota" in error_message:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Whoa there! Our AI is thinking too fast. Please wait 60 seconds and try again.'
                }, status=429)
            return JsonResponse({'status': 'error', 'message': error_message}, status=500) 
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required(login_url='/login/')
def ats_scanner_page(request):
    return render(request, 'ats_match.html')

def live_builder(request):
    return render(request, 'live_builder.html')

@login_required(login_url='/login/')
def resume_finalize(request, template_id):
    selected_template = get_object_or_404(ResumeTemplate, id=template_id)
    return render(request, 'resume_finalize.html', {'template': selected_template})

@login_required
def select_cover_letter_template(request):
    """
    Fetches all available cover letter templates from the database
    and renders them in the selection grid gallery.
    """
    cl_templates = CoverLetterTemplate.objects.all()
    return render(request, 'select_cover_letter_template.html', {
        'cl_templates': cl_templates
    })

@login_required
def cover_letter_builder(request, template_id):
    """
    Renders the split-screen workspace studio for the selected template.
    Passes the template metadata to display IDs and layout specifics.
    """
    template = get_object_or_404(CoverLetterTemplate, id=template_id)
    return render(request, 'cover_letter_builder.html', {
        'template': template
    })

def cl_preview_blank(request, template_id):
    """
    Renders the raw, unpopulated HTML layout profile of the cover letter.
    This runs inside the iframe and contains empty spans with specific IDs 
    (like id='view-sender_name') that the JavaScript targets in real-time.
    """
    template = get_object_or_404(CoverLetterTemplate, id=template_id)
    template_file = template.file_path 
    
    return render(request, template_file, {
        'template': template
    })

@login_required
def save_cover_letter(request, template_id):
    """
    Handles form collection, commits inputs to the database records, 
    and transfers the user cleanly to the final export layout stage.
    """
    if request.method == "POST":
        template = get_object_or_404(CoverLetterTemplate, id=template_id)
        
        # Collect form strings directly from request.POST
        sender_name = request.POST.get('sender_name', '').strip()
        sender_email = request.POST.get('sender_email', '').strip()
        sender_phone = request.POST.get('sender_phone', '').strip()
        sender_location = request.POST.get('sender_location', '').strip()
        recipient_name = request.POST.get('recipient_name', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        job_title = request.POST.get('job_title', '').strip()
        letter_body = request.POST.get('letter_body', '').strip()
        signature_data = request.POST.get('signature_data', '').strip()

        letter = SavedCoverLetter.objects.create(
            user=request.user,
            template=template,
            sender_name=sender_name,
            sender_email=sender_email,
            sender_phone=sender_phone,
            sender_location=sender_location,
            recipient_name=recipient_name,
            company_name=company_name,
            job_title=job_title,
            letter_body=letter_body,
            signature_data=signature_data
        )

        return redirect('export_cover_letter', letter_id=letter.id)
    return redirect('cover_letter_builder', template_id=template_id)

@csrf_exempt
def ai_enhance_text(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_text = data.get("text", "").strip()

            if not user_text:
                return JsonResponse({"success": False, "error": "No text provided"})

            # 🎯 PASS THE KEY DIRECTLY INSIDE THE CLIENT INITIALIZATION:
            client = genai.Client(api_key="AIzaSyA2JJqaqY2lPmTc2WKvURh5Nu08gwY3Ynw")
            
            prompt = (
                f"You are an expert career counselor. Rewrite and polish the following rough draft "
                f"into a highly professional, compelling, and beautifully structured cover letter body paragraph. "
                f"Keep it realistic, engaging, and remove any grammatical errors. Return ONLY the polished body text "
                f"without any placeholders, salutations, or greetings.\n\nRough text:\n{user_text}"
            )

            # Call the model
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )

            return JsonResponse({
                "success": True, 
                "enhanced_text": response.text.strip()
            })

        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)})
            
    return JsonResponse({"success": False, "error": "Invalid request method"})

def export_cover_letter(request, letter_id):
    saved_letter = get_object_or_404(SavedCoverLetter, id=letter_id)
    return render(request, 'cover_letter_export.html', {
        'letter': saved_letter,
        'template': saved_letter.template
    })