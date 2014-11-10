from django.shortcuts import render, redirect, get_object_or_404

from django.http import Http404

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate


from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from forms import *
from models import *
from tools import *
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

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)

    return redirect(reverse('home'))


@login_required
def home(request):
    return buyer_view(request)


@login_required
def buyer_view(request):
    context = {'mode': 'buyer_view'}
    item = {'pics':['/static/img/item1_1.jpg', '/static/img/item1_2.jpg'], 'description':'hahahahahahahahah', 'category':'Apps & Games', 'name': 'WeChat', 'is_auction': False, 'price': 30, 'start_time':datetime.now(), 'seller':{'name':'hquan'}}
    items = []
    items.append(item)
    context['items'] = items
    return render(request, 'buyer_view.html', context)


@login_required
def item_detail(request, id):
    context = {'mode': 'buyer_view'}
    item = {}
    context['item'] = item

    item_obj = get_object_or_404(Item, id=id)
    seller_obj = item_obj.transaction.seller

    seller = {'name':seller_obj.username}
    item['seller'] = seller

    item['category'] = category_converter(item_obj.category)
    item['name'] = item_obj.name
    item['is_auction'] = item_obj.transaction.is_auction
    item['price'] = item_obj.transaction.deal_price
    item['start_time'] = item_obj.transaction.start_time
    item['end_time'] = item_obj.transaction.end_time
    item['description'] = item_obj.description

    return render(request, 'item_detail.html', context)


@login_required
def post_item(request):
    form = PostItemForm(request.POST)

    if not form.is_valid():
        return redirect(reverse('seller_view'))

    if form.cleaned_data.get('mode') == 'fixed':
        transaction = Transaction(deal_price=form.cleaned_data.get('price'),
                                  seller=request.user)
        transaction.save()

        item = Item(name=form.cleaned_data.get('name'),
                    description=form.cleaned_data.get('description'),
                    transaction=transaction,
                    category=form.cleaned_data.get('category'))
        item.save()

    return redirect(reverse('item_detail', args=[item.id]))

@login_required
def seller_view(request):
    context = {'mode':'seller_view'}
    return render(request, 'seller_view.html', context)

@login_required
def my_account(request):
    context = {'mode':'my_account'}
    return render(request, 'my_account.html', context)
