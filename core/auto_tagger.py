"""
Lightweight auto-tagger using ONNX Runtime + MobileNetV2.

Mirrors Android MLKit Image Labeling: MobileNetV2 architecture,
ImageNet 1000-class labels, confidence threshold filtering.

Usage:
    from core.auto_tagger import AutoTagger
    tags = AutoTagger().tag_pin(pin)        # classify + persist
    tags = AutoTagger().classify_pin(pin)   # classify only
"""
import logging
import os
import threading
import urllib.request
from typing import List

import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

# ONNX Model Zoo — MobileNetV2 (opset 7, ~13 MB)
_MODEL_URL = (
    "https://github.com/onnx/models/raw/main/validated/"
    "vision/classification/mobilenet/model/mobilenetv2-7.onnx"
)
_LABELS_URL = (
    "https://raw.githubusercontent.com/pytorch/hub/master/"
    "imagenet_classes.txt"
)

# ImageNet preprocessing constants
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

_lock = threading.Lock()
_session = None  # module-level singleton


def get_model_dir() -> str:
    custom = getattr(settings, "AUTO_TAG_MODEL_DIR", None)
    if custom:
        return custom
    media_root = getattr(settings, "MEDIA_ROOT", "/data/media")
    return os.path.join(os.path.dirname(media_root), "auto_tag_models")


def ensure_model_downloaded() -> tuple:
    """Download model and labels if not already present. Returns (model_path, labels_path)."""
    model_dir = get_model_dir()
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "mobilenetv2-7.onnx")
    labels_path = os.path.join(model_dir, "imagenet_classes.txt")

    if not os.path.exists(model_path):
        logger.info("Downloading MobileNetV2 model to %s ...", model_path)
        urllib.request.urlretrieve(_MODEL_URL, model_path)
        logger.info("Model downloaded: %s", model_path)

    if not os.path.exists(labels_path):
        logger.info("Downloading ImageNet labels to %s ...", labels_path)
        urllib.request.urlretrieve(_LABELS_URL, labels_path)
        logger.info("Labels downloaded: %s", labels_path)

    return model_path, labels_path


def _load_labels(labels_path: str) -> List[str]:
    with open(labels_path, "r") as f:
        return [line.strip() for line in f.readlines()]


def _clean_label(raw: str) -> str:
    """Take first synonym, replace underscores, title-case."""
    first = raw.split(",")[0]
    return first.replace("_", " ").strip().title()


class AutoTagger:
    """
    Singleton ONNX session wrapper.  The session is loaded once per process
    (double-checked locking) and reused across calls.  Memory cost is roughly
    150 MB per gunicorn worker that triggers a classification.
    """

    def _get_session(self):
        global _session
        if _session is None:
            with _lock:
                if _session is None:
                    import onnxruntime as ort
                    model_path, _ = ensure_model_downloaded()
                    opts = ort.SessionOptions()
                    opts.inter_op_num_threads = 1
                    opts.intra_op_num_threads = 2
                    _session = ort.InferenceSession(
                        model_path,
                        sess_options=opts,
                        providers=["CPUExecutionProvider"],
                    )
        return _session

    def _preprocess(self, image_path: str) -> np.ndarray:
        from PIL import Image
        img = Image.open(image_path).convert("RGB")
        img = img.resize((224, 224), Image.BILINEAR)
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = (arr - _MEAN) / _STD
        # HWC -> CHW -> NCHW
        arr = arr.transpose(2, 0, 1)[np.newaxis, ...]
        return arr.astype(np.float32)

    def classify_image_file(self, image_path: str) -> List[str]:
        """Run inference on an image file. Returns list of cleaned label strings."""
        threshold = getattr(settings, "AUTO_TAG_CONFIDENCE_THRESHOLD", 0.20)
        max_tags = getattr(settings, "AUTO_TAG_MAX_TAGS", 5)

        session = self._get_session()
        _, labels_path = ensure_model_downloaded()
        labels = _load_labels(labels_path)

        input_name = session.get_inputs()[0].name
        arr = self._preprocess(image_path)
        logits = session.run(None, {input_name: arr})[0][0]

        # softmax
        e = np.exp(logits - logits.max())
        probs = e / e.sum()

        # filter by threshold, sort descending, cap at max_tags
        indices = np.where(probs >= threshold)[0]
        indices = sorted(indices, key=lambda i: probs[i], reverse=True)[:max_tags]

        return [_clean_label(labels[i]) for i in indices]

    def classify_pin(self, pin) -> List[str]:
        """Resolve pin.image.image.path and classify it."""
        image_path = pin.image.image.path
        return self.classify_image_file(image_path)

    def tag_pin(self, pin) -> List[str]:
        """Classify pin and persist the tags. Returns the list of applied tag strings."""
        tags = self.classify_pin(pin)
        if tags:
            pin.tags.add(*tags)
        return tags
