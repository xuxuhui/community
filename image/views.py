from rest_framework.response import Response
from rest_framework.decorators import api_view
from community.decorate.authentication import authentication
from community.utils.image_util import QiniuImage
from image import settings
from PIL import Image
from qiniu import Auth, put_file
import os
import time


# Create your views here.

# 上传图片需要的token
@api_view(["GET"])
@authentication(sign=True)
def create_token(request):
    access_key = settings.access_key
    secret_key = settings.secret_key
    image = QiniuImage(access_key, secret_key)
    token = image.get_token()

    return Response({"status": 200, "data": {"token": token}})


@api_view(["POST"])
@authentication(sign=True)
def upload_img(request):
    photo = request.FILES['file']

    if photo:
        photoname = str(photo)
        img = Image.open(photo)
        img.save('/tmp/' + photoname)

        access_key = settings.access_key
        secret_key = settings.secret_key
        q = Auth(access_key, secret_key)
        # 要上传的空间
        bucket_name = 'images'
        # 上传到七牛后保存的文件名
        key = "%s.%s" % (str(time.time()).split('.')[0], photoname)
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, key, 3600)
        # 要上传文件的本地路径
        localfile = '/tmp/' + photoname
        ret, info = put_file(token, key, localfile)
        response_data = {}
        if ret and ret.get("key"):
            response_data["code"] = 0
            response_data["msg"] = ""
            response_data["data"] = {"src": settings.host + ret["key"], "title": photoname}
        # 可以交给队列处理
        os.remove(localfile)

        return Response(response_data)
