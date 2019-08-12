from django.db import models
from django.contrib.auth.models import User


class Car(models.Model):
    name = models.CharField(max_length=8)


class CarUser(models.Model):
    username = models.CharField(max_length=8)


class Star(models.Model):
    car = models.ForeignKey(Car, related_name='star_set', related_query_name='star', on_delete=models.CASCADE)
#    user = models.ForeignKey(CarUser, models.CASCADE)
    star_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.car


def create_sample_object():
    car = Car.objects.create(name='car')
#    user = CarUser.objects.create(username='user')
#    user2 = CarUser.objects.create(username='user2')
    Star.objects.create(car=car, star_id=1)
    Star.objects.create(car=car, star_id=2)



class Question(models.Model):
    question_text = models.CharField(max_length=200, blank=False)
    question_type = models.CharField(max_length=10, blank=False)
    limit = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200, blank=False)
    response_num = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class CarOption(models.Model):
    hash_id = models.CharField(max_length=8, blank=True, null=True)
    is_initial = models.NullBooleanField(blank=True, null=True, default=False, verbose_name='최초 입력 여부')
    is_current = models.NullBooleanField(blank=True, null=True, verbose_name='현재 차량 옵션 여부')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def testmethod(*args, **kwargs):
    for key, value in kwargs.items():
        if key in [field.name for field in CarOption._meta.fields]:
            kwargs = {key: kwargs[key] for key in kwargs if key in CarOption._meta.fields}
            print('key: {}, value: {}'.format(key, value))


'''
kwargs
{'id':2,'question_text':'text,'question_type':'type','limit':'3'}
'''

class Responser(models.Model):
    phone_number = models.CharField(max_length=15, unique=True, blank=False)
    choices = models.ManyToManyField(Choice, through='ResponseRecord')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number


class ResponseRecord(models.Model):
    responser = models.ForeignKey(Responser, related_name="response_records", on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, related_name="response_records", on_delete=models.CASCADE)
    rank = models.IntegerField(default=0)
