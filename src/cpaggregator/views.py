from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic


class HomeView(generic.RedirectView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('dashboard'))
        return redirect(reverse_lazy('login'))
