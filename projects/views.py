from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project
from .utils import paginate_queryset


def project_list(request):
    queryset = Project.objects.select_related("owner").all()
    page_obj, query_prefix = paginate_queryset(request, queryset)
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": queryset,
            "page_obj": page_obj,
            "query_prefix": query_prefix,
        },
    )


@login_required
def favorite_projects(request):
    queryset = request.user.favorites.select_related("owner").all()
    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": queryset},
    )


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=pk,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
@require_POST
def toggle_favorite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    favorites = request.user.favorites
    if favorites.filter(pk=project.pk).exists():
        favorites.remove(project)
        favorited = False
    else:
        favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    participants = project.participants
    if participants.filter(pk=request.user.pk).exists():
        participants.remove(request.user)
        is_participant = False
    else:
        participants.add(request.user)
        is_participant = True
    return JsonResponse({"status": "ok", "participant": is_participant})


@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=403)
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(initial={"status": Project.STATUS_OPEN})
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )
