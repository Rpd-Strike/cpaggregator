from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from accounts.forms import UserForm
from info.forms import UserUpdateForm, HandleCreateForm
from . import forms
from info.models import TaskSheet
from data.models import UserProfile, UserHandle

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
            'username': self.request.user.profile.username})


class UserSubmissionsDetailView(generic.DetailView):
    template_name = 'info/user_submissions_detail.html'
    model = UserProfile
    slug_url_kwarg = 'username'
    slug_field = 'username'


class ResultsDetailView(generic.DetailView):
    template_name = 'info/results_detail.html'
    model = TaskSheet
    slug_url_kwarg = 'sheet_id'
    slug_field = 'sheet_id'
    table = None

    def get_object(self, **kwargs):
        obj = super().get_object(**kwargs)
        submissions = obj.get_best_submissions()
        self.table = ResultsTable(submissions)
        print(submissions)
        return obj

    def get_context_data(self, **kwargs):
        print(kwargs)
        kwargs['table'] = self.table
        return super().get_context_data(**kwargs)


class DashboardView(generic.TemplateView):
    template_name = 'info/dashboard_detail.html'
    model = UserProfile
