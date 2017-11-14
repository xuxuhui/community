from user.models import Token
from user import settings
from .base import get_object


def search(limit=settings.pageSize, page=settings.page, **kwargs):
    offset = int(limit) * (int(page) - 1)
    size = int(limit) * int(page)
    where = {}
    if kwargs.get("mobile"):
        where["mobile"] = kwargs["mobile"]
    if kwargs.get("email"):
        where["email"] = kwargs["email"]
    token_list = Token.objects.filter(**kwargs)[offset:size]

    return token_list


def load(**kwargs):
    token_list = Token.objects.filter(**kwargs)
    return get_object(token_list)
