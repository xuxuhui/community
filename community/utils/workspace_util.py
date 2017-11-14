from django.core.cache import cache
from user.models import Workspace
from user.repository import token as tokenRepository
from user.repository import passport as passportRepository
from .time_util import TimeUtil


class WorkspaceUtil(object):
    """docstring for Workspace"""
    @staticmethod
    def get_workspace(request):
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return None
        token = token.split(" ")[1]
        workspace = cache.get(token)
        if not workspace:
            kwargs = {}
            kwargs["token_id"] = token
            token_info = tokenRepository.load(**kwargs)
            if not token_info or token_info.expire_time < TimeUtil.get_utc_time():
                return None
            workspace = WorkspaceUtil.get_workspace_by_token(token_info)

        return workspace

    @staticmethod
    def get_workspace_by_token(token):
        passport_id = token.passport_id
        search = {}
        search["passport_id"] = passport_id
        passport = passportRepository.load(**search)

        workspace = Workspace()
        workspace.name = passport.name
        workspace.passport_id = passport_id
        workspace.token_id = token.token_id
        workspace.avert = passport.avert
        workspace.signature = passport.signature
        workspace.start_time = token.start_time
        workspace.expire_time = token.expire_time
        workspace.login_type = token.login_type

        return workspace
