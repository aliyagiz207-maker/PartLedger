import sys
from pathlib import Path

from loguru import logger


def setup_logger():
    """
    Programın log ayarlarını yapar.

    Normal çalışma ortamında loglar proje kökündeki logs/
    klasörüne yazılır.

    PyInstaller EXE ortamında ise loglar EXE'nin bulunduğu
    klasördeki logs/ dizinine yazılır.
    """

    if getattr(sys, "frozen", False):
        project_root = Path(sys.executable).resolve().parent
    else:
        project_root = Path(__file__).resolve().parent.parent

    log_folder = project_root / "logs"
    log_folder.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        log_folder / "app.log",
        rotation="1 MB",
        retention="10 days",
        level="INFO",
        encoding="utf-8",
    )

    if sys.stdout is not None:
        logger.add(
            sys.stdout,
            level="INFO",
        )

    return logger