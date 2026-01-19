# StudyBuddy - Aralıklı Tekrar Sistemi (SRS)

StudyBuddy, Python standart kütüphanesi kullanılarak geliştirilmiş, "Spaced Repetition" (Aralıklı Tekrar) algoritması (SM-2) ile çalışan bir çalışma kartı (flashcard) uygulamasıdır.

## 🚀 Özellikler

* **Güvenli Kimlik Doğrulama:** Tuzlama (Salt) ve Hash (PBKDF2) ile şifre saklama.
* **Aralıklı Tekrar (SM-2):** Kartların hatırlanma zorluğuna göre bir sonraki çalışma tarihini otomatik belirleme.
* **Veri Yönetimi:** Deste (Deck) ve Kart (Card) oluşturma, silme, listeleme.
* **Raporlama:** İlerleme durumunu gösteren detaylı istatistikler.
* **Saf Python:** Harici kütüphane (pip install) gerektirmez.

## 📂 Kurulum ve Çalıştırma

1. Proje klasörüne terminalden gidin.
2. Uygulamayı başlatın:
   ```bash
   python main.py
3. Menüden "2. Kayıt Ol" seçeneği ile kullanıcı oluşturun.
4. Giriş yaptıktan sonra destelerinizi oluşturup çalışmaya başlayabilirsiniz.

## 🏗️ Dosya Yapısı

main.py: Uygulamanın giriş noktası ve CLI arayüzü.

auth.py: Kullanıcı kayıt ve giriş işlemleri.

storage.py: JSON dosya okuma/yazma ve atomic write işlemleri.

deck_service.py / card_service.py: İçerik yönetimi.

review_service.py: SM-2 algoritması ve çalışma mantığı.

report_service.py: İstatistik hesaplamaları.

data/: Veritabanı dosyalarının (JSON) tutulduğu klasör.

## 🧪 Testler

Uygulama testleri unittest modülü ile yazılmıştır. Testleri çalıştırmak için:

Bash
python -m unittest discover tests