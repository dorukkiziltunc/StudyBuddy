import os
import sys
import time

# Yazdığımız modülleri dahil ediyoruz
import auth
import deck_service
import card_service
import review_service
import report_service

# Oturum durumunu tutan değişken
current_user = None


def clear_screen():
    """Ekranı temizler (İşletim sistemine göre)"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Uygulama başlığını yazar"""
    print("=" * 40)
    print("      STUDY BUDDY - CLI v1.0")
    print("=" * 40)


def menu_guest():
    """Giriş yapmamış kullanıcı menüsü"""
    while True:
        clear_screen()
        print_header()
        print("1. Giriş Yap")
        print("2. Kayıt Ol")
        print("3. Çıkış")
        print("-" * 20)

        choice = input("Seçiminiz: ").strip()

        if choice == "1":
            handle_login()
            if current_user: break  # Giriş başarılıysa döngüyü kır, ana menüye git
        elif choice == "2":
            handle_register()
        elif choice == "3":
            print("Güle güle!")
            sys.exit()
        else:
            input("Geçersiz seçim. Devam etmek için Enter...")


def handle_login():
    """Giriş işlemi"""
    global current_user
    print("\n--- GİRİŞ ---")
    email = input("E-posta: ").strip()
    password = input("Parola: ").strip()

    user = auth.login_user(email, password)
    if user:
        current_user = user
        input(f"Hoş geldin {user['email']}! Devam etmek için Enter...")
    else:
        input("Devam etmek için Enter...")


def handle_register():
    """Kayıt işlemi"""
    print("\n--- KAYIT ---")
    email = input("E-posta: ").strip()
    password = input("Parola: ").strip()

    if len(password) < 4:
        print("Hata: Parola en az 4 karakter olmalı.")
        input("Devam...")
        return

    success = auth.register_user(email, password)
    input("Devam etmek için Enter...")


def menu_main():
    """Giriş yapmış kullanıcı menüsü (Dashboard)"""
    global current_user

    while True:
        clear_screen()
        print_header()

        # Dashboard İstatistikleri

        stats = report_service.get_dashboard_stats(current_user["id"])
        print(f"Kullanıcı: {current_user['email']}")
        print(f"Desteler: {stats['total_decks']} | Kartlar: {stats['total_cards']}")
        print(f"BUGÜN ÇALIŞILACAK KART SAYISI: {stats['due_count']}")
        print("=" * 40)

        print("1. ÇALIŞMAYA BAŞLA (Review Session)")
        print("2. Deste Yönetimi")
        print("3. Kart Yönetimi")
        print("4. Detaylı Rapor")
        print("5. Çıkış Yap (Logout)")

        choice = input("\nSeçiminiz: ").strip()

        if choice == "1":
            flow_review_session()
        elif choice == "2":
            flow_deck_management()
        elif choice == "3":
            flow_card_management()
        elif choice == "4":
            flow_reports()
        elif choice == "5":

            current_user = None
            break
        else:
            input("Geçersiz seçim...")


def flow_review_session():
    """Çalışma (Review) Akışı"""
    clear_screen()
    print("--- ÇALIŞMA ZAMANI ---")

    due_cards = review_service.get_due_cards(current_user["id"])

    if not due_cards:
        print("Tebrikler! Bugün çalışman gereken tüm kartları bitirdin. 🎉")
        input("Ana menüye dönmek için Enter...")
        return

    print(f"Toplam {len(due_cards)} kart çalışılacak.\n")

    for idx, card in enumerate(due_cards, 1):
        clear_screen()
        print(f"Kart {idx} / {len(due_cards)}")
        print("-" * 30)
        print(f"SORU:\n{card['front']}")
        print("-" * 30)

        input("Cevabı görmek için Enter'a bas...")

        print(f"\nCEVAP:\n{card['back']}")
        print("-" * 30)

        while True:
            try:
                score = int(input("Kendini puanla (0=Unuttum ... 5=Mükemmel): "))
                if 0 <= score <= 5:
                    break
                print("Lütfen 0 ile 5 arasında bir sayı gir.")
            except ValueError:
                print("Lütfen sayı gir.")

        # Review sonucunu kaydet
        review_service.submit_review(card["id"], score)
        print("Kaydedildi!")
        time.sleep(0.5)

    print("\nOturum tamamlandı! Harika iş çıkardın.")
    input("Devam...")


