from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = 'releases_notifier'

urlpatterns= [
    path('', views.main_page, name='index'),
    path('index/', RedirectView.as_view(url='', permanent=True)),
    path('save_query/', views.save_query, name='save_query'),
    path('delete_query/', views.delete_query, name='delete_query'),
    path('saved_query_results/', views.search_saved_query, name='saved_query_results')
]