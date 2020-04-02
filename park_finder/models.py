from django.db import models
from django.contrib import messages
import re
import bcrypt
from datetime import datetime

# Create your models here.
class UserManager(models.Manager):
    def registration_validator(self, post_data):
        print("*****post_data: ", post_data)
        errors = {}
        #is email already in db?  --> yes = add message to errors, return errors
        potential_new_user = User.objects.filter(email = post_data['email'])
        if len(potential_new_user)>0:
            errors['not_new'] = "Email already registered"
            return errors
        #regex for email, len(first_name, last_name, password, pw==pw_confirm)
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Invalid email address!"
        if len(post_data['first_name'])<2:
            errors['first_name'] = "first name too short"
        if len(post_data['last_name'])<2:
            errors['last_name'] = "last name too short"
        if len(post_data['password'])<8:
            errors['password'] = "password too short"
        if post_data['password'] != post_data['pw_confirm']:
            errors['pw_match'] = "passwords do not match"
        # if post_data['dob'] > datetime.now().strftime("%Y-%m-%d"):
        #     errors['dob'] = "invalid birthdate"
        # #check if user is at least 13 yrs old     
        # if int(datetime.now().strftime("%Y%m%d")) - int(re.sub('-', '', post_data['dob'])) <=130000:
        #     errors['dob'] = "sorry, you're too young!" 
        return errors

    def login_validator(self, post_data):
        errors = {}
        #is email in db?  --> no = add message to errors, return erros
        login_attempt = User.objects.filter(email = post_data['email'])
        if len(login_attempt)==0:
            errors['existing_email'] = "This email has not been registered"
            return errors
        #does pw match
        if not bcrypt.checkpw(post_data['password'].encode(), User.objects.filter(email = post_data['email'])[0].password.encode()):
            errors['password'] = "That password doesn't work."
        return errors
class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # dob = models.DateTimeField()
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    current_hiking_group = models.CharField(null=True, max_length=255, default = None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class ParkManager(models.Manager):
    def park_validator(self, post_data):
        errors = {}
        #! add in validation requirements
        return errors
class Park(models.Model):
    # Park.objects.create(name="test park", website_url = "http://www.ocparks.com/parks/lagunac", trail_map_url="http://www.ocparks.com/civicax/filebank/blobdload.aspx?BlobID=57857", allows_pets=False, limited_access=False, busy="moderate", has_shade=False, has_water=True, has_bathrooms=True, is_accessible=False, is_kid_friendly=True, permitted_activities="Running, Hiking, Mountain Biking, Horseback Riding", natural_features="ephemeral streams", has_playground=False)
    name = models.CharField(max_length=255)
    website_url = models.URLField(default = None)
    trail_map_url = models.URLField(default = None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    latitude = models.CharField(max_length=255)
    longitue = models.CharField(max_length=255)
    #all filter features:
    allows_pets = models.BooleanField()
    limited_access = models.BooleanField()
    busy = models.CharField(max_length=255) #not busy, moderately busy, very busy
    has_shade = models.BooleanField()
    has_water = models.BooleanField()
    has_bathrooms = models.BooleanField()
    is_accessible = models.BooleanField()
    is_kid_friendly = models.BooleanField()
    permitted_activities = models.CharField(max_length=255)
    natural_features = models.CharField(max_length=255)
    has_playground = models.BooleanField()
    #?maybe have a Trail class that is the child of the Park class??
    # length = models.FloatField()
    # difficulty = models.CharField(max_length=255)

class VisitManager(models.Manager):
    def visit_validator(self, post_data):
        errors = {}
        #! add in validation requirements
        return errors
class Visit(models.Model):
    has_visited = models.BooleanField(default = False)
    date_visited = models.DateTimeField(null=True, default = None)
    public_notes = models.TextField(null=True, default = None)
    private_notes = models.TextField(null=True, default = None)
    hiking_group_at_visit_time = models.CharField(null=True, max_length=255, default = None)
    rating = models.IntegerField(null=True, default = None)
    #? visit_pics = models.????
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = VisitManager()
    user = models.ForeignKey(User, related_name = "visits", on_delete=models.CASCADE)
    park = models.ForeignKey(Park, related_name = "parks", on_delete=models.CASCADE)
    #!image uploads

    # add date format function
    def formatted_date(self):
        if self.date_visited is not None:
            return self.date_visited.strftime("%B %d, %Y")
    def hg_formatted(self):
        if self.hiking_group_at_visit_time is not None:
            return self.hiking_group_at_visit_time.replace("'","")[1:-1].replace(",","").split()
