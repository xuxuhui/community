from user.models import Passport, Follow
from user import settings
from .base import get_object


def count(**kwargs):
    where = {}
    if kwargs.get("mobile"):
        where["mobile"] = kwargs["mobile"]
    if kwargs.get("email"):
        where["email"] = kwargs["email"]
    count = Passport.objects.filter(**where).count()
    return count


def search(limit=settings.pageSize, page=settings.page, **kwargs):
    offset = int(limit) * (int(page) - 1)
    size = int(limit) * int(page)
    where = {}
    if kwargs.get("mobile"):
        where["mobile"] = kwargs["mobile"]
    if kwargs.get("email"):
        where["email"] = kwargs["email"]
    if kwargs.get("id__in"):
        where["id__in"] = kwargs["id__in"]
    if kwargs.get("name"):
        where["name"] = kwargs["name"]
    Passport_list = Passport.objects.filter(**where)[offset:size]

    return Passport_list


def load(**kwargs):
    where = {}
    if kwargs.get("mobile"):
        where["mobile"] = kwargs["mobile"]
    if kwargs.get("email"):
        where["email"] = kwargs["email"]
    if kwargs.get("id"):
        where["id"] = kwargs["id"]
    if kwargs.get("passport_id"):
        where["id"] = kwargs["passport_id"]
    if kwargs.get("name"):
        where["name"] = kwargs["name"]
    passport_list = Passport.objects.filter(**where)
    return get_object(passport_list)


def modify(**kwargs):
    where = {}
    data = {}
    if kwargs.get("id"):
        where["id"] = kwargs["id"]
    if kwargs.get("avert"):
        data["avert"] = kwargs["avert"]
    if kwargs.get("name"):
        data["name"] = kwargs["name"]
    if kwargs.get("password"):
        data["password"] = kwargs["password"]
    if kwargs.get("signature"):
        data["signature"] = kwargs["signature"]

    Passport.objects.filter(**where).update(**data)


def follow(**kwargs):
    where = {}
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]
    if kwargs.get("follow_id"):
        where["follow_id"] = kwargs["follow_id"]

    follow_list = Follow.objects.filter(**where)

    return follow_list
