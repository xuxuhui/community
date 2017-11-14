from pet.models import Catalog
from pet import settings
from .base import get_object
from django.db.models import F


def search(limit=settings.pageSize, page=settings.page, **kwargs):
    offset = limit * (int(page) - 1)
    size = limit * int(page)
    where = {}
    if kwargs.get("parent_id"):
        where["parent_id"] = kwargs["parent_id"]
    if kwargs.get("catalog_type"):
        where["catalog_type"] = kwargs["catalog_type"]
    catalog_list = Catalog.objects.filter(**where).order_by("`left_id")[offset:size]

    return catalog_list


def load(**kwargs):
    where = {}
    if kwargs.get("parent_id"):
        where["parent_id"] = kwargs["parent_id"]
    if kwargs.get("catalog_type"):
        where["catalog_type"] = kwargs["catalog_type"]
    if kwargs.get("id"):
        where["id"] = kwargs["id"]
    if "layer" in kwargs:
        where["layer"] = kwargs["layer"]
    catalog_list = Catalog.objects.filter(**where)
    catalog = get_object(catalog_list)

    return catalog


# 新增时需要更新的左节点
def update_left_id(**kwargs):
    where = {}
    if kwargs.get("right_id"):
        where["left_id__gte"] = kwargs["right_id"]
    if kwargs.get("catalog_type"):
        where["catalog_type"] = kwargs["catalog_type"]
    Catalog.objects.filter(**where).update(left_id=F('left_id') + 2)


# 新增时需要更新的右节点
def update_right_id(**kwargs):
    where = {}
    if kwargs.get("right_id"):
        where["right_id__gte"] = kwargs["right_id"]
    if kwargs.get("catalog_type"):
        where["catalog_type"] = kwargs["catalog_type"]

    Catalog.objects.filter(**where).update(right_id=F('right_id') + 2)


# 查找同级上一个节点
def find_up_catalog(**kwargs):
    where = {}
    if kwargs.get("layer"):
        where["layer"] = kwargs["layer"]
    if kwargs.get("left_id"):
        where["right_id__lt"] = kwargs["left_id"]
    if kwargs.get("catalog_type"):
        where["catalog_type"] = kwargs["catalog_type"]
    catalog_list = Catalog.objects.filter(**where).order_by("-left_id")[:1]
    catalog = get_object(catalog_list)

    return catalog


# 查找同级下一个节点
def find_next_catalog(**kwargs):
    where = {}
    where["left_id__gt"] = kwargs["right_id"]
    where["layer"] = kwargs["layer"]
    where["catalog_type"] = kwargs["catalog_type"]
    catalog_list = Catalog.objects.filter(**where).order_by("left_id")[:1]
    catalog = get_object(catalog_list)

    return catalog


