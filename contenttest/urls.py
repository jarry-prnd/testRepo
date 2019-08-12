from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('submit/', views.submit_view, name='submit'),
    path('submit-complete/', views.submit_complete_view, name='submit-complete'),
    path('survey-admin/', views.survey_admin_view, name='survey-admin'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #path('signup/', views.signup_view, name='signup'),
    path('csv-download/', views.csv_download, name='csv-download'),

    path('questions/', views.question_post, name="question-post"),
    path('questions/<int:pk>/', views.question_detail, name="question-detail"),
    path('choices/', views.choice_post, name="choice-post"),
    path('choices/<int:pk>/', views.choice_detail, name="choice-detail"),
    path('responsers/', views.responser_list, name="responser-list"),
    path('responsers/<int:pk>/', views.responser_detail, name="responser-detail"),

    path('test/', views.test, name="test"),
]
