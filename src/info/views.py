from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from accounts.forms import UserForm
from info.forms import UserUpdateForm, HandleCreateForm
from . import forms
from info.models import TaskSheet
from data.models import UserProfile, UserHandle, UserGroup, Task

from info.tables import ResultsTable
from django.contrib.messages.views import SuccessMessageMixin
from bootstrap_modal_forms.mixins import PassRequestMixin


class ProfileUpdateView(LoginRequiredMixin, PassRequestMixin,
                        SuccessMessageMixin, generic.UpdateView):
    template_name = 'info/update_profile.html'
    success_message = 'Success: User was updated.'
    success_url = reverse_lazy('me')
    model = UserProfile
    form_class = UserUpdateForm
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_queryset(self):
        return super(ProfileUpdateView, self).get_queryset() \
            .filter(user=self.request.user)


class HandleCreateView(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, generic.CreateView):
    template_name = 'info/create_handle.html'
    success_message = 'Success: Handle was created.'
    model = UserHandle
    success_url = reverse_lazy('me')
    form_class = HandleCreateForm

    def form_invalid(self, form):
        super(HandleCreateView, self).form_invalid(form)
        return redirect(self.success_url)

    def form_valid(self, form):
        super(HandleCreateView, self).form_valid(form)
        return redirect(self.success_url)


class HandleDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = UserHandle
    success_url = reverse_lazy('me')
    slug_url_kwarg = 'handle_id'
    slug_field = 'id'

    def get_queryset(self):
        return super(HandleDeleteView, self).get_queryset() \
            .filter(user__user=self.request.user)


