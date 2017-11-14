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
from user.controller import user, catalog, article, comment, message


urlpatterns = [
    url(r'^sendEmail$', user.send_email),
    url(r'^sendMobile$', user.send_mobile),
    url(r'^getImageCode$', user.get_image_code),
    url(r'^verifyName$', user.verify_name),
    url(r'^modifyInfo$', user.improve_user_information),
    url(r'^register$', user.register),
    url(r'^isExist', user.is_exist),
    url(r'^detail', user.detail),
    url(r'^modifyPassword', user.modify_password),
    url(r'^login', user.login),
    url(r'^isLogin', user.is_login),
    url(r'^logout', user.logout),
    url(r'^catalog/create', catalog.create_catalog),
    url(r'^catalog/moveUp', catalog.move_up),
    url(r'^catalog/moveDown', catalog.move_down),
    url(r'^catalog/bottom', catalog.bottom),
    url(r'^catalog/top', catalog.top),
    url(r'^catalog/delete', catalog.delete),
    url(r'^catalog/modify', catalog.modify_catalog),
    url(r'^article/create$', article.create),
    url(r'^article/list$', article.list),
    url(r'^article/detail$', article.detail),
    url(r'^article/addPv$', article.add_pv),
    url(r'^article/collect$', article.collect),
    url(r'^article/cancelCollect$', article.cancel_collect),
    url(r'^article/collectList$', article.collect_list),
    url(r'^catalog/list', catalog.list),
    url(r'^comment/create', comment.add_comment),
    url(r'^comment/list', comment.list),
    url(r'^comment/reply', comment.reply),
    url(r'^comment/favor', comment.favor),
    url(r'^comment/cancelFavor', comment.cancel_favor),
    url(r'^messages', message.list),
    url(r'^message/unread', message.unread),
    # url(r'^comment/delete', catalog.delete),
]
