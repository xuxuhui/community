from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import transaction
from .repository import catalog as catalogRepository
from .models import Catalog
from community.utils.time_util import TimeUtil
from community.decorate.authentication import authentication


# Create your views here.


# 新增分类
@api_view(['POST'])
@transaction.atomic(using='pet')
@authentication(sign=True)
def create_catalog(request):
    data = request.data
    parent_id = data.get('parent_id', 0)
    catalog_type = data.get("catalog_type")
    name = data.get("name")
    if not (catalog_type and name):
        return Response({"status": 400, "msg": "参数错误"})
    utc_time = TimeUtil.get_utc_time()
    if parent_id == 0:
        # 判断是否有根节点存在
        kwargs = {}
        kwargs["layer"] = 0
        kwargs["catalog_type"] = catalog_type
        catalog_res = catalogRepository.load(**kwargs)
        # 根节点不存在 先创建一个根节点
        if not catalog_res:
            catalog = Catalog()
            catalog.parent_id = 0
            catalog.layer = 0
            catalog.left_id = 1
            catalog.right_id = 4
            catalog.name = ""
            catalog.catalog_type = catalog_type
            catalog.version = 1
            catalog.created = utc_time
            catalog.save()
            catalog_id = catalog.id

            catalog1 = Catalog()
            catalog1.parent_id = catalog_id
            catalog1.layer = 1
            catalog1.left_id = 2
            catalog1.right_id = 3
            catalog1.name = name
            catalog1.icon = data.get("icon")
            catalog1.code = data.get("code")
            catalog1.catalog_type = catalog_type
            catalog1.version = 1
            catalog1.created = utc_time
            catalog1.save()

        else:
            # 更新需要更新的左节点
            kwargs = {}
            kwargs["catalog_type"] = catalog_type
            kwargs["right_id"] = catalog_res.right_id
            catalogRepository.update_left_id(**kwargs)

            # 更新需要更新的右节点
            catalogRepository.update_right_id(**kwargs)

            parent_id = catalog_res.id
            catalog = Catalog()
            catalog.parent_id = parent_id
            catalog.layer = catalog_res.layer + 1
            catalog.left_id = catalog_res.right_id
            catalog.right_id = catalog_res.right_id + 1
            catalog.name = name
            catalog.icon = data.get("icon")
            catalog.code = data.get("code")
            catalog.catalog_type = catalog_type
            catalog.version = 1
            catalog.created = utc_time
            catalog.save()

    else:
        # 新增节点
        kwargs = {}
        kwargs["id"] = parent_id
        catalog_res = catalogRepository.load(**kwargs)
        # 更新需要更新的左节点
        kwargs = {}
        kwargs["catalog_type"] = catalog_res.catalog_type
        kwargs["right_id"] = catalog_res.right_id
        catalogRepository.update_left_id(**kwargs)

        # 更新需要更新的右节点
        catalogRepository.update_right_id(**kwargs)

        catalog = Catalog()
        catalog.parent_id = parent_id
        catalog.layer = catalog_res.layer + 1
        catalog.left_id = catalog_res.right_id
        catalog.right_id = catalog_res.right_id + 1
        catalog.name = name
        catalog.icon = data.get("icon")
        catalog.code = data.get("code")
        catalog.catalog_type = catalog_res.catalog_type
        catalog.version = 1
        catalog.created = utc_time
        catalog.save()

    return Response({"status": 200, "msg": "新增分类成功"})


# 同级上移分类
@api_view(["POST"])
@transaction.atomic(using='pet')
@authentication(sign=True)
def move_up(request):
    data = request.data
    # 要移动id
    if not data.get("id"):
        return Response({"status": 400, "msg": "参数错误"})
    kwargs = {}
    kwargs["id"] = data["id"]
    catalog = catalogRepository.load(**kwargs)
    if not catalog:
        return Response({"status": 404, "msg": "分类不存在"})
    kwargs = {}
    kwargs["left_id"] = catalog.left_id
    kwargs["layer"] = catalog.layer
    kwargs["catalog_type"] = catalog.catalog_type
    to_catalog = catalogRepository.find_up_catalog(**kwargs)
    if not to_catalog:
        return Response({"status": 400, "msg": "已经是最上层节点"})

    step = catalog.left_id - to_catalog.right_id
    kwargs = {}
    kwargs["step"] = step
    kwargs["pre_right_id"] = to_catalog.right_id
    kwargs["pre_left_id"] = to_catalog.left_id
    kwargs["left_id"] = catalog.left_id
    kwargs["right_id"] = catalog.right_id
    kwargs["catalog_type"] = catalog.catalog_type

    catalogRepository.up_catalog_pre_left(**kwargs)
    catalogRepository.up_catalog_cur_left(**kwargs)
    catalogRepository.up_catalog_pre_right(**kwargs)
    catalogRepository.up_catalog_cur_right(**kwargs)

    return Response({"status": 200, "msg": "上移成功"})


# 同级下移分类
@api_view(["POST"])
@transaction.atomic(using='pet')
@authentication(sign=True)
def move_down(request):
    data = request.data
    # 要移动的id
    if not data.get("id"):
        return Response({"status": 400, "msg": "参数错误"})
    kwargs = {}
    kwargs["id"] = data["id"]
    catalog = catalogRepository.load(**kwargs)
    if not catalog:
        return Response({"status": 404, "msg": "分类不存在"})
    kwargs = {}
    kwargs["right_id"] = catalog.right_id
    kwargs["catalog_type"] = catalog.catalog_type
    kwargs["layer"] = catalog.layer
    to_catalog = catalogRepository.find_next_catalog(**kwargs)
    if not to_catalog:
        return Response({"status": 400, "msg": "已经是最下层节点"})

    step = to_catalog.left_id - catalog.right_id
    kwargs = {}
    kwargs["step"] = step
    kwargs["next_right_id"] = to_catalog.right_id
    kwargs["next_left_id"] = to_catalog.left_id
    kwargs["left_id"] = catalog.left_id
    kwargs["right_id"] = catalog.right_id
    kwargs["catalog_type"] = catalog.catalog_type

    catalogRepository.down_catalog_pre_left(**kwargs)
    catalogRepository.down_catalog_cur_left(**kwargs)
    catalogRepository.down_catalog_pre_right(**kwargs)
    catalogRepository.down_catalog_cur_right(**kwargs)

    return Response({"status": 200, "msg": "下移成功"})


