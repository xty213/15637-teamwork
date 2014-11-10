from django.shortcuts import render, redirect, get_object_or_404

from django.http import Http404

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from forms import *
from models import *

from datetime import datetime


def register(request):
    context = {}
    errors = []
    context['errors'] = errors
    context['page_title'] = 'Register'

    if request.method == 'GET':
        return render(request, 'register.html', context)

    form = RegisterForm(request.POST)

    if not form.is_valid():
        for field, form_errors in form.errors.items():
            for error in form_errors:
                errors.append(error)
        return render(request, 'register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data.get('username'),
                                        password=form.cleaned_data.get('password'),
                                        email=(form.cleaned_data.get('username') + '@andrew.cmu.edu'))
    new_user.is_active = False
    new_user.save()
    new_user_info = UserInfo(user=new_user)
    new_user_info.save()

    token = default_token_generator.make_token(new_user)
    email_body = """
Welcome to the online flea market at CMU! Please click the following link to complete your registration:
http://%s%s
""" % (request.get_host(), reverse('confirm_registration', args=[new_user.username, token]))

    send_mail(subject='Verify your email address',
              message=email_body,
              from_email='noreply.OFM.CMU@gmail.com',
              recipient_list=[new_user.email])

    return redirect(reverse('login'))


def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    if not default_token_generator.check_token(user, token):
        raise Http404

    user.is_active = True
    user.save()

    return redirect(reverse('home'))


@login_required
def home(request):
    return buyer_view(request)


@login_required
def buyer_view(request):
    context = {'mode': 'buyer_view'}
    item = {'pics':['/static/img/item1_1.jpg', '/static/img/item1_2.jpg'], 'description':'hahahahahahahahah', 'category':'Apps & Games', 'name': 'WeChat', 'is_auction': False, 'price': 30, 'start_time':datetime.now(), 'seller':'hquan'}
    items = []
    items.append(item)
    context['items'] = items
    return render(request, 'buyer_view.html', context)
