import uuid
from django.core.cache import cache
from .cryptogram import CryptogramGenerate
from .time_util import TimeUtil
from user.models import Token, Workspace
from user.serializers import WorkspaceSerializers
from user.repository import token as tokenRepository
from user.repository import passport as passportRepository


class TokenUtil(object):
    """docstring for TokenUtil"""

    # token表创建token
    def create_token(self, **kwargs):
        # 首先判断Token是否存在
        passport_id = kwargs["passport_id"]
        search = {}
        search["passport_id"] = passport_id
        search["login_type"] = kwargs["login_type"]
        token_list = tokenRepository.search(**search)
        if len(token_list) > 0:
            # 先删除已经存在的token
            exist_token = token_list[0]
            exist_token.delete()

        token = Token()
        token.passport_id = kwargs["passport_id"]
        token.token_id = self.create_token_id()
        token.start_time = TimeUtil.get_utc_time()
        token.expire_time = kwargs["expire_time"] + token.start_time
        token.login_type = kwargs["login_type"]
        token.created = TimeUtil.get_utc_time()
        token.version = 1
        token.save()

        # 获取用户名称.
        search = {}
        search["passport_id"] = passport_id
        passport = passportRepository.load(**search)

        workspace = Workspace()
        workspace.name = passport.name
        workspace.avert = passport.avert
        workspace.signature = passport.signature
        workspace.update_time = TimeUtil.get_utc_time()
        workspace.passport_id = passport_id
        workspace.token_id = token.token_id
        workspace.start_time = token.start_time
        workspace.expire_time = token.expire_time
        workspace.login_type = token.login_type
        cache.set(token.token_id, workspace, kwargs["expire_time"])

        return workspace

    # 每次调用更新redis过期时间
    def update_token_expire(self):
        pass

    def create_token_id(self):
        salt = CryptogramGenerate.get_salt(16).decode()
        uid = uuid.uuid1().hex
        return uid + '|' + salt

    @staticmethod
    def get_header_token(request):
        token = request.META.get("HTTP_AUTHORIZATION")
        if token:
            token = token.split(" ")[1]
            return token
        return None

    # 获取用户信息
    def get_user_info(request):
        token_id = TokenUtil.get_header_token(request)
        token = cache.get(token_id)
        if token:
            return token
        kwargs = {}
        kwargs["token_id"] = token_id
        token = tokenRepository.load(**kwargs)
        if token:
            return token
        return None
