from rest_framework.response import Response
from rest_framework.decorators import api_view
from community.utils.workspace_util import WorkspaceUtil
from user.repository import message as messageRepository
from user.repository import article as articleRepository
from user import settings as user_settings
from community.decorate.authentication import authentication
from user.serializers import MessageSerializers


@api_view(["GET"])
@authentication(sign=True)
def list(request):
    workspace = WorkspaceUtil.get_workspace(request)
    if not workspace:
        return Response({"status": 401, "msg": "token过期"})
    passport_id = workspace.passport_id
    kwargs = {"passport_id": passport_id}

    data = request.data
    if data.get("status"):
        kwargs["status"] = data["status"]

    page = user_settings.page
    page_size = user_settings.pageSize
    if data.get("page"):
        page = data["page"]
    if data.get("page_size"):
        page_size = data["page_size"]

    count = messageRepository.count(**kwargs)
    messages = messageRepository.search(page_size, page, **kwargs)
    # 获取文章信息
    article_ids = []
    for item in messages:
        if item.article_id not in article_ids:
            article_ids.append(item.article_id)

    article_dict = {}
    if len(article_ids) > 0:
        kwargs = {"ids": article_ids}
        articles = articleRepository.search(**kwargs)
        for item in articles:
            article_dict[item.id] = item

    messages = MessageSerializers(messages, many=True).data
    for item in messages:
        article = article_dict[item["article_id"]]
        item["catalog_id"] = article.catalog_id
        item["article_title"] = article.title

    ret_data = {"data": messages, "count": count}

    return Response({"status": 200, "data": ret_data})


# 获取未读消息总数
@api_view(["GET"])
@authentication(sign=True)
def unread(request):
    workspace = WorkspaceUtil.get_workspace(request)
    if not workspace:
        return Response({"status": 401, "msg": "token过期"})
    passport_id = workspace.passport_id
    kwargs = {"passport_id": passport_id, "status": 0}

    count = messageRepository.count(**kwargs)

    return Response({"status": 200, "data": count})
