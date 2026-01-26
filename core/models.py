import ipaddress
import logging
import PIL.Image
import requests
from urllib.parse import urlparse

from io import BytesIO

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models import Index
from django.dispatch import receiver

from django_images.models import Image as BaseImage, Thumbnail
from taggit.managers import TaggableManager

from users.models import User

logger = logging.getLogger(__name__)

# Maximum response size for image downloads (10 MB)
MAX_IMAGE_SIZE = 10 * 1024 * 1024
# Request timeout in seconds
REQUEST_TIMEOUT = 10


class SSRFProtectionError(Exception):
    """Raised when a URL fails SSRF validation."""
    pass


def is_private_ip(hostname):
    """Check if a hostname resolves to a private/reserved IP address."""
    import socket
    try:
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        # Block private, loopback, link-local, and reserved addresses
        return (
            ip_obj.is_private or
            ip_obj.is_loopback or
            ip_obj.is_link_local or
            ip_obj.is_reserved or
            ip_obj.is_multicast
        )
    except (socket.gaierror, ValueError):
        # If we can't resolve, block it to be safe
        return True


def validate_url_for_ssrf(url):
    """
    Validate a URL to prevent SSRF attacks.

    Raises SSRFProtectionError if the URL is not safe.
    """
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise SSRFProtectionError(f"Invalid URL format: {e}")

    # Only allow http and https schemes
    if parsed.scheme not in ('http', 'https'):
        raise SSRFProtectionError(f"Invalid URL scheme: {parsed.scheme}. Only http/https allowed.")

    # Must have a hostname
    if not parsed.hostname:
        raise SSRFProtectionError("URL must have a hostname")

    # Block private IP ranges
    if is_private_ip(parsed.hostname):
        raise SSRFProtectionError("URLs pointing to private/internal networks are not allowed")

    return True


class ImageManager(models.Manager):
    # Updated User-Agent string (Chrome 120 on Windows 10)
    _default_ua = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36',
    }

    @staticmethod
    def _is_valid_image(fp):
        fp.seek(0)
        try:
            PIL.Image.open(fp)
        except PIL.UnidentifiedImageError:
            fp.seek(0)
            return False
        else:
            fp.seek(0)
            return True

    # FIXME: Move this into an asynchronous task
    def create_for_url(self, url, referer=None):
        """
        Download an image from a URL and create an Image object.

        Includes SSRF protection:
        - Only allows http/https schemes
        - Blocks private/internal IP addresses
        - Enforces request timeout
        - Limits response size
        """
        # Validate URL for SSRF protection
        try:
            validate_url_for_ssrf(url)
        except SSRFProtectionError as e:
            logger.warning(f"SSRF protection blocked URL {url}: {e}")
            return None

        file_name = url.split("/")[-1].split('#')[0].split('?')[0]
        # Sanitize filename
        if not file_name or len(file_name) > 255:
            file_name = 'downloaded_image'

        buf = BytesIO()
        headers = dict(self._default_ua)
        if referer is not None:
            headers["Referer"] = referer

        try:
            # Stream the response with timeout to enforce size limits
            response = requests.get(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                stream=True
            )
            response.raise_for_status()

            # Check Content-Length header if available
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > MAX_IMAGE_SIZE:
                logger.warning(f"Image too large (Content-Length: {content_length}): {url}")
                return None

            # Read with size limit
            bytes_read = 0
            for chunk in response.iter_content(chunk_size=8192):
                bytes_read += len(chunk)
                if bytes_read > MAX_IMAGE_SIZE:
                    logger.warning(f"Image exceeded size limit while downloading: {url}")
                    return None
                buf.write(chunk)

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout downloading image from: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error downloading image from {url}: {e}")
            return None

        if not self._is_valid_image(buf):
            return None

        obj = InMemoryUploadedFile(buf, 'image', file_name,
                                   None, buf.tell(), None)
        # create the image and its thumbnails in one transaction, removing
        # a chance of getting Database into a inconsistent state when we
        # try to create thumbnails one by one later
        image = self.create(image=obj)
        Thumbnail.objects.get_or_create_at_sizes(image, settings.IMAGE_SIZES.keys())
        return image


class Image(BaseImage):
    objects = ImageManager()

    class Sizes:
        standard = "standard"
        thumbnail = "thumbnail"
        square = "square"

    class Meta:
        proxy = True

    @property
    def standard(self):
        return Thumbnail.objects.get(
            original=self, size=self.Sizes.standard
        )

    @property
    def thumbnail(self):
        return Thumbnail.objects.get(
            original=self, size=self.Sizes.thumbnail
        )

    @property
    def square(self):
        return Thumbnail.objects.get(
            original=self, size=self.Sizes.square
        )


class Board(models.Model):
    class Meta:
        unique_together = ("submitter", "name")
        indexes = [
            Index(fields=["submitter", "name"]),
        ]

    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False, null=False)
    private = models.BooleanField(default=False, blank=False)
    pins = models.ManyToManyField("Pin", related_name="pins", blank=True)

    published = models.DateTimeField(auto_now_add=True)


class Pin(models.Model):
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    private = models.BooleanField(default=False, blank=False)
    url = models.CharField(null=True, blank=True, max_length=2048)
    referer = models.CharField(null=True, blank=True, max_length=2048)
    description = models.TextField(blank=True, null=True)
    image = models.ForeignKey(Image, related_name='pin', on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    def tag_list(self):
        return self.tags.all()

    def __str__(self):
        return '%s - %s' % (self.submitter, self.published)


@receiver(models.signals.post_delete, sender=Pin)
def delete_pin_images(sender, instance, **kwargs):
    try:
        instance.image.delete()
    except Image.DoesNotExist:
        pass
