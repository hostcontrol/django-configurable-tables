from __future__ import absolute_import

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

import django_tables
from app.forms import LoginForm

from app.models import Customer
from app.tables import CustomerTable


class Main(django_tables.ConfigurableTableView):

    template_name = 'app/customer_list.html'

    model = Customer
    table_class = CustomerTable

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(Main, self).dispatch(request, *args, **kwargs)


class Login(FormView):

    form_class = LoginForm
    template_name = 'app/login.html'

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user:
            login(request=self.request, user=user)
            return redirect(self.request.GET.get('next', '/'))
        else:
            form.add_error(None, 'The username or password is invalid')
            return self.form_invalid(form=form)