def flow_deck_management():
    """Deste ekleme/silme/listeleme"""
    while True:
        clear_screen()
        print("--- DESTE YÖNETİMİ ---")
        decks = deck_service.get_user_decks(current_user["id"])

        if decks:
            for d in decks:
                print(f"[ID: {d['id']}] {d['name']}")
        else:
            print("Henüz hiç deste yok.")

        print("\n1. Yeni Deste Ekle")
        print("2. Deste Sil")
        print("3. Geri Dön")

        choice = input("Seçim: ").strip()

        if choice == "1":
            name = input("Deste Adı: ").strip()
            if name:
                deck_service.create_deck(current_user["id"], name)
                input("Deste oluşturuldu. Enter...")
        elif choice == "2":
            try:
                d_id = int(input("Silinecek Deste ID: "))
                if deck_service.delete_deck(d_id, current_user["id"]):
                    input("Silindi. Enter...")
                else:
                    input("Silinemedi. Enter...")
            except ValueError:
                input("Geçersiz ID.")
        elif choice == "3":
            break


def flow_card_management():
    """Kart ekleme/silme işlemleri"""
    while True:
        clear_screen()
        print("--- KART YÖNETİMİ ---")

        # Önce deste seçilmeli
        decks = deck_service.get_user_decks(current_user["id"])
        if not decks:
            print("Önce bir deste oluşturmalısın!")
            input("Geri dön...")
            break

        print("Hangi destede işlem yapacaksın?")
        for d in decks:
            print(f"[ID: {d['id']}] {d['name']}")
        print("0. Geri Dön")

        try:
            deck_choice = int(input("Deste ID seç: "))
            if deck_choice == 0: break

            # Seçilen destenin varlığını kontrol et
            selected_deck = next((d for d in decks if d["id"] == deck_choice), None)
            if not selected_deck:
                input("Böyle bir deste yok.")
                continue

            _card_submenu(selected_deck)

        except ValueError:
            input("Sayı girmelisin.")


def _card_submenu(deck):
    """Seçilen deste içindeki kart işlemleri"""
    while True:
        clear_screen()
        print(f"--- DESTE: {deck['name']} ---")
        cards = card_service.get_cards_by_deck(deck["id"])

        print(f"Toplam Kart: {len(cards)}")
        for c in cards:
            # Sığdırmak için ön yüzü kırp
            front_preview = (c['front'][:30] + '..') if len(c['front']) > 30 else c['front']
            print(f"[ID: {c['id']}] {front_preview}")

        print("\n1. Yeni Kart Ekle")
        print("2. Kart Sil")
        print("3. Geri Dön")

        choice = input("Seçim: ")

        if choice == "1":
            print("\n(İpucu: İptal etmek için boş bırakıp Enter'a bas)")
            front = input("Soru (Ön Yüz): ").strip()
            if not front: continue
            back = input("Cevap (Arka Yüz): ").strip()

            card_service.create_card(deck["id"], front, back)
            input("Kart eklendi! Enter...")

        elif choice == "2":
            try:
                c_id = int(input("Silinecek Kart ID: "))
                # Kartın bu desteye ait olduğunu kontrol etmek iyi olurdu ama
                # şimdilik global ID ile siliyoruz (basitlik için)
                if card_service.delete_card(c_id):
                    input("Kart silindi. Enter...")
                else:
                    input("Kart bulunamadı. Enter...")
            except ValueError:
                input("Geçersiz giriş.")
        elif choice == "3":
            break


def flow_reports():
    """Detaylı rapor ekranı"""
    clear_screen()
    print("--- DETAYLI RAPOR ---")

    box_stats = report_service.get_progress_stats(current_user["id"])

    print("\nÖğrenme Durumu (Kutu Dağılımı):")
    print(f"Kutu 1 (Yeni/Zor):      {box_stats.get(1, 0)} kart")
    print(f"Kutu 2 (Biraz Tanıdık): {box_stats.get(2, 0)} kart")
    print(f"Kutu 3 (İyi):           {box_stats.get(3, 0)} kart")
    print(f"Kutu 4 (Çok İyi):       {box_stats.get(4, 0)} kart")
    print(f"Kutu 5 (Mükemmel):      {box_stats.get(5, 0)} kart")
    print(f"Kutu 6+ (Uzman):        {box_stats.get('6+', 0)} kart")

    print("\n" + "-" * 30)
    input("Menüye dönmek için Enter...")


if __name__ == "__main__":
    # Uygulama döngüsü
    while True:
        if current_user:
            menu_main()
        else:
            menu_guest()