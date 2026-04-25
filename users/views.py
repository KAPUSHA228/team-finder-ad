from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect, render, reverse
from django.views.generic import DetailView, ListView, TemplateView, UpdateView

from .forms import UserEditForm, UserLoginForm, UserRegistrationForm
from .models import User


class UserRegisterView(TemplateView):
    template_name = "users/register.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": UserRegistrationForm()})

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # user = form.save()
            return redirect("users:login")
        return render(request, self.template_name, {"form": form})


class UserLoginView(TemplateView):
    template_name = "users/login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": UserLoginForm()})

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("projects:project-list")
            form.add_error(None, "Неверный email или пароль")
        return render(request, self.template_name, {"form": form})


def UserLogoutView(request):
    logout(request)
    return redirect("projects:project-list")


class UserListView(ListView):
    model = User
    template_name = "users/participants.html"
    context_object_name = "participants"
    paginate_by = 12

    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by("-id")


class UserDetailView(DetailView):
    model = User
    template_name = "users/user-details.html"
    context_object_name = "user"
    pk_url_kwarg = "user_id"

    def get_queryset(self):
        return User.objects.filter(is_active=True)


class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = "users/edit_profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context

    def form_valid(self, form):
        # response = super().form_valid(form)
        return redirect("users:user-detail", user_id=self.request.user.id)

    def get_success_url(self):
        return reverse("users:user-detail", kwargs={"user_id": self.request.user.id})


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "users/change_password.html"

    def get_success_url(self):
        return f"/users/{self.request.user.id}/"
