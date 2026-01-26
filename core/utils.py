import hashlib
import os


def upload_path(instance, filename, **kwargs):
    """
    Generate upload path using SHA-256 hash of image content.

    Note: Changed from MD5 to SHA-256 for better collision resistance.
    This only affects new uploads; existing files keep their original paths.
    """
    hasher = hashlib.sha256()
    for chunk in instance.image.chunks():
        hasher.update(chunk)
    hash = hasher.hexdigest()
    base, ext = os.path.splitext(filename)
    return '%(first)s/%(second)s/%(hash)s/%(base)s%(ext)s' % {
        'first': hash[0],
        'second': hash[1],
        'hash': hash,
        'base': base,
        'ext': ext,
    }
