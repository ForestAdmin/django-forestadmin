import datetime
import uuid

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinLengthValidator
from django.db import models


# ForeignKey example
from django.db.models import UUIDField


class Topic(models.Model):
    name = models.CharField(max_length=200)

class Question(models.Model):
    question_text = models.CharField(max_length=200, validators=[MinLengthValidator(1)], default='how are you?')
    pub_date = models.DateTimeField('date published', default=datetime.datetime(2020, 5, 17))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


# Complex ForeignKey example
class Car(models.Model):
    brand = models.CharField(max_length=200, unique=True)


class Wheel(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='wheels', to_field='brand')


# custom pk example
class Session(models.Model):
    session_key = models.CharField(max_length=40, primary_key=True)
    session_data = models.TextField()
    expire_date = models.DateTimeField()


# ManyToManyField example
class Publication(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class Article(models.Model):
    headline = models.CharField(max_length=100)
    publications = models.ManyToManyField(Publication)

    def __str__(self):
        return self.headline


# OneToOneField example
class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)

    def __str__(self):
        return "%s the place" % self.name


class Restaurant(models.Model):
    place = models.OneToOneField(
        Place,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    serves_hot_dogs = models.BooleanField(default=False)
    serves_pizza = models.BooleanField(default=False)

    def __str__(self):
        return "%s the restaurant" % self.place.name


class Waiter(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return "%s the waiter at %s" % (self.name, self.restaurant)


# Enums example
class Student(models.Model):
    FRESHMAN = 'FR'
    SOPHOMORE = 'SO'
    JUNIOR = 'JR'
    SENIOR = 'SR'
    GRADUATE = 'GR'
    YEAR_IN_SCHOOL_CHOICES = [
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
        (GRADUATE, 'Graduate'),
    ]
    year_in_school = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default=FRESHMAN,
    )


# ArrayField example
class ChessBoard(models.Model):
    board = ArrayField(
        models.CharField(max_length=10, blank=True),
        size=8,
    )


# UUID Field
class Serial(models.Model):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
