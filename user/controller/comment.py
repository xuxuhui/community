from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import transaction
from community.utils.time_util import TimeUtil
from community.utils.workspace_util import WorkspaceUtil
from user.models import Comment, CommentFavour, Message
from user import settings as user_settings
from user.repository import comment as commentRepository
from user.repository import passport as passportRepository
from user.repository import comment_favour as commentFavourRepository
from user.repository import article as articleRepository
from user.serializers import CommentSerializers
from community.decorate.authentication import authentication


# 添加评论
@api_view(["POST"])
@transaction.atomic(using='users')
@authentication(sign=True)
def add_comment(request):
    data = request.data
    parent_id = data.get('parent_id', 0)
    content = data.get("content")
    article_id = data.get("article_id")
    if not (content and article_id):
        return Response({"status": 400, "msg": "参数错误"})

    kwargs = {"id": article_id}
    article = articleRepository.load(**kwargs)
    if not article:
        return Response({"status": 400, "msg": "文章不存在"})

    utc_time = TimeUtil.get_utc_time()
    catalog_type = data.get("catalog_type")
    workspace = WorkspaceUtil.get_workspace(request)
    passport_id = workspace.passport_id

    message = Message()
    message.reply_id = passport_id
    message.reply_name = workspace.name
    message.passport_id = article.passport_id
    message.article_id = article.id
    message.article_title = article.title
    message.created = utc_time
    message.status = 0
    message.reply_type = Message.Type.reply.value
    flag = True

    if parent_id == 0:
        message.reply_type = Message.Type.answer.value
        if article.passport_id == passport_id:
            flag = False
        # 判断是否有根节点存在
        kwargs = {}
        kwargs["layer"] = 0
        kwargs["article_id"] = article_id
        catalog_res = commentRepository.load(**kwargs)
        # 根节点不存在 先创建一个根节点
        if not catalog_res:
            catalog = Comment()
            catalog.passport_id = passport_id
            catalog.parent_id = 0
            catalog.layer = 0
            catalog.left_id = 1
            catalog.right_id = 4
            catalog.content = ""
            catalog.catalog_type = catalog_type
            catalog.version = 1
            catalog.created = utc_time
            catalog.article_id = article_id
            catalog.save()
            catalog_id = catalog.id

            catalog = Comment()
            catalog.parent_id = catalog_id
            catalog.layer = 1
            catalog.left_id = 2
            catalog.right_id = 3
            catalog.content = data["content"]
            catalog.passport_id = passport_id
            catalog.catalog_type = catalog_type
            catalog.article_id = article_id
            catalog.version = 1
            catalog.created = utc_time
            catalog.save()

        else:
            # 更新需要更新的左节点
            kwargs = {}
            kwargs["catalog_type"] = catalog_type
            kwargs["right_id"] = catalog_res.right_id
            commentRepository.update_left_id(**kwargs)

            # 更新需要更新的右节点
            commentRepository.update_right_id(**kwargs)

            parent_id = catalog_res.id
            catalog = Comment()
            catalog.parent_id = parent_id
            catalog.layer = catalog_res.layer + 1
            catalog.left_id = catalog_res.right_id
            catalog.right_id = catalog_res.right_id + 1
            catalog.catalog_type = catalog_type
            catalog.passport_id = passport_id
            catalog.article_id = article_id
            catalog.content = data["content"]
            catalog.version = 1
            catalog.created = utc_time
            catalog.save()

    else:
        # 新增节点
        kwargs = {}
        kwargs["id"] = parent_id
        catalog_res = commentRepository.load(**kwargs)
        message.passport_id = catalog_res.passport_id
        if catalog_res.passport_id == passport_id:
            flag = False

        # 更新需要更新的左节点
        kwargs = {}
        kwargs["catalog_type"] = catalog_res.catalog_type
        kwargs["right_id"] = catalog_res.right_id
        commentRepository.update_left_id(**kwargs)

        # 更新需要更新的右节点
        commentRepository.update_right_id(**kwargs)

        catalog = Comment()
        catalog.parent_id = parent_id
        catalog.layer = catalog_res.layer + 1
        catalog.left_id = catalog_res.right_id
        catalog.right_id = catalog_res.right_id + 1
        catalog.passport_id = passport_id
        catalog.article_id = article_id
        catalog.catalog_type = catalog_res.catalog_type
        catalog.content = data["content"]
        catalog.version = 1
        catalog.created = utc_time
        catalog.save()

    catalog = CommentSerializers(catalog).data

    if flag:
        message.save()

    return Response({"status": 200, "msg": "新增评论成功", "data": catalog})


