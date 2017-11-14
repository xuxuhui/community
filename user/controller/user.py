import urllib
import json
import http.client
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.cache import cache
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from community.utils.cryptogram import CryptogramGenerate
from community.utils.time_util import TimeUtil
from community.utils.token_util import TokenUtil
from user.models import Passport, Token, Follow
from user.serializers import RegisterSerializers, WorkspaceSerializers
from community.utils.validate import Validate
from community.utils.verification_code import VerificationCode
from community import settings
from user.repository import passport as passportRepository
from user.repository import token as tokenRepository
from community.decorate.authentication import authentication
from user import settings as user_settings
from community.utils.workspace_util import WorkspaceUtil


# Create your views here.

# 验证码发送
@api_view(['POST'])
def send_email(request):
    data = request.data
    if not data.get("email"):
        return Response({"status": 400, "msg": "参数错误"})
    # 验证邮箱有效性
    if not Validate.email_validate(data.get("email")):
        return Response({"status": 400, "msg": "参数错误"})

    validate_code = VerificationCode.num_random_list(6)
    send_mail('萌宠屋', '注册验证码:{0}'.format(validate_code), settings.EMAIL_HOST_USER,
              [data["email"]], fail_silently=False)

    # email作为key缓存code 注册时候比较
    cache.set(data["email"], validate_code, timeout=30 * 60)

    return Response({"status": 200, "msg": "注册码发送成功"})


