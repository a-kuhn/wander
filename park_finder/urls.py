from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('logout', views.logout),
    path('dashboard', views.dashboard),
    path('login', views.login),
    path('register', views.register),
    path('park_search', views.park_search),
    path('add_park', views.add_park),
    path('create_park', views.create_park),
    path('search_db', views.search_db),
    path('search_results', views.search_results),
    path('user_profile/<int:user_id>', views.user_profile),
    path('memory_log/<int:visit_id>', views.memory_log),
    path('add_trail_report/<int:park_id>', views.add_trail_report),
    path('create_report/<int:park_id>', views.create_report),
    path('add_visit_from_results/<int:park_id>', views.add_visit_from_results),
    path('add_visit_from_park_profile/<int:park_id>', views.add_visit_from_park_profile),
    path('park_profile/<int:park_id>', views.park_profile),
    path('remove_park_from_list/<int:park_id>', views.remove_park_from_list),
]