# 移到底部
@api_view(["POST"])
@transaction.atomic(using='pet')
@authentication(sign=True)
def bottom(request):
    data = request.data
    if not data.get("id"):
        return Response({"status": 400, "msg": "参数错误"})
    kwargs = {}
    kwargs["id"] = data["id"]
    catalog = catalogRepository.load(**kwargs)
    if not catalog:
        return Response({"status": 404, "msg": "分类不存在"})

    # 获取底部节点
    kwargs = {}
    kwargs["catalog_type"] = catalog.catalog_type
    kwargs["parent_id"] = catalog.parent_id
    catalog_list = catalogRepository.search(limit=500, page=1, **kwargs)
    bottom_catalog = catalog_list[len(catalog_list) - 1]

    # 获取要移动的子节点
    kwargs = {}
    kwargs["left_id"] = catalog.left_id
    kwargs["right_id"] = catalog.right_id
    kwargs["catalog_type"] = catalog.catalog_type
    to_move_catalogs = catalogRepository.find_move_son(**kwargs)

    step = bottom_catalog.right_id - catalog.right_id
    level_step = catalog.right_id - catalog.left_id + 1
    ids = []
    for item in to_move_catalogs:
        ids.append(item.id)
    kwargs = {}
    kwargs["step"] = step
    kwargs["level_step"] = level_step
    kwargs['org_right_id'] = catalog.right_id
    kwargs['org_left_id'] = catalog.left_id
    kwargs['target_right_id'] = bottom_catalog.right_id
    kwargs["ids"] = ids
    kwargs["catalog_type"] = catalog.catalog_type

    catalogRepository.downdate_up_current(**kwargs)
    catalogRepository.downdate_up_same_level(**kwargs)

    return Response({"status": 200, "msg": "移动到底部成功"})


# 移到顶部
@api_view(["POST"])
@transaction.atomic(using='pet')
@authentication(sign=True)
def top(request):
    data = request.data
    if not data.get("id"):
        return Response({"status": 400, "msg": "参数错误"})
    kwargs = {}
    kwargs["id"] = data["id"]
    catalog = catalogRepository.load(**kwargs)
    if not catalog:
        return Response({"status": 404, "msg": "分类不存在"})

    # 获取顶部节点
    kwargs = {}
    kwargs["catalog_type"] = catalog.catalog_type
    kwargs["parent_id"] = catalog.parent_id
    catalog_list = catalogRepository.search(limit=500, page=1, **kwargs)
    top_catalog = catalog_list[0]

    # 获取待移动子节点
    kwargs = {}
    kwargs["catalog_type"] = catalog.catalog_type
    kwargs["left_id"] = catalog.left_id
    kwargs["right_id"] = catalog.right_id
    catalog_list = catalogRepository.find_move_son(**kwargs)

    step = catalog.left_id - top_catalog.left_id
    level_step = catalog.right_id - catalog.left_id + 1
    ids = []
    for item in catalog_list:
        ids.append(item.id)

    kwargs = {}
    kwargs["step"] = step
    kwargs["level_step"] = level_step
    kwargs["org_right_id"] = catalog.right_id
    kwargs["org_left_id"] = catalog.left_id
    kwargs["target_left_id"] = top_catalog.left_id
    kwargs["ids"] = ids
    kwargs["catalog_type"] = catalog.catalog_type

    catalogRepository.update_up_current(**kwargs)
    catalogRepository.update_up_same_level(**kwargs)

    return Response({"status": 200, "msg": "移动到顶部成功"})


# 删除分类
@api_view(["POST"])
@transaction.atomic(using='pet')
@authentication(sign=True)
def delete(request):
    data = request.data
    if not data.get("id"):
        return Response({"status": 400, "msg": "参数错误"})

    kwargs = {}
    kwargs["id"] = data["id"]
    catalog = catalogRepository.load(**kwargs)
    if not catalog:
        return Response({"status": 200, "msg": "删除成功"})
    kwargs = {}
    kwargs["left_id"] = catalog.left_id
    kwargs["right_id"] = catalog.right_id
    kwargs["catalog_type"] = catalog.catalog_type

    catalogRepository.delete_son(**kwargs)
    catalogRepository.delete_modify_left(**kwargs)
    catalogRepository.delete_modify_right(**kwargs)

    return Response({"status": 200, "msg": "删除成功"})


# 修改分类
@api_view(["POST"])
@transaction.atomic(using='pet')
@authentication(sign=True)
def modify_catalog(request):
    data = request.data
    if not data.get("id"):
        return Response({"status": 400, "msg": "参数错误"})
    kwargs = {}
    kwargs["id"] = data["id"]
    catalog = catalogRepository.load(**kwargs)
    if not catalog:
        return Response({"status": 404, "msg": "分类不存在"})
    catalog.name = data.get("name")
    catalog.save()

    return Response({"status": 200, "msg": "修改成功"})


# 宠物介绍新增
def create(request):
    pass


# 宠物介绍修改
def modify(request):
    pass


# 宠物介绍删除
def deleted(request):
    pass
