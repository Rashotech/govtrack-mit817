from django.urls import path
from . import views

app_name = 'govtracker'

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('reports/', views.CitizenPostListView.as_view(), name='citizen_post_list'),
    path('reports/<str:reference_number>/', views.CitizenPostDetailView.as_view(), name='citizen_post_detail'),
    path('report-issue/', views.CitizenPostCreateView.as_view(), name='citizen_post_create'),
    path('reports/<str:reference_number>/upvote/', views.upvote_post, name='upvote_post'),
]
