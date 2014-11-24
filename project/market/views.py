from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse, Http404

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate

from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from mimetypes import guess_type

from forms import *
from models import *
from tools import *
from datetime import datetime
from django.utils import timezone

import httplib
import json
import sys


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


def send_verification_email(request):
    if not 'username' in request.GET:
        return HttpResponse('missing username')

    user = None
    try:
        user = User.objects.get(username__exact=request.GET['username'])
    except User.DoesNotExist:
        return HttpResponse('invalid username')

    token = default_token_generator.make_token(user)
    email_body = """
Please click the following link to reset your password:
http://%s%s
""" % (request.get_host(), reverse('reset_password', args=[user.username, token]))

    send_mail(subject='Reset your password',
              message=email_body,
              from_email='noreply.OFM.CMU@gmail.com',
              recipient_list=[user.email])

    return HttpResponse('success')


def reset_password(request, username, token):
    context = {}
    errors = []
    context['errors'] = errors
    context['page_title'] = 'Reset password'
    context['username'] = username
    context['token'] = token

    user = get_object_or_404(User, username=username)

    if not default_token_generator.check_token(user, token):
        raise Http404

    if request.method == 'GET':
        return render(request, 'reset_password.html', context)

    form = ResetPasswordForm(request.POST)
    if not form.is_valid():
        for field, form_errors in form.errors.items():
            for error in form_errors:
                errors.append(error)
        return render(request, 'reset_password.html', context)

    user.set_password(form.cleaned_data.get('password'))
    user.save()

    return redirect(reverse('login'))


@login_required
def home(request):
    return buyer_view(request)


@login_required
def buyer_view(request, id='0'):
    context = {'mode': 'buyer_view'}
    items = []
    context['items'] = items

    if id == '0':
        item_objs = Item.objects.all()
    else:
        item_objs = Item.objects.filter(category__exact=id)

    item_objs = filter(lambda o:not o.transaction.is_closed, item_objs)

    for item_obj in item_objs:
        item = {}
        item['id'] = item_obj.id
        item['category'] = category_converter(item_obj.category)
        item['name'] = item_obj.name
        item['is_auction'] = item_obj.transaction.is_auction
        item['price'] = '%.2f' % (item_obj.transaction.deal_price / 100.0)
        item['start_time'] = item_obj.transaction.start_time
        item['end_time'] = item_obj.transaction.end_time
        item['seller'] = {'name':item_obj.transaction.seller.username}
        item['description'] = item_obj.description

        pics = []
        if item_obj.pic1:
            pics.append("/media/item/%d/1" % item_obj.id)
        if item_obj.pic2:
            pics.append("/media/item/%d/2" % item_obj.id)
        if item_obj.pic3:
            pics.append("/media/item/%d/3" % item_obj.id)
        if item_obj.pic4:
            pics.append("/media/item/%d/4" % item_obj.id)
        item['pics'] = pics

        items.append(item)

    items.sort(key=lambda x:x['start_time'], reverse=True)

    return render(request, 'buyer_view.html', context)


