'''
Created on Dec 16, 2019

@author: groupe13
'''
from django.db import models

class User(models.Model):
    Email = models.EmailField(max_length=50)
    Password = models.CharField(max_length=128)
    Firstname = models.CharField(max_length=30)
    Lastname = models.CharField(max_length=50)
    City = models.CharField(max_length=50)
    Street = models.CharField(max_length=30, null=True)
    Infos = models.TextField(null=True)
    Status = (
        ('Parent','Parent'),
        ('Sitter','Sitter'),
        ('Both','Both'),
        )
    Status = models.CharField(max_length=30, choices=Status)
    Price = models.FloatField(null=True)
    Age = models.IntegerField(null=True)
    Admin = models.BooleanField(default=False)
    Banned = models.BooleanField(default=False)
    
    def __str__(self):
        return self.Email + ": " + self.Firstname + " " + self.Lastname
    
class Disponibilities(models.Model):
    SitterId = models.IntegerField(null=True)
    Date = models.TextField(null=True)
    Duration = models.IntegerField(null=True)
    Reserved = models.BooleanField(default=False)
    By = models.IntegerField(null=True)
    Start = models.IntegerField(null=True)
    End = models.IntegerField(null=True)
    Price = models.FloatField(null=True)
    ChildMax = models.IntegerField(null=True)
    City = models.TextField(null=True)
    
class Message(models.Model):
    Date = models.DateTimeField(auto_now=True)
    Target = models.IntegerField(null=True)
    Content = models.TextField()
    Type = models.TextField(null=True)
    Link = models.TextField(null=True)
    
class Comment(models.Model):
    Sitter = models.IntegerField(null=True)
    Parent = models.IntegerField(null=True)
    Reservation = models.IntegerField(null=True)
    Note = models.IntegerField(null=True)
    Comment = models.TextField(null=True)
    Answer = models.BooleanField(default=False)
    Related = models.IntegerField(null=True)
    
class Child(models.Model):
    Name = models.TextField(null=True)
    Parent = models.IntegerField(null=True)
    Age = models.IntegerField(null=True)
    Sex = (
        ('M','M'),
        ('F','F'),
        ('X','X'),
        )
    Sex = models.CharField(max_length=30, choices=Sex)
    Infos = models.TextField(null=True)
    
class Favorite(models.Model):
    User = models.IntegerField(null=True)
    FavoriteUser = models.IntegerField(null=True)
    
class Chat(models.Model):
    Sender = models.IntegerField(null=True)
    Receiver = models.IntegerField(null=True)
    Content = models.TextField(null=True)
    
class Report(models.Model):
    Reported = models.IntegerField(null=True)
    By = models.IntegerField(null=True)
    Date = models.DateTimeField(null=True,auto_now_add=True)
    Comment = models.TextField(null=True)
    
    
    
    