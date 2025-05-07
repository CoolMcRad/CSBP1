from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView, name='index'),
    path('<int:question_id>/', views.DetailView, name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('secret/', views.secret, name='secret'),
    path('unauthorized/', views.UnauthorizedView, name='unauthorized'),
    path('all_polls/', views.AllPollsView, name='all_polls'),
    path('create_poll/', views.CreatePollView, name='create_poll'),
    path('search/', views.SearchView, name='search'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('', views.HomePageView, name='home'),
]