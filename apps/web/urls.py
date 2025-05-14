from django.urls import path
from django.views.generic import TemplateView

app_name = 'web'

urlpatterns = [

    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='auth/login.html'), name='login'),
    path('profile/', TemplateView.as_view(template_name='auth/profile.html'), name='profile'),
    
    path('parts/', TemplateView.as_view(template_name='parts/list.html'), name='parts_list'),
    path('parts/create/', TemplateView.as_view(template_name='parts/create.html'), name='part_create'),
    
    path('aircrafts/', TemplateView.as_view(template_name='aircrafts/list.html'), name='aircrafts_list'),
    path('aircrafts/create/', TemplateView.as_view(template_name='aircrafts/create.html'), name='aircraft_create'),
] 