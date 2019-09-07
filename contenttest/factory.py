import factory.fuzzy
from contenttest.models import Star


class StarFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Star