# 手机验证码发送
@api_view(["POST"])
def send_mobile(request):
    data = request.data
    # 判断验证码是否正确
    if not data.get("uid"):
        return Response({"status": 400, "msg": "参数错误"})
    if not data.get("code"):
        return Response({"status": 400, "msg": "参数错误"})
    key = data.get("uid")
    cache_data = cache.get(key)
    if not data:
        return Response({"status": 400, "msg": "图片验证码过期"})
    if cache_data.lower() != data.get("code"):
        return Response({"status": 400, "msg": "图片验证码错误"})
    if not data.get("mobile"):
        return Response({"status": 400, "msg": "参数错误"})
    # 验证手机号有效性
    if not Validate.mobile_validate(data.get("mobile")):
        return Response({"status": 400, "msg": "手机号不正确"})

    mobile = data["mobile"]
    apikey = user_settings.smsApikey
    sms_host = user_settings.smsHost
    sms_port = user_settings.smsPort
    sms_version = user_settings.smsVersion
    sms_send_uri = "/" + sms_version + "/sms/single_send.json"
    validate_code = VerificationCode.num_random_list(6)
    text = "【易宠享】您的验证码是%s" % (validate_code)
    params = urllib.parse.urlencode(
        {'apikey': apikey, 'text': text, 'mobile': mobile})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = http.client.HTTPSConnection(sms_host, port=sms_port, timeout=60)
    conn.request("POST", sms_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    try:
        response_data = json.loads(response_str.decode("utf-8"))
        if response_data.get("code") == 0:
            # 缓存
            cache.set(mobile, validate_code, timeout=30 * 60)
            return Response({"status": 200, "data": response_data})
        else:
            return Response({"status": 500, "msg": "发送失败"})
    except Exception as e:
        return Response({"status": 500, "msg": "发送失败"})


# 获取图片验证码并缓存, src=data:image/gif;base64 + data展示
@api_view(["GET"])
def get_image_code(request):
    mstream, strs = VerificationCode.generate_verify_image()
    key = VerificationCode.generate_uuid()
    cache.set(key, strs, timeout=60 * 5)
    data = {}
    data["key"] = key
    data["value"] = mstream
    data["code"] = strs

    return Response({"status": 200, "data": data})


# 验证用户名注册
@api_view(["POST"])
def verify_name(request):
    data = request.data
    if not data.get("name"):
        return Response({"status": 400, "msg": "名称不能为空"})
    kwargs = {}
    kwargs["name"] = data["name"]
    passport_list = passportRepository.search(**kwargs)
    if passport_list:
        return Response({"status": 400, "msg": "用户名已存在"})

    return Response({"status": 200, "msg": ""})


# 用户注册
@api_view(['POST'])
def register(request):
    # 判断参数是否正确
    data = request.data
    code = data.get("code")
    if not code:
        return Response({"status": 400, "msg": "验证码不能为空"})
    validate_code = None
    kwargs = {}
    if data.get("mobile"):
        kwargs["mobile"] = data["mobile"]
        passport = passportRepository.load(**kwargs)
        if passport:
            return Response({"status": 400, "msg": "用户已存在"})
        validate_code = cache.get(data.get("mobile"))
    elif data.get("email"):
        kwargs["email"] = data["email"]
        passport = passportRepository.load(**kwargs)
        if passport:
            return Response({"status": 400, "msg": "用户已存在"})
        validate_code = cache.get(data.get("email"))
    else:
        return Response({"status": 400, "msg": "参数错误"})

    kwargs = {}
    kwargs["name"] = data["name"]
    passport_list = passportRepository.search(**kwargs)
    if passport_list:
        return Response({"status": 400, "msg": "用户名已存在"})

    if validate_code != str(code):
        return Response({"status": 400, "msg": "验证码错误"})

    password = data.get("password")
    if not password:
        return Response({"status": 400, "msg": "密码不能为空"})
    if not Validate.password_validate(password):
        return Response({"status": 400, "msg": "密码格式不正确"})

    # 随机生成盐值加密
    salt = CryptogramGenerate.get_salt().decode()
    password = CryptogramGenerate.md5(password + salt)
    password = password + '|' + salt
    created = TimeUtil.get_utc_time()
    avert = user_settings.defaultAvert
    passport = Passport(password=password, created=created,
                        email=data.get("email"), mobile=data.get("mobile"), name=data.get("name"), avert=avert)
    passport.save()

    return Response({"status": 200, "msg": ""})


# 邮箱,手机号是否被注册
@api_view(['POST'])
# @authentication(sign=True)
def is_exist(request):
    data = request.data
    passport = None
    kwargs = {}
    if data.get("email"):
        kwargs["email"] = data["email"]
        passport = passportRepository.load(**kwargs)
        if passport:
            passport = RegisterSerializers(passport).data
    elif data.get("mobile"):
        kwargs["mobile"] = data["mobile"]
        passport = passportRepository.load(**kwargs)
        if passport:
            passport = RegisterSerializers(passport).data
    else:
        return Response({"status": 400, "msg": "参数错误"})
    return Response({"status": 200, "data": passport})


# 密码修改
@api_view(['POST'])
def modify_password(request):
    data = request.data
    code = data.get("code")
    if not code:
        return Response({"status": 400, "msg": "参数错误"})
    kwargs = {}
    if data.get("email"):
        kwargs["email"] = data["email"]
        passport = passportRepository.load(**kwargs)
        if not passport:
            return Response({"status": 404, "msg": "用户不存在"})
        validate_code = cache.get(data.get("email"))
        if not validate_code:
            return Response({"status": 404, "msg": "验证码过期"})
    elif request.get("mobile"):
        kwargs["mobile"] = data["mobile"]
        passport = passportRepository.load(**kwargs)
        if not passport:
            return Response({"status": 404, "msg": "用户不存在"})
        validate_code = cache.get(data.get("mobile"))
        if not validate_code:
            return Response({"status": 404, "msg": "验证码过期"})
    else:
        return Response({"status": 400, "msg": "参数错误"})

    if str(code) != validate_code:
        return Response({"status": 400, "msg": "验证码错误"})

    password = data.get("password")
    if not password:
        return Response({"status": 400, "msg": "密码不能为空"})
    if not Validate.password_validate(password):
        return Response({"status": 400, "msg": "密码格式不正确"})

    salt = CryptogramGenerate.get_salt().decode()
    password = CryptogramGenerate.md5(password + salt)
    password = password + '|' + salt
    passport.password = password
    passport.save()

    return Response({"status": 200, "msg": "密码更新成功"})


# 登录, token的操作, TODO 每次登录用elastic_search记录,作为登录日志
@api_view(['POST'])
@transaction.atomic(using='users')
def login(request):
    data = request.data
    password = data.get("password")
    if not password:
        return Response({"status": 400, "msg": "参数错误"})

    kwargs = {}
    if data.get("email"):
        kwargs["email"] = data["email"]
        passport = passportRepository.load(**kwargs)
        if not passport:
            return Response({"status": 404, "msg": "用户名或密码错误"})
    elif data.get("mobile"):
        kwargs["mobile"] = data["mobile"]
        passport = passportRepository.load(**kwargs)
        if not passport:
            return Response({"status": 404, "msg": "用户名或密码错误"})
    else:
        return Response({"status": 400, "msg": "参数错误"})
    salt = passport.password.split('|')[1]
    password = CryptogramGenerate.md5(password + salt)
    if passport.password != password + '|' + salt:
        return Response({"status": 404, "msg": "用户名或密码错误"})

    # 每次登录都会创建一个token信息, 并将token信息写入到redis缓存, key passport, value token
    login_type = data["login_type"]
    expire_time = None
    if login_type == Token.LoginType.app.value:
        expire_time = user_settings.appExpireTime
    elif login_type == Token.LoginType.web.value:
        expire_time = user_settings.webExpireTime
    kwargs = {}
    kwargs["passport_id"] = passport.id
    kwargs["expire_time"] = expire_time
    kwargs["login_type"] = login_type

    token_util = TokenUtil()
    workspace = token_util.create_token(**kwargs)
    workspace = WorkspaceSerializers(workspace).data
    return Response({"status": 200, "msg": "登录成功", "data": workspace})


# 退出登录. 删除缓存中的token 和 token表中的token
@api_view(['POST'])
def logout(request):
    token = TokenUtil.get_header_token(request)
    if token:
        cache.delete(token)
        # 删除数据库记录
        kwargs = {}
        kwargs["token_id"] = token
        token = tokenRepository.load(**kwargs)
        if token:
            token.delete()

    return Response({"status": 200, "msg": "登出成功"})


# 判断登录状态
@api_view(["GET"])
@authentication(sign=True)
def is_login(request):

    return Response({"status": 200, "msg": "登录状态"})


# 完善用户信息
@api_view(['POST'])
@authentication(sign=True)
def improve_user_information(request):
    data = request.data
    workspace = WorkspaceUtil.get_workspace(request)
    passport_id = workspace.passport_id
    data["id"] = passport_id

    # 判断用户名是否存在
    if data.get("name"):
        kwargs = {}
        kwargs["name"] = data["name"]
        passport = passportRepository.load(**kwargs)
        if passport and passport.id != passport_id:
            return Response({"status": 400, "msg": "昵称已存在"})

    passportRepository.modify(**data)

    return Response({"status": 200, "msg": "修改成功"})


# follow用户
@api_view(['POST'])
@authentication(sign=True)
def follow(request):
    data = request.data
    workspace = WorkspaceUtil.get_workspace(request)
    if not workspace:
        return Response({"status": 401, "msg": "token过期"})
    passport_id = workspace.passport_id
    follow_id = data["follow_id"]

    follow = Follow()
    follow.passport_id = passport_id
    follow.follow_id = follow_id
    follow.save()

    return Response({"status": 200, "msg": "关注成功"})


# 关注列表
@api_view(['GET'])
@authentication(sign=True)
def follow_list(request):
    workspace = WorkspaceUtil.get_workspace(request)
    if not workspace:
        return Response({"status": 401, "msg": "token过期"})
    passport_id = workspace.passport_id
    kwargs = {}
    kwargs["passport_id"] = passport_id
    follow_list = passportRepository.follow(**kwargs)
    passport_ids = []
    for item in follow_list:
        passport_ids.append(item.follow_id)
    kwargs = {}
    kwargs["id__in"] = passport_ids
    passport_list = passportRepository.search(1, 1000, **kwargs)
    passport_list = RegisterSerializers(passport_list).data

    return Response({"status": 200, "data": passport_list, "msg": "获取关注列表成功"})


# 被关注列表
@api_view(['GET'])
@authentication(sign=True)
def be_followed_list(request):
    workspace = WorkspaceUtil.get_workspace(request)
    if not workspace:
        return Response({"status": 401, "msg": "token过期"})
    passport_id = workspace.passport_id
    kwargs = {}
    kwargs["follow_id"] = passport_id
    follow_list = passportRepository.follow(**kwargs)
    passport_ids = []
    for item in follow_list:
        passport_ids.append(item.passport_id)
    kwargs = {}
    kwargs["id__in"] = passport_ids
    passport_list = passportRepository.search(1, 1000, **kwargs)
    passport_list = RegisterSerializers(passport_list).data

    return Response({"status": 200, "data": passport_list, "msg": "获取被关注者列表成功"})


@api_view(["GET"])
@authentication(sign=False)
def detail(request):
    data = request.GET
    id = ""
    if data.get("id"):
        id = data["id"]
    else:
        workspace = WorkspaceUtil.get_workspace(request)
        if not workspace:
            return Response({"status": 401, "msg": "登录超时,请重新登录"})
        id = workspace.passport_id
    kwargs = {"id": id}
    passport = passportRepository.load(**kwargs)
    if not passport:
        return Response({"status": 404, "msg": "用户不存在"})

    passport = RegisterSerializers(passport).data
    del passport["password"]
    del passport["mobile"]
    del passport["email"]

    return Response({"status": 200, "msg": "", "data": passport})
