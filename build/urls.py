from django.contrib import admin
from django.urls import path
from app import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('builder/<int:template_id>/finalize/', views.resume_finalize, name='resume_finalize'),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('nav/', views.nav, name='nav'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('templates/', views.select_template, name='select_template'),
    path('builder/<int:template_id>/', views.resume_builder, name='resume_builder'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="password_reset"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name="password_reset_complete"),
    path('builder/<int:template_id>/experience/', views.add_experience, name='add_experience'),
    path('builder/<int:template_id>/experience/delete/<int:job_id>/', views.delete_experience, name='delete_experience'),
    path('builder/<int:template_id>/education/', views.add_education, name='add_education'),
    path('builder/<int:template_id>/education/delete/<int:edu_id>/', views.delete_education, name='delete_education'),
    path('builder/<int:template_id>/skills/', views.add_skill, name='add_skill'),
    path('builder/<int:template_id>/skills/delete/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('builder/<int:template_id>/preview/', views.resume_preview, name='resume_preview'),
    path('builder/<int:template_id>/details/', views.add_details, name='add_details'),
    path('builder/<int:template_id>/details/delete/<int:detail_id>/', views.delete_detail, name='delete_detail'),
    path('live-builder/', views.live_builder, name='live_builder'),
    path('builder/<int:template_id>/save_export/', views.save_export, name='save_export'),
    path('builder/<int:template_id>/download_png/', views.download_png, name='download_png'),
    path('builder/<int:template_id>/download_pdf/', views.download_pdf, name='download_pdf'),
    path('api/ats-scanner/', views.ats_scanner, name='ats_scanner'),
    path('ats-scanner/', views.ats_scanner_page, name='ats_scanner_page'),
    path('api/enhance-bullet/', views.enhance_bullet, name='enhance_bullet'),
    path('cover-letter/templates/', views.select_cover_letter_template, name='select_cover_letter_template'),
    path('cover-letter/builder/<int:template_id>/', views.cover_letter_builder, name='cover_letter_builder'),
    path('cover-letter/preview/<int:template_id>/', views.cl_preview_blank, name='cl_preview_blank'),
    path('cover-letter/save/<int:template_id>/', views.save_cover_letter, name='save_cover_letter'),
    path('ai/enhance-text/', views.ai_enhance_text, name='ai_enhance_text'),
    path('cover-letter/export/<int:letter_id>/', views.export_cover_letter, name='export_cover_letter'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
