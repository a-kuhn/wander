from django.shortcuts import render, redirect
from django.contrib import messages
import re
import bcrypt
from .models import *

# Create your views here.
# ?? RENDER FUNCTIONS
def index(request):
    return render(request,'index.html')

def dashboard(request):
    user = User.objects.get(email = request.session['email'])
    context = {
        "user": user,
        "places_to_visit": Visit.objects.filter(user_id = user.id).filter(has_visited=False),
        "visited_places": Visit.objects.filter(user_id = user.id).filter(has_visited=True),
    }
    print("dashboard context: ", context)
    return render(request, 'dashboard.html', context)

def park_search(request):
    #renders park search page
    context = {
        "parks": Park.objects.all(),
    }
    return render(request, 'park_search.html', context)

def add_park(request):
    #renders add a park page
    return render(request, 'add_park.html')

def search_results(request):
    
    #renders search results page with info from search_db
    data = request.POST.copy()
    formatted_activities = data.getlist('permitted_activities')
    formatted_features = data.getlist('natural_features')

    parks = Park.objects.all()
    if request.POST['allows_pets'] == 'True':
        parks = parks.filter(allows_pets = True)
    if request.POST['limited_access'] == '':
        parks = parks.filter(limited_access = True)
    if request.POST['busy'] == 'True':
        parks = parks.filter(busy = True)
    if request.POST['has_shade'] == 'True':
        parks = parks.filter(has_shade = True)
    if request.POST['has_water'] == 'True':
        parks = parks.filter(has_water = True)
    if request.POST['has_bathrooms'] == 'True':
        parks = parks.filter(has_bathrooms = True)
    if request.POST['is_accessible'] == 'True':
        parks = parks.filter(is_accessible = True)
    if request.POST['is_kid_friendly'] == 'True':
        parks = parks.filter(is_kid_friendly = True)
    if request.POST['has_playground'] == 'True':
        parks = parks.filter(has_playground = True)

    activities_features_list = []
    for park in parks:
        possible_features = [item.strip() for item in park.natural_features.replace("'","").split(',')]
        possible_activities = [item.strip() for item in park.permitted_activities.replace("'","").split(',')]
        park_dict = {
            'a_match': [i for i in formatted_activities if i in possible_activities],
            'a_no_match': [i for i in formatted_activities if i not in possible_activities],
            'f_match': [i for i in formatted_features if i in possible_features],
            'f_no_match': [i for i in formatted_features if i not in possible_features],
        }
        activities_features_list.append((park, park_dict))
        print("\n\n\n","*^"*60, "\np_a: ", possible_activities, "\nf_a: ", formatted_activities, "\np_f: ", possible_features, "\nf_f: ", formatted_features, "\n\nactivities features list: ", activities_features_list)



    message = "Here's a list of parks that meet your needs:"
    if len(parks)<1:
        message = "Sorry, we couldn't find any parks that meet your needs. Try searching with fewer filters."
    
    context = {
        "message": message,
        "activities_features_list": activities_features_list,
    }
    return render(request, 'search_results.html', context)

def user_profile(request, user_id):
    #renders user's profile
    user = User.objects.get(id = user_id)
    visits = Visit.objects.filter(user_id = user_id).filter(has_visited=True).order_by("-date_visited")
    context = {
        "user": user,
        "visits": visits,
    }
    return render(request, 'user_profile.html', context)

def memory_log(request, visit_id):
    #renders user's memory log for specific visit
    user_visit = Visit.objects.get(id = visit_id)
    hiking_group = user_visit.hg_formatted
    # hiking_group_at_visit_time.replace("'","")[1:-1].replace(",","").split()
    context = {
        "user_visit": user_visit,
        "hiking_group": hiking_group,
    }
    print("CONTEXT: ", context)
    return render(request, 'memory_log.html', context)

def add_trail_report(request, park_id):
    print("loading trail report page for park_id: ", park_id)
    #render's trail report template
    user = User.objects.get(email=request.session['email'])
    park = Park.objects.get(id=park_id)
    context = {
        "user": user,
        "park": park,
    }
    return render(request, 'add_trail_report.html', context)

def park_profile(request, park_id):
    #renders park profile page
    user = User.objects.get(email = request.session['email'])
    park = Park.objects.get(id=park_id)
    visits = Visit.objects.filter(park_id=park_id).exclude(date_visited = None).order_by("-created_at")
    visit_check_list = Visit.objects.filter(user_id = user.id).filter(park_id=park_id)
    visits_count = len(visits)
    activities = park.permitted_activities[1:-1].replace("'",'').split(',')
    natural_features = park.natural_features[1:-1].replace("'",'').split(',')
    memory_log_id = None
    def visit_check(visits, user_id): 
        for visit in visits: 
            if visit.user_id == user_id and visit.has_visited==False:
                return "remove_from_list"
            elif visit.user_id==user_id and visit.has_visited==True:
                memory_log_id = visit.id
                return "memory_log", memory_log_id
        return "add_to_list"
    context = {
        "user": user,
        "park" : park,
        "visits" : visits,
        "visits_count": visits_count,
        "activities": activities,
        "natural_features": natural_features,
        "list_action": visit_check(visit_check_list, user.id),
        "memory_log_id": memory_log_id,
    }
    print("Context: ", context)
    print("LIST ACTION== ", context['list_action'])
    return render(request, 'park_profile.html', context)


