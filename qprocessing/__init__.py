from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("qprocessing")
except PackageNotFoundError as e:
    # package is not installed
    pass
