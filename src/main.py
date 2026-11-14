import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from loguru import logger

from config_loader import load_config
from data_cleaner import clean_data
from excel_reader import read_and_combine
from file_manager import archive_report
from kpi_calculator import calculate_kpis
from logger import setup_logger
from pdf_report import generate_pdf_report
from report_generator import generate_report
from validator import validate_dataframe


class PartLedgerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PartLedger - Kurumsal Veri İşleme Motoru")
        self.root.geometry("750x500")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")

        # Ana Çerçeve
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- BAŞLIK ALANI ---
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title_label = ttk.Label(
            header_frame,
            text="PartLedger",
            font=("Helvetica", 24, "bold"),
            foreground="#1F4E78",
        )
        title_label.pack(anchor=tk.W)

        subtitle = ttk.Label(
            header_frame,
            text="Otomatik Veri Analiz ve Raporlama Motoru",
            font=("Helvetica", 11, "italic"),
            foreground="gray",
        )
        subtitle.pack(anchor=tk.W)

        # --- LOG (KONSOL) ALANI ---
        console_frame = ttk.LabelFrame(main_frame, text=" Sistem İşlem Günlüğü ", padding="10")
        console_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.console = tk.Text(
            console_frame,
            height=12,
            bg="#1E1E1E",
            fg="#00FF00",
            font=("Consolas", 9),
            state=tk.DISABLED,
        )
        scrollbar = ttk.Scrollbar(console_frame, command=self.console.yview)
        self.console.configure(yscrollcommand=scrollbar.set)

        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- ALT BUTONLAR ALANI ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_open_input = ttk.Button(
            btn_frame,
            text="📂 Input Klasörünü Aç",
            command=self.open_input_folder,
        )
        self.btn_open_input.pack(side=tk.LEFT, padx=5, ipady=5)

        self.btn_open_output = ttk.Button(
            btn_frame,
            text="📂 Output Klasörünü Aç",
            command=self.open_output_folder,
        )
        self.btn_open_output.pack(side=tk.LEFT, padx=5, ipady=5)

        self.run_btn = ttk.Button(
            btn_frame,
            text="🚀 Raporları Üret",
            command=self.start_processing,
        )
        self.run_btn.pack(side=tk.RIGHT, padx=5, ipady=5, ipadx=20)

        self._log_to_console("PartLedger GUI başarıyla başlatıldı. Sistem hazır.")

        # PyInstaller yol çözümü
        if getattr(sys, "frozen", False):
            self.project_root = Path(sys.executable).resolve().parent
        else:
            self.project_root = Path(__file__).resolve().parent.parent

        self.input_folder = self.project_root / "data" / "input"
        self.output_folder = self.project_root / "data" / "output"

    def _log_to_console(self, message):
        """Konsol ekranına gerçek zamanlı bilgi basar."""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, f"> {message}\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def open_input_folder(self):
        """Kullanıcının Excel dosyalarını atacağı klasörü tek tıkla açar."""
        self.input_folder.mkdir(parents=True, exist_ok=True)
        os.startfile(str(self.input_folder))

    def open_output_folder(self):
        """Üretilen raporların olduğu klasörü tek tıkla açar."""
        self.output_folder.mkdir(parents=True, exist_ok=True)
        os.startfile(str(self.output_folder))

    def start_processing(self):
        self.run_btn.config(state=tk.DISABLED)
        self.btn_open_input.config(state=tk.DISABLED)
        self._log_to_console("Veri işleme hattı (pipeline) tetiklendi...")

        thread = threading.Thread(target=self.run_pipeline, daemon=True)
        thread.start()

    def run_pipeline(self):
        try:
            config = load_config()
            archive_folder = self.project_root / "data" / "archive"

            self.input_folder.mkdir(parents=True, exist_ok=True)
            self.output_folder.mkdir(parents=True, exist_ok=True)
            archive_folder.mkdir(parents=True, exist_ok=True)

            if not any(self.input_folder.glob("*.xls*")) and not any(self.input_folder.glob("*.csv")):
                raise ValueError(
                    "Analiz edilecek veri bulunamadı. Lütfen Input klasörüne veri ekleyin."
                )

            self.root.after(
                0,
                self._log_to_console,
                "Ham veriler (Excel/CSV) okunuyor (Bellek Optimizasyonlu)...",
            )
            df = read_and_combine(self.input_folder, chunk_size=50000)
            if df is None:
                raise ValueError(
                    "Input klasöründeki dosyalardan okunabilir veri çıkarılamadı. "
                    "Dosya formatlarını kontrol edin."
                )

            self.root.after(
                0,
                self._log_to_console,
                "Veri bütünlüğü doğrulanıyor ve anormallikler temizleniyor...",
            )
            # Tamamen boş satırları doğrulamadan önce ayıkla
            df = df.dropna(how="all")
            df = validate_dataframe(df)
            df = clean_data(df)

            self.root.after(
                0,
                self._log_to_console,
                "Finansal metrikler (KPI) ve özet tablolar hesaplanıyor...",
            )
            kpis, region_summary, product_summary, monthly_summary, enriched_df = calculate_kpis(df)

            self.root.after(
                0,
                self._log_to_console,
                "Kurumsal Excel ve PDF raporları derleniyor...",
            )
            generate_report(
                kpis,
                region_summary,
                product_summary,
                monthly_summary,
                enriched_df,
                config,
            )
            generate_pdf_report(
                kpis,
                region_summary,
                product_summary,
                monthly_summary,
                config,
            )

            report_file = self.project_root / config["output_file"]
            archive_report(report_file, archive_folder)

            self.root.after(0, self.on_success)

        except ValueError as ve:
            logger.warning(f"Kullanıcı eylemi gerekli: {ve}")
            self.root.after(0, self.on_warning, str(ve))

        except PermissionError as pe:
            hata_mesaji = (
                "Input veya Output klasöründeki dosyalardan biri şu an kilitli!\n"
                "Lütfen açık olan tüm Excel/CSV/PDF dosyalarını kapatıp tekrar deneyin."
            )
            logger.error(f"Dosya kilitli hatası: {pe}")
            self.root.after(0, self.on_error, hata_mesaji)

        except UnicodeDecodeError as ue:
            hata_mesaji = (
                "Dosyalardan birinin formatı bozuk veya okunamıyor.\n"
                "Sadece geçerli Excel ve CSV dosyaları yüklediğinizden emin olun."
            )
            logger.error(f"Format hatası (Unicode): {ue}")
            self.root.after(0, self.on_error, hata_mesaji)

        except Exception as e:
            logger.exception(f"Kritik Hata: {e}")
            self.root.after(0, self.on_error, str(e))

    def on_success(self):
        self._log_to_console("İŞLEM BAŞARILI: Tüm raporlar oluşturuldu ve arşivlendi.")
        messagebox.showinfo(
            "Başarılı",
            "Tüm analizler tamamlandı.\nRaporlarınız başarıyla oluşturuldu ve arşivlendi.",
        )
        self._reset_buttons()

    def on_warning(self, msg):
        self._log_to_console(f"SİSTEM UYARISI: {msg}")
        messagebox.showwarning(
            "Eksik / Hatalı Veri",
            f"{msg}\n\nSol alttaki 'Input Klasörünü Aç' butonunu kullanarak dosyalarınızı kolayca kontrol edebilirsiniz.",
        )
        self._reset_buttons()

    def on_error(self, error_msg):
        self._log_to_console("KRİTİK HATA: İşlem durduruldu. Detaylar log dosyasındadır.")
        messagebox.showerror(
            "Sistem Hatası",
            f"Beklenmeyen bir sorun oluştu:\n{error_msg}\n\nDetaylar logs klasöründedir.",
        )
        self._reset_buttons()

    def _reset_buttons(self):
        self.run_btn.config(state=tk.NORMAL)
        self.btn_open_input.config(state=tk.NORMAL)


def main():
    setup_logger()
    root = tk.Tk()
    PartLedgerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()