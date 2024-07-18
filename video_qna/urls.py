from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.app_login, name="login"),
    path("signup", views.app_signup, name="signup"),
    path("logout", views.app_logout, name="logout"),
    path("generate-answer", views.generate_answer, name="generate-answer"),
    path("query-history", views.query_history, name="query-history"),
    path("answer-detail/<int:pk>/", views.answer_detail, name="answer-detail"),
]
