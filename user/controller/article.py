from rest_framework.response import Response
from django.db import transaction
from rest_framework.decorators import api_view
from community.utils.time_util import TimeUtil
from community.utils.workspace_util import WorkspaceUtil
from user.models import Article, Collect
from user.repository import article as articleRepository
from user.repository import passport as passportRepository
from user.repository import catalog as catalogRepository
from user.repository import comment as commentRepository
from user.repository import collect as collectRepository
from user import settings as user_settings
from community.decorate.authentication import authentication
from user.serializers import ArticleSerializers


# 新增文章
@api_view(["POST"])
@authentication(sign=True)
def create(request):
    data = request.data
    workspace = WorkspaceUtil.get_workspace(request)
    if not workspace:
        return Response({"status": 401, "msg": "token过期"})
    if not data.get("catalog_id"):
        return Response({"status": 400, "msg": "参数错误"})

    kwargs = {}
    kwargs["id"] = data["catalog_id"]
    catalog = catalogRepository.load(**kwargs)
    if not catalog:
        return Response({"status": 404, "msg": "类目不存在"})

    article = Article()
    article.passport_id = workspace.passport_id
    article.passport_name = workspace.name
    article.catalog_id = data.get("catalog_id")
    article.catalog_name = catalog.name
    article.title = data.get("title")
    article.content = data.get("content")
    article.created = TimeUtil.get_utc_time()
    article.pv = 0
    article.version = 1
    article.save()

    return Response({"status": 200, "msg": "新增成功"})


# 获取文章详情
@api_view(["GET"])
def detail(request):
    data = request.GET
    if not data.get("id"):
        return Response({"status": 400, "msg": "参数错误"})
    kwargs = {}
    kwargs["id"] = data["id"]
    article = articleRepository.load(**kwargs)
    if not article:
        return Response({"status": 404, "msg": "文章不存在"})

    # 获取 passport
    kwargs = {}
    kwargs["id"] = article.passport_id
    passport = passportRepository.load(**kwargs)

    article = ArticleSerializers(article).data
    if (passport):
        article["passport_name"] = passport.name
        article["avert"] = passport.avert

    workspace = WorkspaceUtil.get_workspace(request)
    article["is_collect"] = False
    if workspace:
        passport_id = workspace.passport_id
        kwargs = {"passport_id": passport_id, "article_id": data["id"]}
        collect = collectRepository.load(**kwargs)
        if collect:
            article["is_collect"] = True

    return Response({"status": 200, "data": article})


# 获取文章列表
@api_view(["GET"])
def list(request):
    data = request.GET
    kwargs = {}
    if data.get("catalog_id"):
        kwargs["catalog_id"] = data["catalog_id"]
    if data.get("order_by"):
        kwargs["order_by"] = data["order_by"]
    # 获取自己文章列表
    if data.get("owner"):
        workspace = WorkspaceUtil.get_workspace(request)
        if not workspace:
            return Response({"status": 401, "msg": "token过期"})
        passport_id = workspace.passport_id
        kwargs["passport_id"] = passport_id
    if data.get("passport_id"):
        kwargs["passport_id"] = data["passport_id"]

    page = user_settings.page
    page_size = user_settings.pageSize
    if data.get("page"):
        page = data["page"]
    if data.get("page_size"):
        page_size = data["page_size"]

    passport_ids = []
    article_list = articleRepository.search(page_size, page, **kwargs)
    article_ids = []
    for item in article_list:
        article_ids.append(item.id)
        passport_ids.append(item.passport_id)

    # 获取一次用户对象
    where = {}
    where["id__in"] = passport_ids
    passport_list = passportRepository.search(page_size, 1, **where)
    passport_dict = {}
    for item in passport_list:
        if item.id not in passport_dict:
            passport_dict[item.id] = item

    # 获取文章评论量
    comment_dict = {}
    if article_ids:
        where = {}
        where["article_id__in"] = article_ids
        comment_list = commentRepository.group(**where)
        for item in comment_list:
            comment_dict[item["article_id"]] = item["count"]

    count = articleRepository.count(**kwargs)
    article_list = ArticleSerializers(article_list, many=True).data
    for item in article_list:
        passport = passport_dict.get(item["passport_id"])
        item["reply"] = comment_dict.get(item["id"], 0)
        if passport:
            item["passport_name"] = passport.name
            item["avert"] = passport.avert
        else:
            item["passport_name"] = ""
            item["avert"] = ""
        del item["content"]

    response_data = {"data": article_list, "count": count}

    return Response({"status": 200, "data": response_data})


