from django.db import models
from enum import Enum

# Create your models here.


# 用户表
class Passport(models.Model):
    """docstring for Passport"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default='')
    avert = models.CharField(max_length=50, default='')  # 头像
    signature = models.CharField(max_length=1000, default='')  # 签名
    mobile = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=100, default='')  # 加密后密码
    created = models.IntegerField(default=0)

    class Meta:
        db_table = 'passport'


# token表
class Token(models.Model):
    """docstring for  Token"""
    passport_id = models.IntegerField(primary_key=True)
    token_id = models.CharField(max_length=60, default='')
    start_time = models.IntegerField(default=0)
    expire_time = models.IntegerField(default=0)
    login_type = models.IntegerField(null=True)
    updated = models.IntegerField(null=True)
    created = models.IntegerField(null=True)
    version = models.IntegerField(null=True)

    class LoginType(Enum):
        """docstring for LoginType"""
        web = 1
        app = 2

        def describe(self):
            dictName = {}
            dictName[1] = 'web'
            dictName[2] = 'app'
            return self.value, dictName[self.value]

    class Meta:
        db_table = 'token'


# workspace对象构建
class Workspace(models.Model):
    """docstring for workspace"""
    passport_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    avert = models.CharField(max_length=50, blank=True)
    signature = models.CharField(max_length=1000, blank=True)
    update_time = models.IntegerField(null=True)
    token_id = models.CharField(max_length=60, null=True)
    start_time = models.IntegerField(null=True)
    expire_time = models.IntegerField(null=True)
    login_type = models.IntegerField(null=True)


# 文章等分类表
class Catalog(models.Model):
    """docstring for Catalog"""
    id = models.AutoField(primary_key=True)
    passport_id = models.IntegerField()
    name = models.CharField(max_length=100)
    parent_id = models.IntegerField()
    catalog_type = models.IntegerField()
    layer = models.IntegerField()
    left_id = models.IntegerField()
    right_id = models.IntegerField()
    icon = models.CharField(max_length=100)
    created = models.IntegerField()
    updated = models.IntegerField()
    version = models.IntegerField()

    class Meta:
        """docstring for Meta"""
        db_table = 'catalog'

    class Type(Enum):
        """docstring for LoginType"""
        article = 1
        comment = 2

        def describe(self):
            dictName = {}
            dictName[1] = '文章分类'
            dictName[2] = '评论'
            return self.value, dictName[self.value]


# 文章
class Article(models.Model):
    """docstring for Content"""
    id = models.AutoField(primary_key=True)
    passport_id = models.IntegerField()
    passport_name = models.CharField(max_length=100)  # 冗余了作者名称
    catalog_id = models.IntegerField()
    catalog_name = models.CharField(max_length=100)  # 冗余
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=2000)
    pv = models.IntegerField()
    # favorite = models.IntegerField()  # 点赞量
    created = models.IntegerField()
    updated = models.IntegerField()
    version = models.IntegerField()

    class Meta:
        """docstring for Meta"""
        db_table = "article"
        ordering = ['-created']


# 评论, 多级评论问题, 树结构
class Comment(models.Model):
    """docstring for Comment"""
    id = models.AutoField(primary_key=True)
    passport_id = models.IntegerField()
    passport_name = models.CharField(max_length=100)
    parent_id = models.IntegerField()
    catalog_type = models.IntegerField()
    layer = models.IntegerField()
    left_id = models.IntegerField()
    right_id = models.IntegerField()
    article_id = models.IntegerField()
    content = models.CharField(max_length=2000)
    created = models.IntegerField()
    updated = models.IntegerField()
    version = models.IntegerField()

    class Type(Enum):
        """docstring for LoginType"""
        article = 1
        comment = 2

        def describe(self):
            dictName = {}
            dictName[1] = '文章分类'
            dictName[2] = '评论'
            return self.value, dictName[self.value]

    class Meta:
        """docstring for Meta"""
        db_table = "comment"


# 评论点赞
class CommentFavour(models.Model):
    """docstring for Comment"""
    comment_id = models.IntegerField()
    passport_id = models.IntegerField()

    class Meta:
        """docstring for Meta"""
        db_table = "comment_favour"
        unique_together = ('comment_id', 'passport_id')


# 收藏文章列表
class Collect(models.Model):
    """docstring for  Collect"""
    passport_id = models.IntegerField()
    article_id = models.IntegerField()
    created = models.IntegerField()

    class Meta:
        """docstring for Meta"""
        db_table = "collect"
        unique_together = ('passport_id', 'article_id')


# 关注的人列表
class Follow(models.Model):
    """docstring for Follow"""
    passport_id = models.IntegerField()  # 被关注人
    follow_id = models.IntegerField()  # 关注人


class Message(models.Model):
    """docstring for Me"""
    id = models.IntegerField(primary_key=True)
    reply_id = models.IntegerField()  # 回复人
    reply_name = models.CharField(max_length=200)  # 回复人名称
    passport_id = models.IntegerField()  # 被回复人
    article_id = models.IntegerField()
    article_title = models.IntegerField()
    reply_type = models.IntegerField()
    status = models.IntegerField()
    created = models.IntegerField()  # 回复时间

    class Type(Enum):
        """docstring for LoginType"""
        reply = 1
        answer = 2

        def describe(self):
            dictName = {}
            dictName[1] = '回复'
            dictName[2] = '回答'

    class Meta:
        """docstring for Meta"""
        db_table = "message"
