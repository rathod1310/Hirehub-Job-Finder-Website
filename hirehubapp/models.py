from django.db import models
from django.utils import timezone    

class User(models.Model):
    USER_TYPE_CHOICES = [
    ('company', 'Company'),
    ('applicant', 'Applicant'),
    ]
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=100)
    email=models.EmailField()
    mobile=models.PositiveIntegerField()
    address=models.TextField()
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=50)
    zipcode=models.PositiveIntegerField()
    password=models.CharField(max_length=100)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
    	return self.fname+" "+self.lname

class PostJob(models.Model):
    job_id = models.CharField(max_length=20,null=False)
    company_name = models.CharField(max_length=100, null=False)
    title = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    description = models.TextField(max_length=100)
    salary = models.IntegerField(null=False) 
    jobtype = models.CharField(max_length=20)
    posted_at = models.DateTimeField(default=timezone.now) 
    skills = models.CharField(max_length=100)    
    experience = models.IntegerField(default=0) 
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.job_id} - {self.company_name} - {self.title}"

    @staticmethod
    def get_next_job_id():
        last_job = PostJob.objects.order_by('-id').first()
        if last_job:
            last_number = int(last_job.job_id.split('-')[1]) 
            next_number = last_number + 1
        else:
            next_number = 1  
        
        return f"JOB-{str(next_number).zfill(3)}"

class Apply_Job(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
    ]

    job_id = models.CharField(max_length=20, null=True, default=None)
    company_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Applied')
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)


    def __str__(self):
        return f"{self.job_id} - {self.name} - {self.company_name} - {self.title}"