@login_required
def item_detail(request, id):
    context = {'mode': 'buyer_view'}
    item = {}
    context['item'] = item

    item_obj = get_object_or_404(Item, id=id)
    seller_obj = item_obj.transaction.seller

    seller = {'name':seller_obj.username}
    rates = [x for x in map(lambda x:x.buyer_rate, Transaction.objects.filter(seller__exact=seller_obj)) if x]
    if len(rates) > 0:
        rate = int(round(sum(rates) / float(len(rates)), 0))
        seller['stars'] = xrange(rate)
        seller['empty_stars'] = xrange(5 - rate)
    item['seller'] = seller

    item['id'] = item_obj.id
    item['category'] = category_converter(item_obj.category)
    item['name'] = item_obj.name
    item['is_closed'] = item_obj.transaction.is_closed
    item['deal_time'] = item_obj.transaction.deal_time if item_obj.transaction.is_closed else None
    item['is_auction'] = item_obj.transaction.is_auction
    item['price'] = '%.2f' % (item_obj.transaction.deal_price / 100.0)
    item['start_time'] = item_obj.transaction.start_time
    item['end_time'] = item_obj.transaction.end_time
    item['description'] = item_obj.description
    item['sold_by_curr_user'] = item_obj.transaction.seller == request.user
    item['curr_username'] = request.user.username

    qas = map(lambda x:{'q':x.query, 'a':x.answer, 'id':x.id}, item_obj.questions.all())
    item['qas'] = qas

    bid_logs = list(item_obj.transaction.bid_logs.all())
    bid_logs.sort(key=lambda x:x.bid_price, reverse=True)
    item['bid_log'] = map(lambda x:{'bidder':x.user,
                                    'price':"%.2f" % (float(x.bid_price) / 100),
                                    'time':x.bid_time}, bid_logs)

    pics = []
    if item_obj.pic1:
        pics.append("/media/item/%d/1" % item_obj.id)
    if item_obj.pic2:
        pics.append("/media/item/%d/2" % item_obj.id)
    if item_obj.pic3:
        pics.append("/media/item/%d/3" % item_obj.id)
    if item_obj.pic4:
        pics.append("/media/item/%d/4" % item_obj.id)
    item['pics'] = pics

    if 'pay_status' in request.GET:
        if request.GET['pay_status'] == 'success':
            context['pay_msg'] = "Your payment is approved."
        elif request.GET['pay_status'] == 'error':
            context['pay_msg'] = "An error occured when redirecting to PayPal. Please try again."
        elif request.GET['pay_status'] == 'cancel':
            context['pay_msg'] = "Your payment is canceled."
        elif request.GET['pay_status'] == 'pending':
            context['pay_msg'] = "Another payment is still pending."

    return render(request, 'item_detail.html', context)


@login_required
def post_item(request):
    form = PostItemForm(request.POST, request.FILES)

    if not form.is_valid():
        return redirect(reverse('seller_view'))

    transaction = None
    if form.cleaned_data.get('mode') == 'fixed':
        transaction = Transaction(deal_price=(int(form.cleaned_data.get('price') * 100)),
                                  seller=request.user)
    else:
        transaction = Transaction(deal_price=(int(form.cleaned_data.get('price') * 100)),
                                  seller=request.user,
                                  end_time=form.cleaned_data.get('endtime'),
                                  is_auction=True)
    transaction.save()

    item = Item(name=form.cleaned_data.get('name'),
                description=form.cleaned_data.get('description'),
                transaction=transaction,
                category=form.cleaned_data.get('category'))
    if form.cleaned_data.get('pic1'):
        item.pic1 = form.cleaned_data.get('pic1')
    if form.cleaned_data.get('pic2'):
        item.pic2 = form.cleaned_data.get('pic2')
    if form.cleaned_data.get('pic3'):
        item.pic3 = form.cleaned_data.get('pic3')
    if form.cleaned_data.get('pic4'):
        item.pic4 = form.cleaned_data.get('pic4')
    item.save()

    return redirect(reverse('item_detail', args=[item.id]))

@login_required
def get_item_pic(request, itemid, index):
    item = get_object_or_404(Item, id=itemid)

    pic = None
    if index == '1':
        pic = item.pic1
    elif index == '2':
        pic = item.pic2
    elif index == '3':
        pic = item.pic3
    elif index == '4':
        pic = item.pic4

    if not pic:
        raise Http404

    content_type = guess_type(pic.name)
    return HttpResponse(pic, content_type=content_type)

@login_required
def buy_fixed_price_item(request):
    if not 'itemid' in request.POST or not request.POST["itemid"]:
        return HttpResponse('missing itemid')

    if not 'msg' in request.POST:
        return HttpResponse('missing message')

    item = None
    try:
        item = Item.objects.get(id__exact=request.POST["itemid"])
    except Item.DoesNotExist:
        return HttpResponse('invalid itemid')

    if item.transaction.seller.username == request.user.username:
        return HttpResponse('the seller cannot be the buyer')

    trans = item.transaction
    trans.deal_time = datetime.now()
    trans.is_closed = True
    trans.buyer = request.user
    trans.save()

    email_body = """The following item is bought by %s:
Item name: %s
Item description: %s
Item price: $%.2f

The buyer left the following message:
%s
""" % (request.user.username, item.name, item.description, float(trans.deal_price)/100, request.POST["msg"])

    send_mail(subject='An item has been sold!',
              message=email_body,
              from_email='noreply.OFM.CMU@gmail.com',
              recipient_list=[item.transaction.seller.email])

    return HttpResponse('success')

