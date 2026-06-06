from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
import csv
import pandas as pd
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count


def send_simple_mail(subject, message, recipients):
    recipients = [email for email in recipients if email]
    if recipients:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=True,
        )


def get_company_email(company_name):
    companies = User.objects.filter(user_type='company')
    for company in companies:
        full_name = f"{company.fname} {company.lname}".strip().lower()
        if full_name == company_name.strip().lower():
            return company.email
    return None


def get_common_data(request):
    common_data = {}

    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])

    return common_data


def home(request):
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        if user.user_type == "company":
            return redirect('company_home')

    context = get_common_data(request)
    return render(request, "index.html",context)

def show_applied_job(request):
    user = None
    if 'email' in request.session:
        user=User.objects.get(email=request.session['email'])
    apply_jobs = Apply_Job.objects.filter(email=user.email)
    return render(request, "show_applied_job.html",{'apply_jobs':apply_jobs})

def show_job(request):
    jobs = PostJob.objects.all()
    apply_jobs = Apply_Job.objects.all()
    total_jobs = jobs.count()
    applied_job_ids = []
    if 'email' in request.session:
        applied_job_ids = Apply_Job.objects.filter(email=request.session['email']).values_list('job_id', flat=True)
    return render(request, "show_job.html",{'jobs':jobs, 'applied_job_ids': applied_job_ids,'total_jobs': total_jobs,'apply_jobs':apply_jobs})

def company_applied_applicant(request):
    user = None
    if 'email' in request.session:
        user=User.objects.get(email=request.session['email'])
    apply_jobs = Apply_Job.objects.filter(company_name=user)
    return render(request, "company/company_applied_applicant.html",{'apply_jobs':apply_jobs})

def applicant_detail(request, pk):
    if 'email' not in request.session:
        return redirect('login')

    user = User.objects.get(email=request.session['email'])
    if user.user_type != "company":
        return redirect('home')

    apply_job = get_object_or_404(Apply_Job, pk=pk, company_name=str(user))
    return render(request, "company/applicant_detail.html", {'apply_job': apply_job})

def update_status(request, pk):
    apply_job = Apply_Job.objects.get(pk=pk)

    if request.method == "POST":
        new_status = request.POST.get("status")
        apply_job.status = new_status
        apply_job.save()
        send_simple_mail(
            f"Application Status Updated - {apply_job.title}",
            f"Hello {apply_job.name},\n\n"
            "Your job application status has been updated by the company.\n\n"
            "Application Details:\n"
            f"Job Title: {apply_job.title}\n"
            f"Company: {apply_job.company_name}\n"
            f"Job ID: {apply_job.job_id}\n"
            f"Current Status: {apply_job.status}\n\n"
            "You can log in to HireHub to view your application details.\n\n"
            "Regards,\n"
            "HireHub Team",
            [apply_job.email],
        )

    return redirect("company_applied_applicant")


