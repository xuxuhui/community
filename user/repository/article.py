from user.models import Article, Collect
from django.db.models import F
from user import settings
from .base import get_object


def count(**kwargs):
    where = {}
    if kwargs.get("catalog_id"):
        where["catalog_id"] = kwargs["catalog_id"]
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]
    if kwargs.get("ids"):
        where["id__in"] = kwargs.get("ids")

    count = Article.objects.filter(**where).count()

    return count


def search(limit=settings.pageSize, page=settings.page, **kwargs):
    where = {}
    offset = int(limit) * (int(page) - 1)
    size = int(limit) * int(page)
    if kwargs.get("catalog_id"):
        where["catalog_id"] = kwargs["catalog_id"]
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]
    if kwargs.get("ids"):
        where["id__in"] = kwargs.get("ids")

    print(where, "where.....")
    article_list = Article.objects.filter(**where)[offset:size]

    return article_list


def load(**kwargs):
    where = {}
    if kwargs.get("id"):
        where["id"] = kwargs["id"]
    article_list = Article.objects.filter(**where)
    return get_object(article_list)


def update_pv(**kwargs):
    Article.objects.filter(**kwargs).update(pv=F("pv") + 1)


def delete_comment(**kwargs):
    where = {}
    if kwargs.get("article_id"):
        Collect.objects.filter(**where).delete()
