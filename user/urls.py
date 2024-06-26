from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from user.views import (
    GoogleLoginApi,
    GoogleLoginRedirectApi,
    MeView,
    PersonListCreateView,
    PersonRetrieveUpdateDestroyView,
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
    register,
)

app_name = "user"


urlpatterns = [
    path(
        "",
        PersonListCreateView.as_view(),
        name="person-list-create",
    ),
    path(
        "<int:pk>/",
        PersonRetrieveUpdateDestroyView.as_view(),
        name="person-retrieve-update-destroy",
    ),
    path(
        "register/",
        csrf_exempt(register),
        name="register",
    ),
    path(
        "google-redirect/",
        csrf_exempt(GoogleLoginRedirectApi.as_view()),
        name="google-redirect",
    ),
    path("tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path(
        "tasks/<int:pk>/", TaskRetrieveUpdateDestroyView.as_view(), name="task-detail"
    ),
    path("me/", MeView.as_view(), name="me"),
    path("google-login/", csrf_exempt(GoogleLoginApi.as_view()), name="google-login"),
]
