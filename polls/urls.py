from django.urls import path

from . import views

app_name = 'polls'

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:question_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
    # ex: /polls/5/edit/
    path('<int:question_id>/edit/', views.edit_question, name='edit_question'),
    # search
    path('search_question/', views.search_question, name='search_question'),
    # load_poll (external poll)
    path('load_url/', views.load_url, name='load_url'),

]