from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import FirstRunForm


def status(request):
    if not User.objects.exists():
        return redirect('first-run')
    elif request.user.is_authenticated:
        return render(request, 'status.html', {'title': 'Server Status'})
    else:
        return redirect('admin:login')


class FirstRunView(FormView):
    template_name = 'first_run.html'
    form_class = FirstRunForm
    success_url = reverse_lazy('status')

    def dispatch(self, request, *args, **kwargs):
        # Only work if no user exists
        if User.objects.exists():
            return redirect('status')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'hidenav': True})
        return context