def registration(request):
    if request.method=="POST":
        try:
            User.objects.get(email=request.POST['email'])
            msg="Email Already Registered"
            return render(request,'registration.html',{'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                user = User.objects.create(
                        user_type = request.POST.get('userType'),
                        fname=request.POST['fname'],
                        lname=request.POST['lname'],
                        email=request.POST['email'],
                        mobile=request.POST['mobile'],
                        address=request.POST['address'],
                        city=request.POST['city'],
                        state=request.POST['state'],
                        zipcode=request.POST['zipcode'],
                        password=request.POST['password'],
                    )
                send_simple_mail(
                    "Welcome to HireHub - Registration Successful",
                    f"Hello {user.fname},\n\n"
                    "Your HireHub account has been created successfully.\n\n"
                    "Account Details:\n"
                    f"Name: {user.fname} {user.lname}\n"
                    f"Email: {user.email}\n"
                    f"Account Type: {user.user_type.title()}\n"
                    f"City: {user.city}\n\n"
                    "You can now log in and start using HireHub.\n\n"
                    "Regards,\n"
                    "HireHub Team",
                    [user.email],
                )
                msg="User Sign Up Successfully"
                return render(request,'login.html',{'msg':msg})
            else:
                msg="Password & Confirm Password Does Not Matched"
                return render(request,'registration.html',{'msg':msg})
    else:
        return render(request, "registration.html")

def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            if user.password == request.POST['password']:
                request.session['email'] = user.email
                request.session['fname'] = user.fname
                                
                if user.user_type == "company":
                    return redirect('company_home')
                else:
                    return redirect('home') 
            else:
                msg="Incorrect Password"
                return render(request, 'login.html',{'msg':msg})
        except User.DoesNotExist:
            msg="Email Not Registered"
            return render(request, 'login.html',{'msg':msg})
    else:
        return render(request, 'login.html')

def company_show_all_jobs(request):
    user = None
    if 'email' in request.session:
        user=User.objects.get(email=request.session['email'])
    jobs=PostJob.objects.filter(company_name=user)
    return render(request, "company/company_show_all_jobs.html", {'jobs': jobs})


def post_job(request):
    users = User.objects.get(email=request.session['email'])
    msg = ""
    job_id = None

    if request.method == "POST":

        # =========================
        # ✅ BULK UPLOAD (CSV/Excel)
        # =========================
        if 'bulk_apply' in request.FILES:
            file = request.FILES['bulk_apply']

            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    messages.error(request, "Only CSV or Excel files are allowed.")
                    return redirect('post_job')

                for _, row in df.iterrows():
                    PostJob.objects.create(
                        job_id=PostJob.get_next_job_id(),
                        company_name=row['company_name'],
                        title=row['title'],
                        city=row['city'],
                        description=row['description'],
                        salary=row['salary'],
                        jobtype=row['jobtype'],
                        posted_at=timezone.now(),
                        skills=row['skills'],
                        experience=row['experience'],
                    )

                messages.success(request, "Bulk jobs uploaded successfully.")
                return redirect('company_show_all_jobs')

            except KeyError as e:
                messages.error(request, f"Missing column in CSV: {e}")
            except Exception as e:
                messages.error(request, str(e))

            return redirect('post_job')

        # =========================
        # ✅ MANUAL JOB POST
        # =========================
        else:
            job_id = PostJob.get_next_job_id()
            PostJob.objects.create(
                job_id=job_id,
                company_name=request.POST.get('company_name'),
                title=request.POST.get('title'),
                city=request.POST.get('city'),
                description=request.POST.get('description'),
                salary=request.POST.get('salary'),
                jobtype=request.POST.get('jobtype'),
                posted_at=request.POST.get('posted_at') or timezone.now(),
                skills=request.POST.get('skills'),
                experience=request.POST.get('experience'),
            )

            msg = "Job Posted Successfully"
            return redirect('company_show_all_jobs')

    return render(request, "company/post_job.html", {
        'msg': msg,
        'job_id': job_id,
        'users': users
    })
    users = User.objects.get(email=request.session['email'])
    msg = ""
    job_id = None
    if request.method=="POST":
        job_id = PostJob.get_next_job_id()
        PostJob.objects.create(
                job_id=job_id,
                company_name = request.POST['company_name'],
                title = request.POST['title'],
                city = request.POST['city'],
                description = request.POST['description'],
                salary = request.POST['salary'],
                jobtype = request.POST['jobtype'],
                posted_at = request.POST['posted_at'] or timezone.now(),
                skills = request.POST['skills'],
                experience = request.POST['experience'],
                category = request.POST['category']
                )
        msg="Job Posted Successfully"
        return redirect('company_show_all_jobs')
    return render(request, "company/post_job.html",{'msg':msg,'job_id': job_id,'users':users})

def logout(request):
    try:
        del request.session['email']
        del request.session['fname']
        return render(request,'index.html')
    except:
        return render(request,'index.html')

def apply_job(request,pk):
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        jobs = PostJob.objects.get(pk=pk)

        if request.method == 'POST':
            applied_job = Apply_Job.objects.create(
                job_id=request.POST['job_id'],
                company_name=request.POST['company_name'],
                title=request.POST['title'],
                name=request.POST['name'],
                email=request.POST['email'],
                mobile=request.POST['mobile'],
                address=request.POST['address'],
                city=request.POST['city'],
                pincode=request.POST['pincode'],
                resume=request.FILES.get('resume'),
            )
            company_email = get_company_email(applied_job.company_name)
            send_simple_mail(
                f"Application Submitted - {applied_job.title}",
                f"Hello {applied_job.name},\n\n"
                "Your job application has been submitted successfully.\n\n"
                "Application Details:\n"
                f"Job Title: {applied_job.title}\n"
                f"Company: {applied_job.company_name}\n"
                f"Job ID: {applied_job.job_id}\n"
                f"Status: {applied_job.status}\n\n"
                "The company can now review your profile and CV. You will receive another email when your application status changes.\n\n"
                "Regards,\n"
                "HireHub Team",
                [applied_job.email],
            )
            send_simple_mail(
                f"New Job Application Received - {applied_job.title}",
                f"Hello,\n\n"
                "A new applicant has applied for one of your posted jobs on HireHub.\n\n"
                "Job Details:\n"
                f"Job Title: {applied_job.title}\n"
                f"Job ID: {applied_job.job_id}\n"
                f"Company: {applied_job.company_name}\n\n"
                "Applicant Details:\n"
                f"Name: {applied_job.name}\n"
                f"Email: {applied_job.email}\n"
                f"Mobile: {applied_job.mobile}\n"
                f"City: {applied_job.city}\n"
                f"Pincode: {applied_job.pincode}\n\n"
                "Please log in to your HireHub company account to view the full applicant details and CV.\n\n"
                "Regards,\n"
                "HireHub Team",
                [company_email],
            )
            msg = "Job Applied Successfully"
            return redirect('show_applied_job')
        else:
            context = get_common_data(request)
            context.update({'user': user, 'jobs': jobs})
            return render(request, 'apply_job.html', context)
    else:
        return redirect('login')



def get_company_home_context(request):
    if 'email' not in request.session:
        return None

    user = User.objects.get(email=request.session['email'])
    company_name = f"{user.fname} {user.lname}"
    jobs = PostJob.objects.filter(company_name=company_name)
    applications = Apply_Job.objects.filter(company_name=company_name)

    status_counts = {
        item['status']: item['total']
        for item in applications.values('status').annotate(total=Count('id'))
    }
    status_data = []
    for status, label in Apply_Job.STATUS_CHOICES:
        status_data.append({
            'label': label,
            'count': status_counts.get(status, 0),
        })

    max_status_count = max([item['count'] for item in status_data] + [1])
    for item in status_data:
        item['percent'] = int((item['count'] / max_status_count) * 100)

    top_jobs = []
    for job in jobs:
        count = applications.filter(job_id=job.job_id).count()
        top_jobs.append({
            'title': job.title,
            'job_id': job.job_id,
            'count': count,
        })
    top_jobs = sorted(top_jobs, key=lambda item: item['count'], reverse=True)[:5]
    max_job_count = max([item['count'] for item in top_jobs] + [1])
    for item in top_jobs:
        item['percent'] = int((item['count'] / max_job_count) * 100)

    context = get_common_data(request)
    context.update({
        'company_name': company_name,
        'total_jobs': jobs.count(),
        'total_applications': applications.count(),
        'applied_count': applications.filter(status='Applied').count(),
        'under_review_count': applications.filter(status='Under Review').count(),
        'shortlisted_count': applications.filter(status='Shortlisted').count(),
        'rejected_count': applications.filter(status='Rejected').count(),
        'status_data': status_data,
        'top_jobs': top_jobs,
        'recent_applications': applications.order_by('-id')[:5],
    })
    return context


def company_home(request):
    context = get_company_home_context(request)
    if context is None:
        return redirect('login')
    return render(request, "company/company-index.html", context)


def search_jobs(request):
    query = request.GET.get('q', '').strip()  # Get search text, default empty string
    msg = ""
    jobs = PostJob.objects.none()  # default empty queryset

    if query:
        # Search by title (case-insensitive)
        jobs = PostJob.objects.filter(title__icontains=query)
        if not jobs.exists():
            msg = "Oops, no results found!"
    else:
        msg = "Please enter a keyword to search."

    return render(request, "show_job.html", {'jobs': jobs,'query': query,'msg': msg})


def edit_profile(request):
    if 'email' not in request.session:
        return redirect('login')

    users = User.objects.get(email=request.session['email'])

    if request.method == 'POST':
        users.fname = request.POST['fname']
        users.lname = request.POST['lname']
        users.email = request.POST['email']
        users.mobile = request.POST['mobile']
        users.address = request.POST['address']
        users.city = request.POST['city']
        users.state = request.POST['state']
        users.zipcode = request.POST['zipcode']
        users.save()
        messages.success(request, "Profile updated successfully ✅")
        return redirect('edit_profile')


    context = get_common_data(request)
    context.update({'users': users})
    return render(request, 'edit_profile.html', context)




def export_applied_jobs_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="applied_jobs.csv"'

    writer = csv.writer(response)

    # CSV Header
    writer.writerow([
        'Candidate Name',
        'Job Title',
        'Company Name',
        'Status'
    ])

    jobs = Apply_Job.objects.all()

    for job in jobs:
        writer.writerow([
            job.name,
            job.title,
            job.company_name,
            job.status
        ])

    return response

def edit_job(request, pk):
    if 'email' not in request.session:
        return redirect('login')

    user = User.objects.get(email=request.session['email'])
    job = get_object_or_404(PostJob, pk=pk)

    if request.method == 'POST':
        job.title = request.POST['title']
        job.city = request.POST['city']
        job.description = request.POST['description']
        job.salary = request.POST['salary']
        job.jobtype = request.POST['jobtype']
        job.skills = request.POST['skills']
        job.experience = request.POST['experience']
        job.category = request.POST['category']
        job.save()
        
        return redirect('company_show_all_jobs')

    context = get_common_data(request)
    context.update({
        'user': user,
        'job': job
    })
    return render(request, 'company/edit_job.html', context)

def delete_job(request, pk):
    if 'email' not in request.session:
        return redirect('login')

    user = User.objects.get(email=request.session['email'])
    job = get_object_or_404(PostJob, pk=pk)

    # Build the full company name from the logged-in user
    user_company_name = f"{user.fname} {user.lname}"

    # Safety check (case-insensitive, ignores extra spaces)
    if job.company_name.strip().lower() != user_company_name.strip().lower():
        return redirect('company_show_all_jobs')

    job.delete()
    return redirect('company_show_all_jobs')