@login_required
def pay_by_paypal(request):
    host_name = request.get_host()

    if not 'itemid' in request.POST or not request.POST["itemid"]:
        return HttpResponse('missing itemid')

    item = None
    try:
        item = Item.objects.get(id__exact=request.POST["itemid"])
    except Item.DoesNotExist:
        return HttpResponse('invalid itemid')

    if item.transaction.seller.username == request.user.username:
        return HttpResponse('the seller cannot be the buyer')

    if item.transaction.is_closed:
        return HttpResponse('the transaction is already closed')

    if item.transaction.paykey:
        resp = get_paypal_payment_detail(item.transaction.paykey)
        if resp['status'] != "EXPIRED" or resp['status'] != "ERROR":
            return redirect("https://%s/item_detail/%d?pay_status=pending" % (host_name, item.id))

    # init a transaction, and redirect to paypal
    resp = init_paypal_payment(host_name, item)
    if resp['responseEnvelope']['ack'] == 'Success':
        # update the paykey and buyer
        trans = item.transaction
        trans.paykey = resp['payKey']
        trans.buyer = request.user
        trans.save()
        return redirect('https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey=%s' % resp['payKey'])
    else:
        return redirect("https://%s/item_detail/%d?pay_status=error" % (host_name, item.id))

@login_required
def finish_paypal_payment(request, id):
    item = None
    try:
        item = Item.objects.get(id__exact=id)
    except Item.DoesNotExist:
        return HttpResponse('invalid itemid')

    if not item.transaction.paykey:
        return HttpResponse('the payment is not initiated')

    if item.transaction.buyer.username != request.user.username:
        return HttpResponse('you are not the buyer')

    print(item.transaction.paykey)
    resp = get_paypal_payment_detail(item.transaction.paykey)
    if resp['status'] == "COMPLETED":
        trans = item.transaction
        trans.deal_time = timezone.now()
        trans.is_closed = True
        trans.save()
        return redirect("https://%s/item_detail/%d?pay_status=success" % (request.get_host(), item.id))
    return redirect("https://%s/item_detail/%d" % (request.get_host(), item.id))

def init_paypal_payment(host_name, item):
    conn = httplib.HTTPSConnection('svcs.sandbox.paypal.com')
    conn.request('POST',
                 '/AdaptivePayments/Pay',
                 json.dumps({"actionType":"PAY",
                            "currencyCode":"USD",
                            "payKeyDuration":"PT10M",
                            "receiverList":{"receiver":[{
                                "amount":"%.2f" % (float(item.transaction.deal_price) / 100),
                                "email":"%s@andrew.cmu.edu" % item.transaction.seller.username}]},
                            "returnUrl":"https://%s/finish_paypal_payment/%d" % (host_name, item.id),
                            "cancelUrl":"https://%s/item_detail/%d?pay_status=cancel" % (host_name, item.id),
                            "requestEnvelope":{
                                "errorLanguage":"en_US",
                                "detailLevel":"ReturnAll"}
                           }),
                 {'X-PAYPAL-SECURITY-USERID': 'tianyux-facilitator_api1.andrew.cmu.edu',
                  'X-PAYPAL-SECURITY-PASSWORD': 'K4T4WH8S5RSAMN7V',
                  'X-PAYPAL-SECURITY-SIGNATURE': 'An2ziE2QZvylPCnOQ4l2ELVRsqTrARZS7CP-P68Ic4xlCwS0Yc4z3bhD',
                  'X-PAYPAL-APPLICATION-ID': 'APP-80W284485P519543T',
                  'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
                  'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON'})

    # if the transaction is initiated, redirect to paypal
    return json.loads(conn.getresponse().read())

