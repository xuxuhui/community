from django.db.models import Count
from user.models import CommentFavour
from user import settings
from .base import get_object


def count(**kwargs):
    where = {}
    if kwargs.get("comment_id__in"):
        where["comment_id__in"] = kwargs["comment_id__in"]
    if kwargs.get("comment_id"):
        where["comment_id"] = kwargs["comment_id"]

    count = CommentFavour.objects.filter(**where).count()

    return count


def search(limit=settings.pageSize, page=settings.page, **kwargs):
    where = {}
    offset = int(limit) * (int(page) - 1)
    size = int(limit) * int(page)
    if kwargs.get("comment_id__in"):
        where["comment_id__in"] = kwargs["comment_id__in"]
    if kwargs.get("comment_id"):
        where["comment_id"] = kwargs["comment_id"]
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]

    comment_favour_list = CommentFavour.objects.filter(**where)[offset:size]

    return comment_favour_list


def group(**kwargs):
    where = {}
    if kwargs.get("comment_id__in"):
        where["comment_id__in"] = kwargs["comment_id__in"]

    comment_favour_list = CommentFavour.objects.filter(**where).values('comment_id').annotate(dcount=Count('comment_id'))

    return comment_favour_list


def load(**kwargs):
    where = {}
    if kwargs.get("comment_id"):
        where["comment_id"] = kwargs["comment_id"]
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]

    comment_favour_list = CommentFavour.objects.filter(**where)
    comment_favour = get_object(comment_favour_list)

    return comment_favour


def delete(**kwargs):

    CommentFavour.objects.filter(**kwargs).delete()
