"""
URL configuration for django_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rfp_llm import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('get/', views.get),
    path('add_company_profile/', views.add_company_profile),
    path('del_company_profile/', views.del_company_profile),
    path('add_project/', views.add_project),
    path('del_project/', views.del_project),
    path('add_project_file/', views.add_project_file),
    path('del_project_file/', views.del_project_file),
    path('get_question/', views.get_question),
    path('get_simple_answer/', views.get_simple_answer),
    path('get_simple_answer_verbose/', views.get_simple_answer_verbose),
    path('get_detailed_answer/', views.get_detailed_answer),
    path('get_detailed_answer_verbose/', views.get_detailed_answer_verbose),
    path('sign_up/', views.sign_up),
    path('log_in/', views.log_in),
]
