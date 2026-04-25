from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('list/', views.ProjectListView.as_view(), name='project-list'),
    path('<int:project_id>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('create-project/', views.ProjectCreateView.as_view(), name='project-create'),
    path('<int:project_id>/edit/', views.ProjectEditView.as_view(), name='project-edit'),
    path('<int:project_id>/complete/', views.ProjectCompleteView.as_view(), name='project-complete'),
    path('<int:project_id>/toggle-participate/', views.ToggleParticipateView.as_view(), name='toggle-participate'),
    path('skills/', views.SkillAutocompleteView.as_view(), name='skill-autocomplete'),
    path('<int:project_id>/skills/add/', views.SkillAddView.as_view(), name='skill-add'),
    path('<int:project_id>/skills/<int:skill_id>/remove/', views.SkillRemoveView.as_view(), name='skill-remove'),
]