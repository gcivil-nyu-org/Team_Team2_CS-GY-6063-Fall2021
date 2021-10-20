from django.urls import path

from . import views

app_name = 'naturescall'
urlpatterns = [
    path('', views.index, name='index'),
    path('search_restroom/', views.search_restroom, name='search_restroom'),
    path('restroom_detail/<int:r_id>', views.restroom_detail, name='restroom_detail'),
    path('add_restaurant/<slug:r_id>', views.add_restaurant, name ='add_restaurant'),
]
