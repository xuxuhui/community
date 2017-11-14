def get_object(obj_list):
    if not obj_list:
        return None
    elif len(obj_list) == 1:
        return obj_list[0]
    else:
        raise