class MeDetailView(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('profile', kwargs={
            'username': self.request.user.username})


class UserSubmissionsDetailView(generic.DetailView):
    template_name = 'info/user_submissions_detail.html'
    model = UserProfile
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        return UserProfile.objects.get(user__username=self.kwargs['username'])


class ResultsDetailView(generic.DetailView):
    template_name = 'info/results_detail.html'
    model = TaskSheet
    slug_url_kwarg = 'sheet_id'
    slug_field = 'sheet_id'
    table = None
    submissions = None
    show_all = False

    def get_object(self, **kwargs):
        obj = super().get_object(**kwargs)
        if self.show_all:
            self.submissions = obj.get_all_submissions()
        else:
            self.submissions = obj.get_best_submissions()

        self.table = ResultsTable(self.submissions)
        return obj

    def get_context_data(self, **kwargs):
        kwargs['table'] = self.table
        context = super(ResultsDetailView, self).get_context_data(**kwargs)

        # Map task to verdict of current user.
        verdict_for_user_dict = {
            submission.task: submission.verdict for submission in
            self.submissions.filter(author__user__user=self.request.user)
        }
        # Build tasks as a dict.
        tasks = [{'task': task, 'verdict_for_user': verdict_for_user_dict.get(task)}
                 for task in self.object.tasks.all()]
        context['tasks'] = tasks
        context['show_all'] = self.show_all

        is_owner = False
        for group in context['object'].groups.all():
            if group.author == self.request.user.profile:
                is_owner = True
        context['is_owner'] = is_owner

        return context


class GroupMemberDeleteView(LoginRequiredMixin, SingleObjectMixin, generic.View):
    model = UserGroup
    slug_field = 'group_id'
    slug_url_kwarg = 'group_id'

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        if group.author == request.user.profile:
            user = get_object_or_404(UserProfile, username=request.POST.get('member_username', ''))
            group.members.remove(user)
        return redirect('group-detail', group_id=group.group_id)


class GroupMemberCreateView(LoginRequiredMixin, PassRequestMixin,
                            SuccessMessageMixin, generic.UpdateView):
    model = UserGroup
    slug_field = 'group_id'
    slug_url_kwarg = 'group_id'
    form_class = forms.GroupMemberCreateForm
    success_message = 'Success: Members were created.'
    template_name = 'info/group_add_members.html'

    def form_valid(self, form):
        group = self.get_object()
        if group.author == self.request.user.profile:
            users = []
            for username in map(str.strip, form.cleaned_data['usernames'].split(',')):
                for user in UserProfile.objects.filter(username=username):
                    users.append(user)
            group.members.add(*users)
        return redirect('group-detail', group_id=group.group_id)


class SheetCreateView(LoginRequiredMixin, PassRequestMixin,
                      SuccessMessageMixin, generic.CreateView):
    model = TaskSheet
    form_class = forms.SheetCreateForm
    success_message = 'Success: Sheet were created.'
    template_name = 'info/create_sheet.html'
    group = None
    success_url = reverse_lazy('home')

    def form_invalid(self, form):
        super(SheetCreateView, self).form_invalid(form)
        return redirect('group-detail', group_id=self.group.group_id)

    def form_valid(self, form):
        super(SheetCreateView, self).form_valid(form)
        return redirect('sheet-results', sheet_id=form.cleaned_data['sheet_id'])

    def dispatch(self, request, *args, **kwargs):
        group_id = kwargs['group_id']
        self.group = UserGroup.objects.get(group_id=group_id)
        return super(SheetCreateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SheetCreateView, self).get_form_kwargs()
        kwargs['group'] = self.group
        return kwargs


class SheetTaskCreateView(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, generic.FormView):
    form_class = forms.SheetTaskCreateForm
    success_message = 'Success: Task was added.'
    template_name = 'info/create_task.html'
    sheet = None
    success_url = reverse_lazy('home')

    def form_invalid(self, form):
        super(SheetTaskCreateView, self).form_invalid(form)
        return redirect('sheet-results', sheet_id=self.sheet.sheet_id)

    def form_valid(self, form):
        task, _ = Task.objects.get_or_create(
            judge=form.cleaned_data['judge'],
            task_id=form.cleaned_data['task_id'],
        )
        self.sheet.tasks.add(task)
        return redirect('sheet-results', sheet_id=self.sheet.sheet_id)

    def dispatch(self, request, *args, **kwargs):
        sheet_id = kwargs['sheet_id']
        self.sheet = get_object_or_404(TaskSheet.objects, sheet_id=sheet_id)
        return super(SheetTaskCreateView, self).dispatch(request, *args, **kwargs)


class SheetDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = 'index.html'
    model = TaskSheet
    success_url = reverse_lazy('home')
    slug_url_kwarg = 'sheet_id'
    slug_field = 'sheet_id'

    def delete(self, request, *args, **kwargs):
        for group in TaskSheet.objects.get(sheet_id=kwargs['sheet_id']).groups.all():
            if group.author == request.user.profile:
                return super(SheetDeleteView, self).delete(request, *args, **kwargs)


class GroupDetailView(generic.DetailView):
    template_name = 'info/group_detail.html'
    model = UserGroup
    slug_url_kwarg = 'group_id'
    slug_field = 'group_id'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            kwargs['is_owner'] = self.request.user.profile == self.object.author
        return super(GroupDetailView, self).get_context_data(**kwargs)


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'info/dashboard_detail.html'
    model = UserProfile

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        context['groups_owned'] = UserGroup.objects.filter(author=self.request.user.profile).all()
        print(context['groups_owned'])
        context['task_sheets'] = [{
            'task_sheet': task_sheet,
            'solved_count': len(task_sheet.get_best_submissions().filter(
                author__user__user=self.request.user, verdict='AC').all()),
        } for task_sheet in self.request.user.profile.get_task_sheets()]

        return context


class SheetDescriptionUpdateView(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin, generic.UpdateView):
    template_name = 'info/sheet_description_update.html'
    model = TaskSheet
    slug_url_kwarg = 'sheet_id'
    slug_field = 'sheet_id'
    form_class = forms.SheetDescriptionUpdateForm

    def get_success_url(self):
        return reverse_lazy('sheet-results', kwargs=dict(sheet_id=self.object.sheet_id))

    def get_form_kwargs(self):
        kwargs = super(SheetDescriptionUpdateView, self).get_form_kwargs()
        kwargs['auto_id'] = False
        return kwargs

    def form_valid(self, form):
        for group in self.object.groups.all():
            if group.author == self.request.user.profile:
                return super(SheetDescriptionUpdateView, self).form_valid(form)
