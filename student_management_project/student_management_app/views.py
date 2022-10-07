from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import CustomUs

# Create your views here.
