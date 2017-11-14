from rest_framework import serializers
from .models import Passport, Token, Workspace, Follow, Catalog, Article, Comment, Message


class RegisterSerializers(serializers.ModelSerializer):

    class Meta(object):
        model = Passport
        fields = '__all__'


class TokenSerializers(serializers.ModelSerializer):

    class Meta(object):
        """docstring for Meta"""
        model = Token
        fields = '__all__'


class WorkspaceSerializers(serializers.ModelSerializer):

    class Meta(object):
        """docstring for Meta"""
        model = Workspace
        fields = '__all__'


class FollowSerializers(serializers.ModelSerializer):
    """docstring for Follow"""

    class Meta(object):
        """docstring for Meta"""
        model = Follow
        fields = '__all__'


class CatalogSerializers(serializers.ModelSerializer):
    """docstring for Follow"""

    class Meta(object):
        """docstring for Meta"""
        model = Catalog
        fields = '__all__'


class ArticleSerializers(serializers.ModelSerializer):
    """docstring for Follow"""

    class Meta(object):
        """docstring for Meta"""
        model = Article
        fields = '__all__'


class CommentSerializers(serializers.ModelSerializer):
    """docstring for ClassName"""

    class Meta(object):
        """docstring for Meta"""
        model = Comment
        fields = '__all__'


class MessageSerializers(serializers.ModelSerializer):
    """docstring for Message"""

    class Meta(object):
        """docstring for Meta"""
        model = Message
        fields = '__all__'
