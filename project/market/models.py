from django.db import models
from django.contrib.auth.models import User


class UserInfo(models.Model):
    user = models.OneToOneField(User, related_name="info")
    user_hash = models.CharField(max_length=32)
    email_setting = models.IntegerField(default=777)

    def __unicode__(self):
        return self.user.username


class Transaction(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    deal_time = models.DateTimeField(auto_now_add=False, blank=True)
    duration = models.IntegerField(blank=True)
    deal_price = models.FloatField(blank=True)
    is_auction = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    seller = models.ForeignKey(User, related_name="trans_as_seller")
    buyer = models.ForeignKey(User, related_name="trans_as_buyer", blank=True)
    seller_rate = models.FloatField(blank=True)
    buyer_rate = models.FloatField(blank=True)

    def __unicode__(self):
        return self.id


class Item(models.Model):
    name = models.CharField(max_length=128)
    discription = models.CharField(max_length=1024, blank=True)
    transaction = models.OneToOneField(Transaction, related_name='item')
    category = models.CharField(max_length=256)
    pic1 = models.ImageField(upload_to='item_pic', blank=True)
    pic2 = models.ImageField(upload_to='item_pic', blank=True)
    pic3 = models.ImageField(upload_to='item_pic', blank=True)
    pic4 = models.ImageField(upload_to='item_pic', blank=True)
    pic5 = models.ImageField(upload_to='item_pic', blank=True)

    def __unicode__(self):
        return self.name


class BidLog(models.Model):
    bid_time = models.DateTimeField(auto_now_add=True)
    bid_price = models.FloatField()
    user = models.ForeignKey(User, related_name="bid_logs")
    transaction = models.ForeignKey(Transaction, related_name="bid_logs")

    def __unicode__(self):
        return self.bid_price


class Demand(models.Model):
    name = models.CharField(max_length=128)
    discription = models.CharField(max_length=1024, blank=True)
    price = models.FloatField(blank=True)
    user = models.ForeignKey(User, related_name="demands")
    is_closed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class ItemQuestions(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    query = models.CharField(max_length=128)
    answer = models.CharField(max_length=128, blank=True)
    item = models.ForeignKey(Item, related_name="questions")

    def __unicode__(self):
        return self.query


class ShortMessage(models.Model):
    sender = models.ForeignKey(User, related_name="outbox")
    receiver = models.ForeignKey(User, related_name="inbox")
    time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=42)
    content = models.CharField(max_length=1024, blank=True)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_receiver = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title