
def sort_to_match(ids, objects, attr="id"):
    """ Sorts objects by one of their attributes to match order of ids. Used when order of objects is
    needed to be retained and DB returns objects in "random" order.
    """
    object_map = {getattr(o, attr): o for o in objects}
    objects = [object_map[id] for id in ids]
    return objects
