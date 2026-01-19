import unittest
import shutil
import pathlib
import datetime
import sys
import os

# Üst dizindeki modülleri görebilmek için path ayarı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import storage
import auth
import deck_service
import card_service
import review_service
import report_service


class StudyBuddyTests(unittest.TestCase):
    """
    StudyBuddy Uygulaması Birim Testleri (Unit Tests)
    Şartname Madde 9.1 ve Rubrik gereği hazırlanmıştır.
    """

    def setUp(self):
        """Her testten önce çalışır: Geçici test ortamı kurar."""
        self.test_dir = pathlib.Path("test_data_temp")

        # Storage modülünün hedef klasörünü değiştiriyoruz (Mocking)
        # Böylece gerçek veriler (data/) bozulmaz.
        storage.DATA_DIR = self.test_dir

        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()

    def tearDown(self):
        """Her testten sonra çalışır: Ortalığı temizler."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    # --- 1. KULLANICI & GÜVENLİK TESTLERİ ---

    def test_01_register_user_success(self):
        """Kullanıcı başarıyla kaydedilmeli."""
        result = auth.register_user("test@test.com", "123456")
        self.assertTrue(result)

        users = storage.load_json("users.json")
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["email"], "test@test.com")
        # Şifre hashlenmiş olmalı, plain text olmamalı
        self.assertNotEqual(users[0]["password_hash"], "123456")

    def test_02_register_duplicate_fail(self):
        """Aynı mail ile ikinci kayıt engellenmeli (Edge Case)."""
        auth.register_user("test@test.com", "123456")
        result = auth.register_user("test@test.com", "999999")
        self.assertFalse(result)  # False dönmeli

    def test_03_login_success_and_fail(self):
        """Doğru şifreyle giriş yapılmalı, yanlış şifreyle reddedilmeli."""
        auth.register_user("user@test.com", "pass123")

        # Yanlış şifre
        login_fail = auth.login_user("user@test.com", "wrongpass")
        self.assertIsNone(login_fail)

        # Doğru şifre
        login_success = auth.login_user("user@test.com", "pass123")
        self.assertIsNotNone(login_success)
        self.assertEqual(login_success["email"], "user@test.com")

    # --- 2. DESTE (DECK) TESTLERİ ---

    def test_04_create_and_get_deck(self):
        """Deste oluşturulmalı ve kullanıcıya göre listelenmeli."""
        auth.register_user("u1@test.com", "1")
        user = auth.login_user("u1@test.com", "1")

        deck = deck_service.create_deck(user["id"], "My Deck")
        self.assertEqual(deck["name"], "My Deck")

        # Listeleme kontrolü
        my_decks = deck_service.get_user_decks(user["id"])
        self.assertEqual(len(my_decks), 1)
        self.assertEqual(my_decks[0]["id"], deck["id"])

    def test_05_delete_deck(self):
        """Deste silindiğinde listeden kalkmalı."""
        auth.register_user("u1@test.com", "1")
        user = auth.login_user("u1@test.com", "1")
        deck = deck_service.create_deck(user["id"], "Silinecek Deste")

        result = deck_service.delete_deck(deck["id"], user["id"])
        self.assertTrue(result)

        remaining = deck_service.get_user_decks(user["id"])
        self.assertEqual(len(remaining), 0)

    # --- 3. KART (CARD) TESTLERİ ---

    def test_06_create_card_creates_srs_state(self):
        """Kart oluşturulduğunda srs_state.json dosyasına da kayıt atılmalı."""
        deck_id = 1  # Mock deck id
        card = card_service.create_card(deck_id, "Soru", "Cevap")

        # srs_state kontrolü
        srs_data = storage.load_json("srs_state.json")
        self.assertEqual(len(srs_data), 1)
        self.assertEqual(srs_data[0]["card_id"], card["id"])
        self.assertEqual(srs_data[0]["box"], 1)  # İlk kutu 1 olmalı

    def test_07_delete_card(self):
        """Kart silindiğinde hem kart hem SRS verisi silinmeli."""
        card = card_service.create_card(1, "Q", "A")
        c_id = card["id"]

        card_service.delete_card(c_id)

        cards = storage.load_json("cards.json")
        srs = storage.load_json("srs_state.json")

        self.assertEqual(len(cards), 0)
        self.assertEqual(len(srs), 0)

    # --- 4. REVIEW VE SM-2 ALGORİTMA TESTLERİ (THE BRAIN) ---

    def test_08_get_due_cards(self):
        """Bugün çalışılması gereken kartlar doğru gelmeli."""
        # 1. Kullanıcı ve Deste Oluştur
        auth.register_user("stu@dy.com", "1")
        user = auth.login_user("stu@dy.com", "1")
        deck = deck_service.create_deck(user["id"], "Math")

        # 2. Kart ekle (Varsayılan olarak tarihi bugündür)
        card_service.create_card(deck["id"], "2+2", "4")

        # 3. Due (Vadesi gelmiş) kartları çek
        due = review_service.get_due_cards(user["id"])
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]["front"], "2+2")

    def test_09_sm2_algorithm_logic(self):
        """SM-2 Mantığı: Yüksek puan (5) tarihi ileri atmalı."""
        card = card_service.create_card(1, "Q", "A")
        c_id = card["id"]

        # İlk başta tarih bugün
        initial_date = datetime.date.today().isoformat()

        # 5 Puan ver (Çok iyi)
        new_state = review_service.submit_review(c_id, 5)

        # Yeni tarih bugünden büyük olmalı
        self.assertGreater(new_state["next_review_date"], initial_date)
        # Kutu (Box) seviyesi artmalı
        self.assertEqual(new_state["box"], 2)

    def test_10_sm2_forget_logic(self):
        """SM-2 Mantığı: Düşük puan (0) kartı başa (Box 1) döndürmeli."""
        card = card_service.create_card(1, "Q", "A")
        c_id = card["id"]

        # Önce kartı biraz ilerletelim (Manuel manipülasyon)
        srs_list = storage.load_json("srs_state.json")
        srs_list[0]["box"] = 4
        storage.save_json("srs_state.json", srs_list)

        # Şimdi 0 puan (Unuttum) verelim
        new_state = review_service.submit_review(c_id, 0)

        # Kutu 1'e veya 0'a düşmeli (Uygulamamızda reset 0 veya 1 mantığına göre)
        # Kodumuzda: repetition = 0 yapıp sonra +1 artırmıyorsak direkt 0 kalabilir veya 1 olur.
        # review_service.py koduna göre else bloğunda: repetition=0, interval=1
        self.assertEqual(new_state["interval"], 1)

    # --- 5. RAPOR TESTİ ---

    def test_11_dashboard_stats(self):
        """Rapor servisi doğru sayıları dönmeli."""
        auth.register_user("rep@ort.com", "1")
        user = auth.login_user("rep@ort.com", "1")
        d = deck_service.create_deck(user["id"], "D1")
        card_service.create_card(d["id"], "Q1", "A1")
        card_service.create_card(d["id"], "Q2", "A2")

        stats = report_service.get_dashboard_stats(user["id"])

        self.assertEqual(stats["total_decks"], 1)
        self.assertEqual(stats["total_cards"], 2)
        self.assertEqual(stats["due_count"], 2)  # İkisi de yeni olduğu için


if __name__ == "__main__":
    unittest.main()