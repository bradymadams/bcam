import bcam


def get_path_non_comment_operations(path: bcam.path.Path) -> list[bcam.path.Operation]:
    return list(filter(lambda op: not isinstance(op, bcam.path._Comment), path))
