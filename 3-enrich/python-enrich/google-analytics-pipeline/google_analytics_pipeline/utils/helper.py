import os


def get_files_recursively(dir_path, path_filter=None):
    files = []
    for root, directories, filenames in os.walk(dir_path):
        for filename in filenames:
            path = os.path.join(root, filename)
            if "." in filename:
                continue
            if path_filter and path_filter not in path:
                continue
            files.append(path)

    return files


def deep_get(dictionary, *keys):
    return reduce(lambda d, key: d.get(key, None) if isinstance(d, dict) else None, keys, dictionary)
