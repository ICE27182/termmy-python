

from os import PathLike
from re import compile

EXTENSION = compile(r".*\.([^\./\\]+)$")
def get_path_extension(path: str | PathLike):
    """
    Get the extension of given path.

    Returns the part after the last (back)slash after the last period.
    Return an empty string if it does not have an extension or the path ends
    with a (back)slash.

    e.g.
    - ~/Photos/image.png -> "png"
    - D:\\\\Code\\\\main.py -> "py"
    - ./....jpg -> "jpg"
    - ../bin/ -> ""
    - ../bin/main -> ""
    - ./.git -> "git"
    - ./.git/HEAD -> ""
    """
    extention = EXTENSION.search(path)
    return extention[1] if extention else ""

if __name__ == "__main__":
    print(get_path_extension(r"~/Photos/image.png"))
    print(get_path_extension(r"D:\\Code\\main.py"))
    print(get_path_extension(r"./....jpg"))
    print(get_path_extension(r"../bin/"))
    print(get_path_extension(r"../bin/main"))
    print(get_path_extension(r"./.git"))
    print(get_path_extension(r"./.git/HEAD"))