def get_paypal_payment_detail(paykey):
    conn = httplib.HTTPSConnection('svcs.sandbox.paypal.com')
    conn.request('POST',
             '/AdaptivePayments/PaymentDetails',
             json.dumps({"payKey":paykey,
                        "requestEnvelope":{
                            "errorLanguage":"en_US",
                            "detailLevel":"ReturnAll"}
                       }),
             {'X-PAYPAL-SECURITY-USERID': 'tianyux-facilitator_api1.andrew.cmu.edu',
              'X-PAYPAL-SECURITY-PASSWORD': 'K4T4WH8S5RSAMN7V',
              'X-PAYPAL-SECURITY-SIGNATURE': 'An2ziE2QZvylPCnOQ4l2ELVRsqTrARZS7CP-P68Ic4xlCwS0Yc4z3bhD',
              'X-PAYPAL-APPLICATION-ID': 'APP-80W284485P519543T',
              'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
              'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON'})

    resp = json.loads(conn.getresponse().read())
    return resp

@login_required
def place_bid(request):
    if not 'itemid' in request.POST or not request.POST["itemid"]:
        return HttpResponse('missing itemid')

    if not 'price' in request.POST or not request.POST["price"]:
        return HttpResponse('missing bidding price')

    price = 0
    try:
        price = int(float(request.POST["price"]) * 100)
    except ValueError:
        return HttpResponse('invalid bidding price')

    item = None
    try:
        item = Item.objects.get(id__exact=request.POST["itemid"])
    except Item.DoesNotExist:
        return HttpResponse('invalid itemid')

    trans = item.transaction

    if trans.seller.username == request.user.username:
        return HttpResponse('the seller cannot be the buyer')

    if price - trans.deal_price < 50:
        return HttpResponse('the bid is too low')

    trans.deal_price = price
    trans.save()

    log = BidLog(bid_price=price,
                user=request.user,
                transaction=trans,)
    log.save()

    return HttpResponse('success')

@login_required
def seller_view(request):
    context = {'mode':'seller_view'}
    return render(request, 'seller_view.html', context)

@login_required
def my_account(request):
    context = {'mode':'my_account'}
    transcations_bought = []
    context['transcations_bought'] = transcations_bought
    transcations_sold = []
    context['transcations_sold'] = transcations_sold

    for trans in Transaction.objects.filter(buyer__exact=request.user):
        trans.deal_price /= 100.0
        transcations_bought.append(trans)

    for trans in Transaction.objects.filter(seller__exact=request.user):
        trans.deal_price /= 100.0
        transcations_sold.append(trans)

    return render(request, 'my_account.html', context)

@login_required
def ask_question(request):
    if not 'itemid' in request.POST or not request.POST['itemid']:
        return HttpResponse('missing itemid')

    if not 'question' in request.POST or not request.POST['question']:
        return HttpResponse('missing question')

    item = None
    try:
        item = Item.objects.get(id__exact=request.POST['itemid'])
    except Item.DoesNotExist:
        return HttpResponse('invalid itemid')

    if item.transaction.seller.username == request.user.username:
        return HttpResponse('the seller cannot ask himself a question')

    question = ItemQuestions(query=request.POST['question'], item=item)
    question.save()

    return HttpResponse('success')

@login_required
def answer_question(request):
    if not 'questionid' in request.POST or not request.POST['questionid']:
        return HttpResponse('missing questionid')

    if not 'answer' in request.POST or not request.POST['answer']:
        return HttpResponse('missing answer')

    question = None
    try:
        question = ItemQuestions.objects.get(id__exact=request.POST['questionid'])
    except ItemQuestions.DoesNotExist:
        return HttpResponse('invalid questionid')

    if not question.item.transaction.seller.username == request.user.username:
        return HttpResponse('only the seller can answer the question')

    question.answer = request.POST['answer']
    question.save()

    return HttpResponse('success')