# 查找需要移动子节点
def find_move_son(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["left_id"]
    where["right_id__lte"] = kwargs["right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    catalog_list = Catalog.objects.filter(**where).order_by("left_id")

    return catalog_list


# 更新上移目标左节点
def up_catalog_pre_left(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["left_id__gte"] = kwargs["left_id"]
    where["right_id__lte"] = kwargs["right_id"]
    step = kwargs["pre_right_id"] - kwargs["pre_left_id"] + kwargs["step"]
    Catalog.objects.filter(**where).update(left_id=F("left_id") - step)


# 更新上移目标右节点
def up_catalog_pre_right(**kwargs):
    where = {}
    where["right_id__gt"] = kwargs["pre_right_id"]
    where["right_id__lte"] = kwargs["right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    step = kwargs['pre_right_id'] - kwargs['pre_left_id'] + kwargs['step']
    Catalog.objects.filter(**where).update(right_id=F("right_id") - step)


# 更新上移左节点
def up_catalog_cur_left(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["left_id__gte"] = kwargs["pre_left_id"]
    where["right_id__lte"] = kwargs["pre_right_id"]
    step = kwargs["right_id"] - kwargs["left_id"] + kwargs["step"]
    Catalog.objects.filter(**where).update(left_id=F("left_id") + step)


# 更新上移右节点
def up_catalog_cur_right(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["pre_left_id"] + (kwargs["right_id"] - kwargs["left_id"] + kwargs["step"])
    where["right_id__lte"] = kwargs["pre_right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    step = kwargs["right_id"] - kwargs["left_id"] + kwargs["step"]
    Catalog.objects.filter(**where).update(right_id=F("right_id") + step)


# 更新下移目标左节点
def down_catalog_pre_left(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["left_id__gte"] = kwargs["next_left_id"]
    where["right_id__lte"] = kwargs["next_right_id"]
    step = kwargs["right_id"] - kwargs["left_id"] + kwargs["step"]
    Catalog.objects.filter(**where).update(left_id=F("left_id") - step)


# 更新下移目标右节点
def down_catalog_pre_right(**kwargs):
    where = {}
    where["right_id__gt"] = kwargs["right_id"]
    where["right_id__lte"] = kwargs["next_right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    step = kwargs['right_id'] - kwargs['left_id'] + kwargs['step']
    Catalog.objects.filter(**where).update(right_id=F("right_id") - step)


# 更新下移左节点
def down_catalog_cur_left(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["left_id__gte"] = kwargs["left_id"]
    where["right_id__lte"] = kwargs["right_id"]
    step = kwargs["next_right_id"] - kwargs["next_left_id"] + kwargs["step"]
    Catalog.objects.filter(**where).update(left_id=F("left_id") + step)


# 更新下移右节点
def down_catalog_cur_right(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["left_id"] + (kwargs["next_right_id"] - kwargs["next_left_id"] + kwargs["step"])
    where["right_id__lte"] = kwargs["right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    step = kwargs["next_right_id"] - kwargs["next_left_id"] + kwargs["step"]
    Catalog.objects.filter(**where).update(right_id=F("right_id") + step)


# 移动到底部
def downdate_up_current(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["org_left_id"]
    where["right_id__lte"] = kwargs["org_right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Catalog.objects.filter(**where).update(left_id=F("left_id") + kwargs["step"], right_id=F("right_id") + kwargs["step"])


# 移动到底部, 同级需要移动修改
def downdate_up_same_level(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["org_right_id"]
    where["left_id__lte"] = kwargs["target_right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Catalog.objects.filter(**where).exclude(id__in=kwargs["ids"]).update(left_id=F("left_id") -
                                                                         kwargs["level_step"], right_id=F("right_id") - kwargs["level_step"])


# 移动到顶部
def update_up_current(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["right_id__lte"] = kwargs["org_right_id"]
    where["left_id__gte"] = kwargs["org_left_id"]
    Catalog.objects.filter(**where).update(left_id=F("left_id") - kwargs["step"], right_id=F("right_id") - kwargs["step"])


# 移动到底部, 同级需要移动修改
def update_up_same_level(**kwargs):
    where = {}
    where["catalog_type"] = kwargs["catalog_type"]
    where["left_id__gte"] = kwargs["target_left_id"]
    where["left_id__lt"] = kwargs["org_left_id"]
    Catalog.objects.filter(**where).exclude(id__in=kwargs["ids"]).update(left_id=F("left_id") +
                                                                         kwargs["level_step"], right_id=F("right_id") + kwargs["level_step"])


# 删除节点和其子节点
def delete_son(**kwargs):
    where = {}
    where["left_id__gte"] = kwargs["left_id"]
    where["right_id__lte"] = kwargs["right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Catalog.objects.filter(**where).delete()


# 修改删除节点左节点
def delete_modify_left(**kwargs):
    where = {}
    where["left_id__gt"] = kwargs["left_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Catalog.objects.filter(**where).update(left_id=F("left_id") - (kwargs["right_id"] - kwargs["left_id"] + 1))


# 修改删除节点右节点
def delete_modify_right(**kwargs):
    where = {}
    where["right_id__gt"] = kwargs["right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Catalog.objects.filter(**where).update(right_id=F("right_id") - (kwargs["right_id"] - kwargs["left_id"] + 1))


# 获取本级到顶级数据
def track(**kwargs):
    where = {}
    where["left_id__lte"] = kwargs["left_id"]
    where["right_id__gte"] = kwargs["right_id"]
    where["catalog_type"] = kwargs["catalog_type"]
    Catalog.objects.filter(**where).order_by("left_id")
