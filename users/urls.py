from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView, name="logout"),
    path("list/", views.UserListView.as_view(), name="user-list"),
    path("<int:user_id>/", views.UserDetailView.as_view(), name="user-detail"),
    path("edit-profile/", views.UserEditView.as_view(), name="edit-profile"),
    path("change-password/", views.UserPasswordChangeView.as_view(), name="change-password"),
]
