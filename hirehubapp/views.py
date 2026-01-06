from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
import csv
import pandas as pd
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.cache import never_cache


def get_common_data(request):
    common_data = {}

    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])

    return common_data


def home(request):
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

def update_status(request, pk):
    apply_job = Apply_Job.objects.get(pk=pk)

    if request.method == "POST":
        new_status = request.POST.get("status")
        apply_job.status = new_status
        apply_job.save()

    return redirect("company_applied_applicant")


def registration(request):
    if request.method=="POST":
        try:
            User.objects.get(email=request.POST['email'])
            msg="Email Already Registered"
            return render(request,'registration.html',{'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
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
            Apply_Job.objects.create(
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
            msg = "Job Applied Successfully"
            return redirect('show_applied_job')
        else:
            context = get_common_data(request)
            context.update({'user': user, 'jobs': jobs})
            return render(request, 'apply_job.html', context)
    else:
        return redirect('login')



def company_home(request):
    context = get_common_data(request)
    return render(request, "company/company-index.html",context)


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