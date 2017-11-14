"""community URL Configuration

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
from pet import views


urlpatterns = [
    url(r'^catalog/create$', views.create_catalog),
    url(r'^catalog/moveUp$', views.move_up),
    url(r'^catalog/moveDown$', views.move_down),
    url(r'^catalog/bottom$', views.bottom),
    url(r'^catalog/top$', views.top),
    url(r'^catalog/delete$', views.delete),
    url(r'^catalog/modify$', views.modify_catalog),
]
