# encoding: utf-8
from collections import OrderedDict

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView, UpdateView, TemplateView
from django.http import Http404

from conversejs import xmpp
from conversejs.models import XMPPAccount

from colab.super_archives.models import (EmailAddress,
                                         EmailAddressValidation)
from colab.search.utils import get_collaboration_data, get_visible_threads
from colab.accounts.models import User

from .forms import (UserCreationForm, UserForm, ListsForm,
                    UserUpdateForm, ChangeXMPPPasswordForm)
from .utils import mailman


class LoginView(TemplateView):
    template_name = "accounts/login.html"


class UserProfileBaseMixin(object):
    model = get_user_model()
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user_'


class UserProfileUpdateView(UserProfileBaseMixin, UpdateView):
    template_name = 'accounts/user_update_form.html'
    form_class = UserUpdateForm

    def get_success_url(self):
        return reverse('user_profile', kwargs={'username':
                                               self.object.username})

    def get_object(self, *args, **kwargs):
        obj = super(UserProfileUpdateView, self).get_object(*args, **kwargs)
        if self.request.user != obj and not self.request.user.is_superuser:
            raise PermissionDenied

        return obj

    def get_context_data(self, **kwargs):
        context = super(UserProfileUpdateView, self).get_context_data(**kwargs)
        context['CONVERSEJS_ENABLED'] = getattr(settings, 'CONVERSEJS_ENABLED')
        return context


class UserProfileDetailView(UserProfileBaseMixin, DetailView):
    template_name = 'accounts/user_detail.html'

    def get_context_data(self, **kwargs):
        profile_user = self.object
        context = {}

        count_types = OrderedDict()

        logged_user = None
        if self.request.user.is_authenticated():
            logged_user = User.objects.get(username=self.request.user)

        collaborations, count_types_extras = get_collaboration_data(
            logged_user, profile_user)

        collaborations.sort(key=lambda elem: elem.modified, reverse=True)

        count_types.update(count_types_extras)

        context['type_count'] = count_types
        context['results'] = collaborations[:10]

        query = get_visible_threads(logged_user, profile_user)
        context['emails'] = query.order_by('-received_time')[:10]

        count_by = 'thread__mailinglist__name'
        context['list_activity'] = dict(query.values_list(count_by)
                                        .annotate(Count(count_by))
                                        .order_by(count_by))

        context.update(kwargs)
        return super(UserProfileDetailView, self).get_context_data(**context)


def signup(request):
    BROWSERID_ENABLED = getattr(settings, 'BROWSERID_ENABLED', False)

    if BROWSERID_ENABLED:
        # If the user is not authenticated, redirect to login
        if not request.user.is_authenticated():
            return redirect('login')

    if request.user.is_authenticated():
        # If the user doesn't need to update its main data,
        #   redirect to its profile
        # It happens when user is created by browserid
        # and didn't set his/her main data
        if not request.user.needs_update:
            return redirect('user_profile', username=request.user.username)

    # If the user is authenticated in Persona, but not in the Colab then he
    # will be redirected to the register form.
    if request.method == 'GET':
        if BROWSERID_ENABLED:
            user_form = UserForm()
        else:
            user_form = UserCreationForm()
        lists_form = ListsForm()

        return render(request, 'accounts/user_create_form.html',
                      {'user_form': user_form, 'lists_form': lists_form})

    if BROWSERID_ENABLED:
        user_form = UserForm(request.POST, instance=request.user)
    else:
        user_form = UserCreationForm(request.POST)
    lists_form = ListsForm(request.POST)

    if not user_form.is_valid() or not lists_form.is_valid():
        return render(request, 'accounts/user_create_form.html',
                      {'user_form': user_form, 'lists_form': lists_form})

    user = user_form.save(commit=False)
    user.needs_update = False

    if not BROWSERID_ENABLED:
        user.is_active = False
        user.save()
        EmailAddressValidation.create(user.email, user)
    else:
        user.save()

    # Check if the user's email have been used previously
    #   in the mainling lists to link the user to old messages
    email_addr, created = EmailAddress.objects.get_or_create(
        address=user.email)
    if created:
        email_addr.real_name = user.get_full_name()

    email_addr.user = user
    email_addr.save()

    mailing_lists = lists_form.cleaned_data.get('lists')
    mailman.update_subscription(user.email, mailing_lists)

    messages.success(request, _('Your profile has been created!'))

    return redirect('user_profile', username=user.username)


class ManageUserSubscriptionsView(UserProfileBaseMixin, DetailView):
    http_method_names = [u'get', u'post']
    template_name = u'accounts/manage_subscriptions.html'

    def get_object(self, *args, **kwargs):
        obj = super(ManageUserSubscriptionsView, self).get_object(*args,
                                                                  **kwargs)
        if self.request.user != obj and not self.request.user.is_superuser:
            raise PermissionDenied

        return obj

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        for email in user.emails.values_list('address', flat=True):
            lists = self.request.POST.getlist(email)
            user.update_subscription(email, lists)

        return redirect('user_profile', username=user.username)

    def get_context_data(self, **kwargs):
        context = {}
        context['membership'] = {}

        user = self.get_object()
        emails = user.emails.values_list('address', flat=True)
        all_lists = mailman.all_lists(description=True)

        for email in emails:
            lists = []
            lists_for_address = mailman.mailing_lists(address=email)
            for listname, description in all_lists:
                if listname in lists_for_address:
                    checked = True
                else:
                    checked = False
                lists.append((
                    {'listname': listname, 'description': description},
                    checked
                ))

            context['membership'].update({email: lists})

        context.update(kwargs)

        return super(ManageUserSubscriptionsView,
                     self).get_context_data(**context)


class ChangeXMPPPasswordView(UpdateView):
    model = XMPPAccount
    form_class = ChangeXMPPPasswordForm
    fields = ['password', ]
    template_name = 'accounts/change_password.html'

    def get_success_url(self):
        return reverse('user_profile', kwargs={
            'username': self.request.user.username
        })

    def get_object(self, queryset=None):
        obj = get_object_or_404(XMPPAccount, user=self.request.user.pk)
        self.old_password = obj.password
        return obj

    def form_valid(self, form):
        transaction.set_autocommit(False)

        response = super(ChangeXMPPPasswordView, self).form_valid(form)

        changed = xmpp.change_password(
            self.object.jid,
            self.old_password,
            form.cleaned_data['password1']
        )

        if not changed:
            messages.error(
                self.request,
                _(u'Could not change your password. Please, try again later.')
            )
            transaction.rollback()
            return response
        else:
            transaction.commit()

        messages.success(
            self.request,
            _("You've changed your password successfully!")
        )
        return response


def password_changed(request):
    messages.success(request, _('Your password was changed.'))

    user = request.user

    return redirect('user_profile_update', username=user.username)


def password_reset_done_custom(request):
    msg = _(("We've emailed you instructions for setting "
             "your password. You should be receiving them shortly."))
    messages.success(request, msg)

    return redirect('home')


def password_reset_complete_custom(request):
    msg = _('Your password has been set. You may go ahead and log in now.')
    messages.success(request, msg)

    return redirect('home')


def myaccount_redirect(request, route):
    if not request.user.is_authenticated():
        raise Http404()

    url = '/'.join(('/account', request.user.username, route))

    return redirect(url)
