from datetime import datetime
from pathlib import Path
from shutil import copy2

from loguru import logger


def archive_report(report_file: Path, archive_folder: Path) -> Path:
    archive_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_file = archive_folder / f"Report_{timestamp}.xlsx"

    copy2(report_file, archive_file)
    logger.info(f"Rapor arşivlendi: {archive_file.name}")

    return archive_file