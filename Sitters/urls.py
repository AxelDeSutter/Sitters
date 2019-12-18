"""Sitters URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin


from Sitters.views import Home, Register, Login, Logout, SitterInfos, AddDisponibility, DeleteDisponibility, Search, Users, Profile, Reserve, DeleteMessage, Cancel, CancelReservation, Details, AddComment, AddChild, AddFavorite, AddAnswer, Chatter, Send, AddReport, Reports, Ban

urlpatterns = [
    url(r'^Admin/', admin.site.urls),
    url(r'^$', Home),
    url(r'^Register$', Register),
    url(r'^Login$', Login),
    url(r'^Logout$', Logout),
    url(r'^SitterInfos$', SitterInfos),
    url(r'^Child$', AddChild),
    url(r'^AddDisponibility$', AddDisponibility),
    url(r'^DeleteDisponibility$', DeleteDisponibility),
    url(r'^Search$', Search),
    url(r'^Users$', Users),
    url(r'^Profile$', Profile),
    url(r'^Reserve$', Reserve),
    url(r'^DeleteMessage$', DeleteMessage),
    url(r'^Cancel$', Cancel),
    url(r'^CancelReservation$', CancelReservation),
    url(r'^Details$', Details),
    url(r'^Comment$', AddComment),
    url(r'^Favorite$', AddFavorite),
    url(r'^Answer$', AddAnswer),
    url(r'^Chat$', Chatter),
    url(r'^Send$', Send),
    url(r'^Report$', AddReport),
    url(r'^Reports$', Reports),
    url(r'^Ban$', Ban),
]