# ? REDIRECT FUNCTIONS
def register(request):
    #validate potential new user
    errors = User.objects.registration_validator(request.POST)
    #fail = redirect to index with messages
    if len(errors)>0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    #succeed = create user, add user to session **hash password**, redirect to success
    User.objects.create(
        first_name = request.POST['first_name'],
        last_name = request.POST['last_name'],
        # dob = request.POST['dob'],
        email = request.POST['email'],
        password = bcrypt.hashpw((request.POST['password']).encode(), bcrypt.gensalt()).decode(),
    )
    request.session['email'] = request.POST['email']
    print("creating new user...")
    return redirect('/dashboard')

def login(request):
    #validate login info: if email in db, if pw matches
    errors = User.objects.login_validator(request.POST)
    #fail = redirect to index with messages
    if len(errors)>0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    #succeed = redirect to user's wall 
    request.session['email'] = request.POST['email']
    print("logging in user...")
    return redirect('/dashboard')

def logout(request):
    #clear session 
    request.session.clear()
    #redirect to index
    return redirect('/')

def search_db(request):
    #uses park_search filters to search db for matching parks
    print("db search post request: ", request.POST)
    return redirect('/search_results')

def create_park(request):
    print("*"*30, "\npost request: ",request.POST)
    #uses add_park info to create new park in db
    data = request.POST.copy()
    formatted_activities = str(data.getlist('permitted_activities'))
    formatted_features = str(data.getlist('natural_features'))
    print("*"*30, "\nactivities: ",type(formatted_activities),"\nfeatures: ",type(formatted_features),)
    Park.objects.create(
        name = request.POST['park_name'],
        website_url = request.POST['website_url'],
        trail_map_url = request.POST['trail_map_url'],
        allows_pets = request.POST['allows_pets'],
        limited_access = request.POST['limited_access'],
        busy = request.POST['busy'],
        has_shade = request.POST['has_shade'],
        has_water = request.POST['has_water'],
        has_bathrooms = request.POST['has_bathrooms'],
        is_accessible = request.POST['is_accessible'],
        is_kid_friendly = request.POST['is_kid_friendly'],
        permitted_activities = formatted_activities,
        natural_features = formatted_features,
        has_playground = request.POST['has_playground'],
        longitue = request.POST['longitue'],
        latitude = request.POST['latitude'],
    )
    Visit.objects.create(
        has_visited = True,
        date_visited = request.POST['date_visited'],
        public_notes = request.POST['public_notes'],
        private_notes = request.POST['private_notes'],
        hiking_group_at_visit_time = (f"{request.POST['hg_adults']}, {request.POST['hg_kids']}, {request.POST['hg_ppl_w_dis']}, {request.POST['hg_pets']}"),
        rating = request.POST['rating'],
        user_id = User.objects.get(email = request.session['email']).id,
        park_id = Park.objects.last().id,
    )
    print("*"*30, "\npost request: ", request.POST)
    return redirect('/dashboard')

def create_report(request, park_id):
    print("*"*60,"\ncreating a new trail report with: ", request.POST, "\nrequest.session: ", request.session['email'])
    #uses add_trail_report form info to create new Visit
    if len(Visit.objects.filter(user_id=User.objects.get(email=request.session['email']).id).filter(park_id=park_id))>0:
        print("*~"*60,"\ncreate trail report filter: ", Visit.objects.filter(park_id=park_id).filter(user_id=User.objects.get(email=request.session['email']).id))
        # update existing visit & switch has_visited to True
        visit = Visit.objects.filter(park_id=park_id).get(user_id=User.objects.get(email=request.session['email']).id)
        visit.has_visited = True
        visit.date_visited = request.POST['date_visited']
        visit.public_notes = request.POST['public_notes']
        visit.private_notes = request.POST['private_notes']
        visit.hiking_group_at_visit_time = (request.POST['hg_adults'], request.POST['hg_kids'], request.POST['hg_ppl_w_dis'], request.POST['hg_pets'])
        # visit.hiking_group_at_visit_time = (f"{request.POST['hg_adults']}, {request.POST['hg_kids']}, {request.POST['hg_ppl_w_dis']}, {request.POST['hg_pets']}")
        visit.rating = request.POST['rating']
        visit.save()
    else: #create new Visit & set has_visited = True
        Visit.objects.create(
            has_visited = True,
            date_visited = request.POST['date_visited'],
            public_notes = request.POST['public_notes'],
            private_notes = request.POST['private_notes'],
            hiking_group_at_visit_time = (f"{request.POST['hg_adults']}, {request.POST['hg_kids']}, {request.POST['hg_ppl_w_dis']}, {request.POST['hg_pets']}"),
            rating = request.POST['rating'],
            user_id = User.objects.get(email = request.session['email']).id,
            park_id = park_id,
        )
    return redirect('/dashboard')

def add_visit_from_results(request, park_id):
    #creates visit with logged-in user's id && park id 
    #leave all defaults (esp has_visited=False)
    #? where to redirect? 
    #want to stay on search results and keep filtered search
    pass

def add_visit_from_park_profile(request, park_id):
    #same as above, but different routing
    Visit.objects.create(
        user = User.objects.get(email=request.session['email']),
        park = Park.objects.get(id=park_id),
    )
    return redirect('/park_profile/'+str(park_id))

def remove_park_from_list(request, park_id):
    #remove unvisited park from user's to-go list
    user = User.objects.get(email=request.session['email'])
    visit = Visit.objects.filter(user_id = user.id).get(park_id=park_id)
    visit.delete()
    return redirect('/dashboard')