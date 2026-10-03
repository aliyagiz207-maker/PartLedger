from pathlib import Path
from src.file_manager import archive_report

def test_archive_report_copies_file(tmp_path):
    source_file = tmp_path / "Test_Report.xlsx"
    source_file.write_text("dummy excel content")
    
    archive_folder = tmp_path / "archive"
    
    archive_report(source_file, archive_folder)
    
    assert archive_folder.exists(), "Arşiv klasörü oluşturulamadı."
    archived_files = list(archive_folder.glob("Report_*.xlsx"))
    
    assert len(archived_files) == 1, "Dosya arşiv klasörüne kopyalanmadı."
    assert archived_files[0].read_text() == "dummy excel content", "Kopya dosyanın içeriği bozuk."