# 获取评论列表
@api_view(["GET"])
@transaction.atomic(using='users')
@authentication(sign=False)
def list(request):
    data = request.GET
    page = user_settings.page
    page_size = user_settings.pageSize
    if data.get("page"):
        page = data["page"]
    if data.get("page_size"):
        page_size = data["page_size"]

    if not data.get("article_id"):
        return Response({"status": 400, "msg": "参数错误"})

    kwargs = {}
    kwargs["article_id"] = data["article_id"]

    comment_list = commentRepository.search(page_size, page, **kwargs)
    # 获取评论人头像, 名字信息, 评论字典
    passport_ids = []
    comment_ids = []
    comment_parents = []
    comment_parents_dict = {}
    for item in comment_list:
        passport_ids.append(item.passport_id)
        comment_ids.append(item.id)
        if item.layer > 1:
            comment_parents.append(item.parent_id)

    # 获取@人信息
    if len(comment_parents) > 0:
        where = {}
        where["comment_id__in"] = comment_parents
        comments = commentRepository.search(page_size, page, **kwargs)
        for item in comments:
            passport_ids.append(item.passport_id)
            comment_parents_dict[item.id] = item.passport_id

    where = {}
    where["id__in"] = passport_ids
    passport_list = passportRepository.search(int(page_size) * 2, 1, **kwargs)
    passport_dict = {}
    for item in passport_list:
        passport_dict[item.id] = item

    # 获取评论量点赞总量
    where = {}
    where["comment_id__in"] = comment_ids
    favor_count = {}
    comment_favour_list = commentFavourRepository.group(**where)
    for item in comment_favour_list:
        favor_count[item["comment_id"]] = item["dcount"]

    # 已点赞id
    favor_ids = []
    # 获取当前用户已点赞评论
    workspace = WorkspaceUtil.get_workspace(request)
    if workspace:
        passport_id = workspace.passport_id
        where["passport_id"] = passport_id
        where["comment_id__in"] = comment_ids
        favour_list = commentFavourRepository.search(page_size, 1, **where)
        for item in favour_list:
            favor_ids.append(item.comment_id)

    comment_list = CommentSerializers(comment_list, many=True).data
    for item in comment_list:
        passport = passport_dict[item["passport_id"]]
        item["favor_count"] = favor_count.get(item["id"], 0)
        item["is_favor"] = False
        if item["id"] in favor_ids:
            item["is_favor"] = True
        if passport:
            item["avert"] = passport.avert
            item["passport_name"] = passport.name
        else:
            item["avert"] = passport.avert
            item["passport_name"] = passport.name
        if item["layer"] > 1:
            reply_passport = passport_dict[comment_parents_dict[item["parent_id"]]]
            item["reply_id"] = reply_passport.id
            item["reply_name"] = reply_passport.name

    count = commentRepository.count(**kwargs)
    response_data = {"count": count, "data": comment_list}

    return Response({"status": 200, "data": response_data})


# 获取简易评论列表
@api_view(["GET"])
@authentication(sign=False)
def reply(request):
    data = request.GET
    page = user_settings.page
    page_size = user_settings.pageSize
    if data.get("page"):
        page = data["page"]
    if data.get("page_size"):
        page_size = data["page_size"]

    if not data.get("passport_id"):
        return Response({"status": 400, "msg": "参数错误"})

    kwargs = {}
    kwargs["passport_id"] = data["passport_id"]

    article_ids = []
    comment_list = commentRepository.search(page_size, page, **kwargs)
    for item in comment_list:
        if item.article_id not in article_ids:
            article_ids.append(item.article_id)

    # 获取文章列表
    article_dict = {}
    if len(article_ids):
        where = {}
        where["ids"] = article_ids
        articles = articleRepository.search(page_size, 1, **where)
        for item in articles:
            article_dict[item.id] = item

    comment_list = CommentSerializers(comment_list, many=True).data
    for item in comment_list:
        article = article_dict[item["article_id"]]
        item["title"] = article.title
        item["article_catalog"] = article.catalog_id

    count = commentRepository.count(**kwargs)
    response_data = {"count": count, "data": comment_list}

    return Response({"status": 200, "data": response_data})


# 给评论点赞
@api_view(["POST"])
@transaction.atomic(using="users")
@authentication(sign=True)
def favor(request):
    data = request.data
    if not data.get("comment_id"):
        return Response({"status": 400, "msg": "参数错误"})
    workspace = WorkspaceUtil.get_workspace(request)
    passport_id = workspace.passport_id

    kwargs = {"id": data["comment_id"]}
    comment = commentRepository.load(**kwargs)
    if not comment:
        return Response({"status": 400, "msg": "该评论不存在"})
    if comment.passport_id == passport_id:
        return Response({"status": 400, "msg": "不能给自己点赞"})

    # 判断该用户点赞
    kwargs = {}
    kwargs["passport_id"] = passport_id
    kwargs["comment_id"] = data["comment_id"]
    comment_favour = commentFavourRepository.load(**kwargs)
    if comment_favour:
        where = {}
        where["comment_id"] = data["comment_id"]
        count = commentFavourRepository.count(**where)
        return Response({"status": 200, "msg": "点赞成功", "data": count})

    # 点赞+1
    comment_favour = CommentFavour(passport_id=passport_id, comment_id=data["comment_id"])
    comment_favour.save()

    # 返回此评论赞
    where = {}
    where["comment_id"] = data["comment_id"]
    count = commentFavourRepository.count(**where)

    return Response({"status": 200, "msg": "点赞成功", "data": count})


# 给评论取消点赞
@api_view(["POST"])
@transaction.atomic(using="users")
@authentication(sign=True)
def cancel_favor(request):
    data = request.data
    if not data.get("comment_id"):
        return Response({"status": 400, "msg": "参数错误"})
    workspace = WorkspaceUtil.get_workspace(request)
    passport_id = workspace.passport_id

    # 判断该用户点赞
    kwargs = {}
    kwargs["passport_id"] = passport_id
    kwargs["comment_id"] = data["comment_id"]
    comment_favour = commentFavourRepository.load(**kwargs)
    if not comment_favour:
        where = {}
        where["comment_id"] = data["comment_id"]
        count = commentFavourRepository.count(**where)
        return Response({"status": 200, "msg": "取消点赞成功", "data": count})
    # 点赞减1
    CommentFavour(passport_id=passport_id, comment_id=data["comment_id"]).delete()

    # 返回此评论赞
    where = {}
    where["comment_id"] = data["comment_id"]
    count = commentFavourRepository.count(**where)

    return Response({"status": 200, "msg": "取消点赞成功", "data": count})
