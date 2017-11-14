class PetRouter(object):
    """
    A router to control all database operations on models in the
    pet application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read pet models go to pet.
        """
        if model._meta.app_label == 'pet':
            return 'pet'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write pet models go to pet.
        """
        if model._meta.app_label == 'pet':
            return 'pet'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the pet app is involved.
        """
        if obj1._meta.app_label == 'pet' or \
                obj2._meta.app_label == 'pet':
            return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the pet app only appears in the 'pet'
        database.
        """
        if app_label == 'pet':
            return db == 'pet'
        return None