# 删除文章, 相关评论, 相关收藏
@api_view(["POST"])
@authentication(sign=True)
@transaction.atomic(using='users')
def deleted(request):
    data = request.data
    if not data.get("id"):
        return Response({"status": 400, "msg": "参数错误"})
    id = data.get("id")
    kwargs = {}
    kwargs["id"] = id
    article = articleRepository.load(**kwargs)
    if not article:
        return Response({"status": 200, "msg": "删除成功"})
    article.delete()

    # 删除相关评论
    kwargs = {}
    kwargs["article_id"] = id
    articleRepository.delete_comment(**kwargs)

    # TODO 删除相关收藏文章

    return Response({"status": 200, "msg": "删除成功"})


# 文章浏览量增加
@api_view(["POST"])
def add_pv(request):
    data = request.data
    if not data.get("article_id"):
        return Response({"status": 400, "msg": "参数错误"})
    where = {"id": data["article_id"]}

    articleRepository.update_pv(**where)

    return Response({"status": 200, "msg": ""})


# 收藏文章
@api_view(["POST"])
@authentication(sign=True)
def collect(request):
    data = request.data
    if not data.get("article_id"):
        return Response({"status": 400, "msg": "参数错误"})

    workspace = WorkspaceUtil.get_workspace(request)
    if not workspace:
        return Response({"status": 401, "msg": "token过期"})

    article_id = data["article_id"]
    passport_id = workspace.passport_id
    kwargs = {"article_id": article_id, "passport_id": passport_id}
    collect = collectRepository.load(**kwargs)
    if collect:
        return Response({"status": 400, "msg": "已收藏"})

    utc_time = TimeUtil.get_utc_time()
    collect = Collect(article_id=article_id,
                      passport_id=passport_id, created=utc_time)
    collect.save()

    return Response({"status": 200, "msg": "收藏文章成功"})


# 取消收藏文章
@api_view(["POST"])
@authentication(sign=True)
def cancel_collect(request):
    data = request.data
    if not data.get("article_id"):
        return Response({"status": 400, "msg": "参数错误"})

    workspace = WorkspaceUtil.get_workspace(request)
    if not workspace:
        return Response({"status": 401, "msg": "token过期"})

    article_id = data["article_id"]
    passport_id = workspace.passport_id
    kwargs = {"article_id": article_id, "passport_id": passport_id}
    collect = collectRepository.load(**kwargs)
    if not collect:
        return Response({"status": 400, "msg": "取消收藏文章成功"})

    collectRepository.delete(**kwargs)

    return Response({"status": 200, "msg": "取消收藏文章成功"})


# 收藏文章列表
@api_view(["GET"])
@authentication(sign=True)
def collect_list(request):
    data = request.GET
    page = user_settings.page
    page_size = user_settings.pageSize
    if data.get("page"):
        page = data["page"]
    if data.get("page_size"):
        page_size = data["page_size"]

    workspace = WorkspaceUtil.get_workspace(request)
    if not workspace:
        return Response({"status": 401, "msg": "token过期"})

    passport_id = workspace.passport_id
    kwargs = {"passport_id": passport_id}
    collect_list = collectRepository.search(page_size, page, **kwargs)
    article_ids = []
    for item in collect_list:
        article_ids.append(item.article_id)

    # 获取文章列表
    article_list = []
    if len(article_ids) > 0:
        # 获取文章评论量
        comment_dict = {}
        if article_ids:
            where = {}
            where["article_id__in"] = article_ids
            comment_list = commentRepository.group(**where)
            for item in comment_list:
                comment_dict[item["article_id"]] = item["count"]

        kwargs = {"ids": article_ids}
        article_list = articleRepository.search(**kwargs)
        article_list = ArticleSerializers(article_list, many=True).data

        for item in article_list:
            item["reply"] = comment_dict.get(item["id"], 0)

    count = collectRepository.count(**kwargs)

    return Response({"status": 200, "msg": "", "data": {"count": count, "data": article_list}})
