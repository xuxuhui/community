from user.models import Comment
from user import settings
from .base import get_object
from django.db.models import F
from django.db.models import Count


def count(**kwargs):
    where = {}
    where["left_id__gt"] = 1
    if kwargs.get("parent_id"):
        where["parent_id"] = kwargs["parent_id"]
    if kwargs.get("article_id"):
        where["article_id"] = kwargs["article_id"]
    if kwargs.get("comment_id__in"):
        where["comment_id__in"] = kwargs["comment_id__in"]
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]

    count = Comment.objects.filter(**where).count()
    return count


def search(limit=settings.pageSize, page=settings.page, **kwargs):
    offset = int(limit) * (int(page) - 1)
    size = int(limit) * int(page)
    where = {}
    if kwargs.get("parent_id"):
        where["parent_id"] = kwargs["parent_id"]
    if kwargs.get("article_id"):
        where["article_id"] = kwargs["article_id"]
    if kwargs.get("comment_id__in"):
        where["comment_id__in"] = kwargs["comment_id__in"]
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]

    where["left_id__gt"] = 1
    print(offset, size, 'xxxxx')
    comment_list = Comment.objects.filter(**where).order_by("left_id")[offset:size]

    return comment_list


def group(**kwargs):
    where = {}
    where["left_id__gt"] = 1
    if kwargs.get("article_id__in"):
        where["article_id__in"] = kwargs["article_id__in"]
    if kwargs.get("passport_id"):
        where["passport_id"] = kwargs["passport_id"]

    comment_list = Comment.objects.filter(**where).values('article_id').annotate(count=Count('article_id'))

    return comment_list


def load(**kwargs):
    where = {}
    if kwargs.get("parent_id"):
        where["parent_id"] = kwargs["parent_id"]
    if kwargs.get("article_id"):
        where["article_id"] = kwargs["article_id"]
    if kwargs.get("id"):
        where["id"] = kwargs["id"]
    if "layer" in kwargs:
        where["layer"] = kwargs["layer"]
    comment_list = Comment.objects.filter(**where)
    catalog = get_object(comment_list)

    return catalog


# 新增时需要更新的左节点
def update_left_id(**kwargs):
    where = {}
    if kwargs.get("right_id"):
        where["left_id__gte"] = kwargs["right_id"]
    if kwargs.get("article_id"):
        where["article_id"] = kwargs["article_id"]
    Comment.objects.filter(**where).update(left_id=F('left_id') + 2)


# 新增时需要更新的右节点
def update_right_id(**kwargs):
    where = {}
    if kwargs.get("right_id"):
        where["right_id__gte"] = kwargs["right_id"]
    if kwargs.get("article_id"):
        where["article_id"] = kwargs["article_id"]

    Comment.objects.filter(**where).update(right_id=F('right_id') + 2)


# 查找同级上一个节点
def find_up_catalog(**kwargs):
    where = {}
    if kwargs.get("layer"):
        where["layer"] = kwargs["layer"]
    if kwargs.get("left_id"):
        where["right_id__lt"] = kwargs["left_id"]
    if kwargs.get("article_id"):
        where["article_id"] = kwargs["article_id"]
    comment_list = Comment.objects.filter(**where).order_by("-left_id")[:1]
    catalog = get_object(comment_list)

    return catalog


# 查找同级下一个节点
def find_next_catalog(**kwargs):
    where = {}
    where["left_id__gt"] = kwargs["right_id"]
    where["layer"] = kwargs["layer"]
    where["article_id"] = kwargs["article_id"]
    comment_list = Comment.objects.filter(**where).order_by("left_id")[:1]
    catalog = get_object(comment_list)

    return catalog