@login_required
def search(request):
    if not 'keyword' in request.GET:
        raise Http404

    if not 'mode' in request.GET or not (request.GET['mode'] == 'items' or request.GET['mode'] == 'demands'):
        raise Http404

    if not 'category' in request.GET or not 0 <= int(request.GET['category']) <= 15:
        raise Http404

    context = {'mode': 'buyer_view'}


    if request.GET['mode'] == 'items':
        items = []
        context['items'] = items
        if not request.GET['keyword']:
            if int(request.GET['category']) == 0:
                item_objs = Item.objects.all()
            else:
                item_objs = Item.objects.filter(category__exact=request.GET['category'])
        else:
            if int(request.GET['category']) == 0:
                item_objs = Item.objects.filter(name__contains=request.GET['keyword']) \
                    | Item.objects.filter(description__contains=request.GET['keyword'])
            else:
                item_objs = Item.objects.filter(name__contains=request.GET['keyword']).filter(category__exact=request.GET['category']) \
                    | Item.objects.filter(description__contains=request.GET['keyword']).filter(category__exact=request.GET['category'])

        for item_obj in item_objs:
            item = {}
            item['id'] = item_obj.id
            item['category'] = category_converter(item_obj.category)
            item['name'] = item_obj.name
            item['is_auction'] = item_obj.transaction.is_auction
            item['price'] = '%.2f' % (item_obj.transaction.deal_price / 100.0)
            item['start_time'] = item_obj.transaction.start_time
            item['end_time'] = item_obj.transaction.end_time
            item['seller'] = {'name':item_obj.transaction.seller.username}
            item['description'] = item_obj.description

            bid_logs = list(item_obj.transaction.bid_logs.all())
            bid_logs.sort(key=lambda x:x.bid_price, reverse=True)
            item['bid_log'] = map(lambda x:{'bidder':x.user,
                                            'price':"%.2f" % (float(x.bid_price) / 100),
                                            'time':x.bid_time}, bid_logs)

            pics = []
            if item_obj.pic1:
                pics.append("/media/item/%d/1" % item_obj.id)
            if item_obj.pic2:
                pics.append("/media/item/%d/2" % item_obj.id)
            if item_obj.pic3:
                pics.append("/media/item/%d/3" % item_obj.id)
            if item_obj.pic4:
                pics.append("/media/item/%d/4" % item_obj.id)
            item['pics'] = pics

            items.append(item)

        items.sort(key=lambda x:x['start_time'], reverse=True)

        return render(request, 'search_item.html', context)

    # TODO
    if request.GET['mode'] == 'demands':
        raise Http404

@login_required
def rate(request):
    if not 'itemid' in request.POST or not request.POST['itemid']:
        return HttpResponse('missing itemid')

    if not 'mode' in request.POST or not request.POST['mode']:
        return HttpResponse('missing mode')

    if not request.POST['mode'] == 'rate_on_buyer' and not request.POST['mode'] == 'rate_on_seller':
        return HttpResponse('invalid mode')

    if not 'rate' in request.POST or not request.POST['rate']:
        return HttpResponse('missing rate')

    try:
        int(request.POST['rate'])
    except ValueError:
        return HttpResponse('invalid rate')

    if not 1 <= int(request.POST['rate']) <= 5:
        return HttpResponse('invalid rate')

    item = None
    try:
        item = Item.objects.get(id__exact=request.POST['itemid'])
    except Item.DoesNotExist:
        return HttpResponse('invalid itemid')

    if request.POST['mode'] == 'rate_on_buyer':
        if not item.transaction.is_closed:
            return HttpResponse('transaction is still open')
        if not item.transaction.seller.username == request.user.username:
            return HttpResponse('you are not the seller')
        if item.transaction.seller_rate:
            return HttpResponse('this transaction has been rated')

        item.transaction.seller_rate = int(request.POST['rate'])
        item.transaction.save()

    else:
        if not item.transaction.is_closed:
            return HttpResponse('transaction is still open')
        if not item.transaction.buyer.username == request.user.username:
            return HttpResponse('you are not the buyer')
        if item.transaction.buyer_rate:
            return HttpResponse('this transaction has been rated')

        item.transaction.buyer_rate = int(request.POST['rate'])
        item.transaction.save()

    return HttpResponse('success')

