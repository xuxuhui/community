class UserRouter(object):
    """
    A router to control all database operations on models in the
    user application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read user models go to user.
        """
        if model._meta.app_label == 'user':
            return 'users'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write user models go to user.
        """
        if model._meta.app_label == 'user':
            return 'users'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'user' or \
                obj2._meta.app_label == 'user':
            return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if app_label == 'user':
            return db == 'users'
        return None
