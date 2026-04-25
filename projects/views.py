import json
from django.shortcuts import get_object_or_404, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.http import JsonResponse

from team_finder.settings import BASE_DIR
from .models import Project, Skill
from .forms import ProjectForm

class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        qs = Project.objects.select_related('owner').prefetch_related('participants', 'skills').order_by('-created_at')
        skill_name = self.request.GET.get('skill')
        if skill_name:
            qs = qs.filter(skills__name__iexact=skill_name)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_skills'] = Skill.objects.values_list('name', flat=True).distinct().order_by('name')
        context['active_skill'] = self.request.GET.get('skill')
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        form.instance.participants.add(self.request.user)
        return response

    def get_success_url(self):
        return reverse('projects:project-detail', kwargs={'project_id': self.object.id})


class ProjectEditView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'
    pk_url_kwarg = 'project_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse('projects:project-detail', kwargs={'project_id': self.object.id})


class ProjectCompleteView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user or project.status != 'open':
            return JsonResponse({'status': 'error'}, status=403)
        project.status = 'closed'
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user not in project.participants.all():
            project.participants.add(request.user)
            return JsonResponse({'status': 'ok', 'participant': True})
        project.participants.remove(request.user)
        return JsonResponse({'status': 'ok', 'participant': False})


class SkillAutocompleteView(View):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        if not q:
            return JsonResponse([], safe=False)
        skills = Skill.objects.filter(name__istartswith=q).order_by('name')[:10]
        return JsonResponse([{'id': s.id, 'name': s.name} for s in skills], safe=False)


class SkillAddView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user:
            return JsonResponse({'error': 'Forbidden'}, status=403)

        data = json.loads(request.body)
        skill_id = data.get('skill_id')
        name = data.get('name')

        if skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
            created = False
        elif name:
            skill = Skill.objects.filter(name__iexact=name).first()
            if not skill:
                skill = Skill.objects.create(name=name)
                created = True
            else:
                created = False
        else:
            return JsonResponse({'error': 'No skill_id or name'}, status=400)

        added = False
        if not project.skills.filter(pk=skill.pk).exists():
            project.skills.add(skill)
            added = True

        return JsonResponse({
            'id': skill.id,
            'name': skill.name,
            'created': created,
            'added': added}
        )


class SkillRemoveView(LoginRequiredMixin, View):
    def post(self, request, project_id, skill_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.owner != request.user:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        skill = get_object_or_404(Skill, pk=skill_id)
        project.skills.remove(skill)
        return JsonResponse({'status': 'ok'})
