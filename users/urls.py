from django.urls import path, include

from users.views import login_user, site_settings
from . import views


app_name = "users"
urlpatterns = [
    path('', include(views.drf_router.urls)),
    path('login/', login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('settings/', site_settings, name='settings'),
]
