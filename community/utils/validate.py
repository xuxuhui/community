import re


class Validate(object):

    """docstring for ClassName"""
    @staticmethod
    def email_validate(email):
        pattern = re.compile('.+@.+\\..+')
        if pattern.match(email):
            return True
        return False

    @staticmethod
    def mobile_validate(mobile):
        pattern = re.compile('^1\d{10}$')
        print(pattern.match(mobile))
        if pattern.match(mobile):
            return True
        return False

    @staticmethod
    def password_validate(password):
        if len(password) < 6:
            return False
        pattern = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$')
        if pattern.match(password):
            return True
        return False
