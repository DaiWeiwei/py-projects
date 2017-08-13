# coding=utf-8


class Role:

    @staticmethod
    def convert(aggregate_obj, role_class_name):
        for obj_name in dir(aggregate_obj):
            obj = getattr(aggregate_obj, obj_name)
            if obj.__class__.__name__ == role_class_name:
                return obj
