import json
import os
import pathlib
from typing import List, Any

# Verilerin tutulacağı klasör adı
DATA_DIR = pathlib.Path("data")


def _ensure_data_dir():
    """Data klasörünün varlığını kontrol eder, yoksa oluşturur."""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filename: str) -> List[Any]:
    """
    Verilen JSON dosyasını okur ve listeyi döndürür.
    Dosya yoksa veya bozuksa boş liste döndürür.
    """
    file_path = DATA_DIR / filename

    # Dosya yoksa boş liste dön (uygulama çökmez)
    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Dosya bozuksa veya okunamıyorsa boş liste dön (loglama eklenebilir)
        return []


def save_json(filename: str, data: List[Any]) -> None:
    """
    Veriyi JSON formatında dosyaya kaydeder.
    Atomic Write (tmp -> replace) yöntemini kullanır.
    """
    _ensure_data_dir()

    file_path = DATA_DIR / filename
    tmp_path = file_path.with_suffix(".tmp")

    try:
        # Önce geçici dosyaya yaz
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Yazma başarılıysa, asıl dosyanın üzerine taşı (Atomic Operation)
        # Windows/Linux uyumlu olması için os.replace tercih edilir
        os.replace(tmp_path, file_path)
    except IOError as e:
        print(f"Hata: Veri kaydedilemedi. {e}")
        # Hata durumunda tmp dosyası temizlenebilir
        if tmp_path.exists():
            os.remove(tmp_path)