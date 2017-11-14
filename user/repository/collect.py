from user.models import Collect
from user import settings
from .base import get_object


def count(**kwargs):
    where = {}
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]

    count = Collect.objects.filter(**where).count()
    return count


def search(limit=settings.pageSize, page=settings.page, **kwargs):
    offset = int(limit) * (int(page) - 1)
    size = int(limit) * int(page)
    where = {}
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]

    collect_list = Collect.objects.filter(**where)[offset:size]

    return collect_list


def load(**kwargs):

    collect_list = Collect.objects.filter(**kwargs)
    catalog = get_object(collect_list)

    return catalog


def delete(**kwargs):

    Collect.objects.filter(**kwargs).delete()
