from django.db import models
from enum import Enum


# Create your models here.


# 分类
class Catalog(models.Model):
    """docstring for Catalog"""
    id = models.AutoField(primary_key=True)
    passport_id = models.IntegerField()
    parent_id = models.IntegerField()
    left_id = models.IntegerField()
    right_id = models.IntegerField()
    layer = models.IntegerField()
    catalog_type = models.IntegerField()
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    icon = models.CharField(max_length=20)
    version = models.IntegerField()
    updated = models.IntegerField()
    created = models.IntegerField()

    class Meta:
        """docstring for Meta"""
        db_table = 'catalog'

    class Type(Enum):
        """docstring for LoginType"""
        pet = 1

        def describe(self):
            dictName = {}
            dictName[1] = '宠物'
            return self.value, dictName[self.value]


# 宠物索引表
class PetIndex(models.Model):
    """docstring for  Pet"""
    pet_id = models.IntegerField()
    catalog_id = models.IntegerField()
    name = models.CharField(max_length=50)
    created = models.IntegerField()

    class Meta:
        """docstring for Meta"""
        db_table = "pet_index"


# 宠物介绍
class Pet(models.Model):
    """docstring for ClassName"""
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=50)
    alias = models.CharField(max_length=200)
    e_name = models.CharField(max_length=100)
    wool_length = models.IntegerField()
    type = models.IntegerField()
    image = models.CharField(max_length=50)
    content = models.CharField(max_length=50)
    height = models.CharField(max_length=50)
    weight = models.CharField(max_length=50)
    lifetime = models.IntegerField()
    source_area = models.CharField(max_length=50)
    reference_price = models.CharField(max_length=50)
    version = models.IntegerField()
    updated = models.IntegerField()
    created = models.IntegerField()

    class Type(Enum):
        """docstring for Type"""
        big = 1
        middle = 2
        small = 3

        def describe(self):
            dictName = {}
            dictName[1] = '大型'
            dictName[2] = '中型'
            dictName[3] = '小型'
            return self.value, dictName[self.value]

    class WoolLength(object):
        """docstring for WoolLength"""
        long_hair = 1
        short_hair = 2

        def describe(self):
            dictName = {}
            dictName[1] = '长毛'
            dictName[2] = '短毛'
            return self.value, dictName[self.value]

    class Meta:
        """docstring for Meta"""
        db_table = "pet"
