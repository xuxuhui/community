from user.models import Message
from user import settings
from .base import get_object


def count(**kwargs):
    where = {}
    if kwargs.get("status"):
        where["status"] = kwargs["status"]
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]

    count = Message.objects.filter(**where).count()
    return count


def search(limit=settings.pageSize, page=settings.page, **kwargs):
    offset = int(limit) * (int(page) - 1)
    size = int(limit) * int(page)
    where = {}
    if kwargs.get("status"):
        where["status"] = kwargs["status"]
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]

    message_list = Message.objects.filter(**where)[offset:size]

    return message_list


def load(**kwargs):

    message_list = Message.objects.filter(**kwargs)
    message = get_object(message_list)

    return message


def delete(**kwargs):

    Message.objects.filter(**kwargs).delete()
