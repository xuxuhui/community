import os
import base64
import hashlib


class CryptogramGenerate(object):
    """docstring for cryptogramGenerate"""
    # 加密盐值获取, os.urandmon
    @staticmethod
    def get_salt(length=32):
        return base64.urlsafe_b64encode(os.urandom(length))

    @staticmethod
    def md5(string):
        if isinstance(string, str):
            m = hashlib.md5()
            m.update(string.encode())
            return m.hexdigest()
        else:
            return ''
