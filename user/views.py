from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.cache import cache
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from community.utils.cryptogram import CryptogramGenerate
from community.utils.time_util import TimeUtil
from community.utils.token_util import TokenUtil
from .models import Passport, Token
from .serializers import RegisterSerializers, TokenSerializers
from community.utils.validate import Validate
from community.utils.verification_code import VerificationCode
from community import settings
from .repository import passport as passportRepository
from .repository import token as tokenRepository
from community.decorate.authentication import authentication
from user import settings as user_settings


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
    cache.set(data.get("email"), validate_code, timeout=30 * 60)

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
    if cache_data.get("code") != data.get("code"):
        return Response({"status": 400, "msg": "图片验证码错误"})
    if not data.get("mobile"):
        return Response({"status": 400, "msg": "参数错误"})
    # 验证手机号有效性
    if not Validate.mobile_validate(data.get("mobile")):
        return Response({"status": 400, "msg": "手机号不正确"})

    #  TODO 发送手机验证码, mobile做为key 并缓存


# 获取图片验证码并缓存, src=data:image/gif;base64 + data展示
@api_view(["GET"])
def get_image_code(request):
    mstream, strs = VerificationCode.generate_verify_image()
    key = VerificationCode.generate_uuid()
    cache.set(key, strs, timeout=60 * 5)
    data = {}
    data["key"] = key
    data["value"] = mstream

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
    passport = Passport(password=password, created=created,
                        email=data.get("email"), mobile=data.get("mobile"), name=data.get("name"))
    passport.save()

    return Response({"status": 200, "msg": ""})


# 邮箱,手机号是否被注册
@api_view(['POST'])
@authentication(sign=True)
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
    passport = passport[0]
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
    token = token_util.create_token(**kwargs)
    token = TokenSerializers(token).data
    return Response({"status": 200, "msg": "登录成功", "data": token})


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


# 完善用户信息
@api_view(['POST'])
@authentication(sign=True)
def improve_user_information(request):
    pass