# 查找需要移动子节点
def find_move_son(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["left_id"]
    where["right_id__lte"] = kwargs["right_id"]
    where["article_id"] = kwargs["article_id"]
    comment_list = Comment.objects.filter(**where).order_by("left_id")

    return comment_list


# 更新上移目标左节点
def up_catalog_pre_left(**kwargs):
    where = {}
    where["article_id"] = kwargs["v"]
    where["left_id__gte"] = kwargs["left_id"]
    where["right_id__lte"] = kwargs["right_id"]
    step = kwargs["pre_right_id"] - kwargs["pre_left_id"] + kwargs["step"]
    Comment.objects.filter(**where).update(left_id=F("left_id") - step)


# 更新上移目标右节点
def up_catalog_pre_right(**kwargs):
    where = {}
    where["right_id__gt"] = kwargs["pre_right_id"]
    where["right_id__lte"] = kwargs["right_id"]
    where["article_id"] = kwargs["article_id"]
    step = kwargs['pre_right_id'] - kwargs['pre_left_id'] + kwargs['step']
    Comment.objects.filter(**where).update(right_id=F("right_id") - step)


# 更新上移左节点
def up_catalog_cur_left(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["left_id__gte"] = kwargs["pre_left_id"]
    where["right_id__lte"] = kwargs["pre_right_id"]
    step = kwargs["right_id"] - kwargs["left_id"] + kwargs["step"]
    Comment.objects.filter(**where).update(left_id=F("left_id") + step)


# 更新上移右节点
def up_catalog_cur_right(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["pre_left_id"] + (kwargs["right_id"] - kwargs["left_id"] + kwargs["step"])
    where["right_id__lte"] = kwargs["pre_right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    step = kwargs["right_id"] - kwargs["left_id"] + kwargs["step"]
    Comment.objects.filter(**where).update(right_id=F("right_id") + step)


# 更新下移目标左节点
def down_catalog_pre_left(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["left_id__gte"] = kwargs["next_left_id"]
    where["right_id__lte"] = kwargs["next_right_id"]
    step = kwargs["right_id"] - kwargs["left_id"] + kwargs["step"]
    Comment.objects.filter(**where).update(left_id=F("left_id") - step)


# 更新下移目标右节点
def down_catalog_pre_right(**kwargs):
    where = {}
    where["right_id__gt"] = kwargs["right_id"]
    where["right_id__lte"] = kwargs["next_right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    step = kwargs['right_id'] - kwargs['left_id'] + kwargs['step']
    Comment.objects.filter(**where).update(right_id=F("right_id") - step)


# 更新下移左节点
def down_catalog_cur_left(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["left_id__gte"] = kwargs["left_id"]
    where["right_id__lte"] = kwargs["right_id"]
    step = kwargs["next_right_id"] - kwargs["next_left_id"] + kwargs["step"]
    Comment.objects.filter(**where).update(left_id=F("left_id") + step)


# 更新下移右节点
def down_catalog_cur_right(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["left_id"] + (kwargs["next_right_id"] - kwargs["next_left_id"] + kwargs["step"])
    where["right_id__lte"] = kwargs["right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    step = kwargs["next_right_id"] - kwargs["next_left_id"] + kwargs["step"]
    Comment.objects.filter(**where).update(right_id=F("right_id") + step)


# 移动到底部
def downdate_up_current(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["org_left_id"]
    where["right_id__lte"] = kwargs["org_right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Comment.objects.filter(**where).update(left_id=F("left_id") + kwargs["step"], right_id=F("right_id") + kwargs["step"])


# 移动到底部, 同级需要移动修改
def downdate_up_same_level(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["org_right_id"]
    where["left_id__lte"] = kwargs["target_right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Comment.objects.filter(**where).exclude(id__in=kwargs["ids"]).update(left_id=F("left_id") -
                                                                         kwargs["level_step"], right_id=F("right_id") - kwargs["level_step"])


# 移动到顶部
def update_up_current(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["right_id__lte"] = kwargs["org_right_id"]
    where["left_id__gte"] = kwargs["org_left_id"]
    Comment.objects.filter(**where).update(left_id=F("left_id") - kwargs["step"], right_id=F("right_id") - kwargs["step"])


# 移动到底部, 同级需要移动修改
def update_up_same_level(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["left_id__gte"] = kwargs["target_left_id"]
    where["left_id__lt"] = kwargs["org_left_id"]
    Comment.objects.filter(**where).exclude(id__in=kwargs["ids"]).update(left_id=F("left_id") +
                                                                         kwargs["level_step"], right_id=F("right_id") + kwargs["level_step"])


# 删除节点和其子节点
def delete_son(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["left_id"]
    where["right_id__lte"] = kwargs["right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Comment.objects.filter(**where).delete()


# 修改删除节点左节点
def delete_modify_left(**kwargs):
    where = {}
    where["left_id__gt"] = kwargs["left_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Comment.objects.filter(**where).update(left_id=F("left_id") - (kwargs["right_id"] - kwargs["left_id"] + 1))


# 修改删除节点右节点
def delete_modify_right(**kwargs):
    where = {}
    where["right_id__gt"] = kwargs["right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Comment.objects.filter(**where).update(right_id=F("right_id") - (kwargs["right_id"] - kwargs["left_id"] + 1))


# 获取本级到顶级数据
def track(**kwargs):
    where = {}
    where["left_id__lte"] = kwargs["left_id"]
    where["right_id__gte"] = kwargs["right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Comment.objects.filter(**where).order_by("left_id")
