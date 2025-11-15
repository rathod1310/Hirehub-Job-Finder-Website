from django.urls import path
from . import views


urlpatterns = [

#######################APPLICANT############################
	path("", views.home, name="home"),
	path("show_applied_job", views.show_applied_job, name="show_applied_job"),
	path("show_job", views.show_job, name="show_job"),
	path("company_applied_applicant", views.company_applied_applicant, name="company_applied_applicant"),
	path("login", views.login, name="login"),
	path("registration", views.registration, name="registration"),
	path("company_show_all_jobs", views.company_show_all_jobs, name="company_show_all_jobs"),
	path("post_job", views.post_job, name="post_job"),
    path('search_jobs/', views.search_jobs, name='search_jobs'),

#######################COMPANY############################
	path('logout/',views.logout,name='logout'),
	path('apply_job/<int:pk>/', views.apply_job, name='apply_job'),

	path("company_home", views.company_home, name="company_home"),
    path("update-status/<int:pk>/", views.update_status, name="update_status"),



	]