"""
Management command: auto_tag_pins

Classifies untagged pins with MobileNetV2 and applies the predicted tags.

Usage:
    python manage.py auto_tag_pins [options]

Options:
    --dry-run        Print predicted tags without saving to DB
    --limit N        Process at most N pins
    --pin-id N       Process a single pin by primary key
    --all-pins       Re-tag already-tagged pins (default: untagged only)
    --download-only  Download model and labels, then exit
"""
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from core.models import Pin
from core.auto_tagger import AutoTagger, ensure_model_downloaded, get_model_dir


class Command(BaseCommand):
    help = "Auto-tag pins using MobileNetV2 image classification"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print predicted tags without saving",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            metavar="N",
            help="Maximum number of pins to process",
        )
        parser.add_argument(
            "--pin-id",
            type=int,
            default=None,
            metavar="N",
            help="Process a single pin by primary key",
        )
        parser.add_argument(
            "--all-pins",
            action="store_true",
            help="Re-tag already-tagged pins (default: untagged only)",
        )
        parser.add_argument(
            "--download-only",
            action="store_true",
            help="Download model and labels then exit",
        )

    def handle(self, *args, **options):
        if options["download_only"]:
            model_path, labels_path = ensure_model_downloaded()
            self.stdout.write(f"Model:  {model_path}")
            self.stdout.write(f"Labels: {labels_path}")
            return

        tagger = AutoTagger()

        if options["pin_id"] is not None:
            try:
                queryset = Pin.objects.filter(pk=options["pin_id"])
            except Pin.DoesNotExist:
                self.stderr.write(f"Pin {options['pin_id']} not found.")
                return
        elif options["all_pins"]:
            queryset = Pin.objects.order_by("pk")
        else:
            # Only untagged pins — use ContentType to avoid ID collisions
            # with other taggable models that share the same TaggedItem table.
            from taggit.models import TaggedItem
            pin_ct = ContentType.objects.get_for_model(Pin)
            tagged_ids = TaggedItem.objects.filter(
                content_type=pin_ct
            ).values_list("object_id", flat=True)
            queryset = Pin.objects.exclude(pk__in=tagged_ids).order_by("pk")

        if options["limit"] is not None:
            queryset = queryset[: options["limit"]]

        processed = 0
        skipped = 0

        for pin in queryset:
            try:
                if options["dry_run"]:
                    tags = tagger.classify_pin(pin)
                    self.stdout.write(
                        f"Pin {pin.pk}: {', '.join(tags) if tags else '(no tags above threshold)'}"
                    )
                else:
                    tags = tagger.tag_pin(pin)
                    self.stdout.write(
                        f"Pin {pin.pk}: tagged {tags}"
                    )
                processed += 1
            except Exception as exc:
                self.stderr.write(f"Pin {pin.pk}: error — {exc}")
                skipped += 1

        suffix = " (dry run)" if options["dry_run"] else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"Done{suffix}: {processed} processed, {skipped} skipped."
            )
        )
