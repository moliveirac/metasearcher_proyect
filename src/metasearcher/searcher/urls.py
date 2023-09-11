from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = 'searcher'

urlpatterns= [
    path('', views.index, name='index'),
    path('index/', RedirectView.as_view(url='', permanent=True)),
    path('search/', views.search_view, name='search'),
    path('advanced/', views.advanced_search_index, name='adv_index'),
    path('advanced/search/', views.advanced_search_view, name='adv_search'),
    path('advanced/search/next-page', views.next_cursor_page, name='adv_search_results'),
    path('search/detail', views.detail_view,  name='detail_view'),
    path('get-last-pub/', views.send_query, name='get_last_pub'),
]