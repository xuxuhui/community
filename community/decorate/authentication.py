from rest_framework.response import Response
from django.core.cache import cache
from user.repository import token as tokenRepository
from user import settings
from user.models import Token
from community.utils.time_util import TimeUtil
from community.utils.workspace_util import WorkspaceUtil


# 接口认证装饰器, 接口上都加这个装饰器就可以自动更新登录过期时间
def authentication(sign=False):

    def _deco(func):
        def __deco(request):
            token = request.META.get("HTTP_AUTHORIZATION")
            if sign:
                if not token:
                    return Response({"status": 401, "msg": "请先登录"})

                # 先从缓存获取token是否存在
                token = token.split(" ")[1]
                token_info = cache.get(token)
                if not token_info:
                    # 从数据库查询
                    kwargs = {}
                    kwargs["token_id"] = token
                    token_info = tokenRepository.load(**kwargs)
                    if not token_info or token_info.expire_time < TimeUtil.get_utc_time():
                        return Response({"status": 401, "msg": "请先登录"})
                    expire_time = settings.webExpireTime
                    if token_info.login_type == Token.LoginType.app.value:
                        expire_time = settings.appExpireTime
                    token_info.start_time = TimeUtil.get_utc_time()
                    token_info.expire_time = TimeUtil.get_utc_time() + expire_time
                    token_info.save()

                    workspace = WorkspaceUtil.get_workspace_by_token(
                        token_info)

                    cache.set(token_info.token_id,
                              workspace, timeout=expire_time)
                else:
                    # 更新缓存过期时间
                    expire_time = settings.webExpireTime
                    if token_info.login_type == Token.LoginType.app.value:
                        expire_time = settings.appExpireTime
                    token_info.expire_time = TimeUtil.get_utc_time() + expire_time
                    token_info.start_time = TimeUtil.get_utc_time()
                    cache.set(token, token_info, timeout=expire_time)

                result = signature(request)
                if not result:
                    return Response({"status": 401, "msg": "签名错误"})

            else:
                # 不需要登录的接口 更新token过期时间
                if token:
                    token = token.split(" ")[1]
                    token_info = cache.get(token)
                    if not token_info:
                        # 从数据库查询, 如果存在更新过期时间
                        kwargs = {}
                        kwargs["token_id"] = token
                        token_info = tokenRepository.load(**kwargs)
                        if token_info:
                            # 判断token 是否过期
                            if token_info.expire_time > TimeUtil.get_utc_time():
                                print(11111)
                                expire_time = settings.webExpireTime
                                if token_info.login_type == Token.LoginType.app.value:
                                    expire_time = settings.appExpireTime
                                token_info.start_time = TimeUtil.get_utc_time()
                                token_info.expire_time = TimeUtil.get_utc_time() + expire_time
                                token_info.save()
                                workspace = WorkspaceUtil.get_workspace_by_token(
                                    token_info)
                                cache.set(token_info.token_id,
                                          workspace, timeout=expire_time)
                            else:
                                print(22222)

            return func(request)

        return __deco
    return _deco


# 接口签名认证方法
def signature(request):
    # TODO 签名认证方法实现
    return True
