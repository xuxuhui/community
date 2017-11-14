from qiniu import Auth


class QiniuImage(object):
    """docstring for QiniuImage"""

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key

    def get_token(self):
        q = Auth(self.access_key, self.secret_key)
        bucket_name = "images"
        key = None
        token = q.upload_token(bucket_name, key, 5 * 60)

        return token
