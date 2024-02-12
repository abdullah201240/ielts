from django.contrib import admin
from django.urls import path
from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Index, name='index'),

    path('login', views.Login, name='login'),
    path('signup/', views.Signup, name='signup'),
    path('home/', views.Home, name='home'),
    path('logout/', views.Logout, name='logout'),
    path('profile/', views.Profile, name='profile'),
    path('history/',views.Historys, name='history'),  
    path('change_password/', views.change_password, name='change_password'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
]
