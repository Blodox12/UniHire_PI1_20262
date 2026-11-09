"""Back up the SQLite database (NFR-09).

Usage:
    python manage.py backup_db             # keeps the 7 most recent backups
    python manage.py backup_db --keep 30

Schedule it every 24 hours (see README > Database backups).
"""

import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.utils import timezone


class Command(BaseCommand):
    help = "Create a timestamped copy of the SQLite database and delete old copies."

    def add_arguments(self, parser):
        parser.add_argument("--keep", type=int, default=7, help="Number of backups to keep (default: 7).")
        parser.add_argument("--dir", default=None, help="Backup folder (default: BACKUP_DIR setting).")

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        if db["ENGINE"] != "django.db.backends.sqlite3":
            raise CommandError("backup_db only supports the SQLite database.")
        source_path = Path(db["NAME"])
        if not source_path.exists():
            raise CommandError(f"Database file not found: {source_path}")
        if options["keep"] < 1:
            raise CommandError("--keep must be at least 1.")

        backup_dir = Path(options["dir"] or settings.BACKUP_DIR)
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
        target_path = backup_dir / f"db-{stamp}.sqlite3"

        # sqlite3's backup API copies a consistent snapshot even while the site
        # is writing (a plain file copy could catch a half-written WAL file).
        connections["default"].close()
        source = sqlite3.connect(source_path)
        target = sqlite3.connect(target_path)
        try:
            with target:
                source.backup(target)
            check = target.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            target.close()
            source.close()
        if check != "ok":
            target_path.unlink(missing_ok=True)
            raise CommandError(f"Backup failed the integrity check: {check}")

        backups = sorted(backup_dir.glob("db-*.sqlite3"), reverse=True)
        for old in backups[options["keep"]:]:
            old.unlink()

        self.stdout.write(self.style.SUCCESS(f"Backup created: {target_path}"))
