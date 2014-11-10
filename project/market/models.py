from django.db import models
from django.contrib.auth.models import User


class UserInfo(models.Model):
    user = models.OneToOneField(User, related_name="info")
    email_setting = models.IntegerField(default=7)

    def __unicode__(self):
        return self.user.username


class Transaction(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    deal_time = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    end_time = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    deal_price = models.IntegerField(null=True, blank=True)
    is_auction = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    seller = models.ForeignKey(User, related_name="trans_as_seller")
    buyer = models.ForeignKey(User, related_name="trans_as_buyer", null=True, blank=True)
    seller_rate = models.IntegerField(null=True, blank=True)
    buyer_rate = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.id


class Item(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, null=True, blank=True)
    transaction = models.OneToOneField(Transaction, related_name='item')
    category = models.IntegerField(null=True, blank=True)
    pic1 = models.ImageField(upload_to='item_pic', null=True, blank=True)
    pic2 = models.ImageField(upload_to='item_pic', null=True, blank=True)
    pic3 = models.ImageField(upload_to='item_pic', null=True, blank=True)
    pic4 = models.ImageField(upload_to='item_pic', null=True, blank=True)

    def __unicode__(self):
        return self.name


class BidLog(models.Model):
    bid_time = models.DateTimeField(auto_now_add=True)
    bid_price = models.IntegerField()
    user = models.ForeignKey(User, related_name="bid_logs")
    transaction = models.ForeignKey(Transaction, related_name="bid_logs")

    def __unicode__(self):
        return self.bid_price


class Demand(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User, related_name="demands")
    is_closed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class ItemQuestions(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    query = models.CharField(max_length=128)
    answer = models.CharField(max_length=128, null=True, blank=True)
    item = models.ForeignKey(Item, related_name="questions")

    def __unicode__(self):
        return self.query


class ShortMessage(models.Model):
    sender = models.ForeignKey(User, related_name="outbox")
    receiver = models.ForeignKey(User, related_name="inbox")
    time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=42)
    content = models.CharField(max_length=1024, null=True, blank=True)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_receiver = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title