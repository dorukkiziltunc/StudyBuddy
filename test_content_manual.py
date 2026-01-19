import deck_service
import card_service
import auth

# Önce giriş yapalım (Daha önce oluşturduğun kullanıcıyla)
# Eğer users.json duruyorsa aynı maili kullanabilirsin.
# Durmuyorsa önce register_user çalıştır.
email = "test@example.com"
user = auth.login_user(email, "123456")

if user:
    user_id = user["id"]
    print(f"\n--- Giriş Yapıldı: User ID {user_id} ---")

    # 1. Deste Oluşturma
    print("\n--- Deste Oluşturuluyor ---")
    my_deck = deck_service.create_deck(user_id, "Python Temelleri")
    deck_id = my_deck["id"]

    # 2. Kart Ekleme
    print("\n--- Kartlar Ekleniyor ---")
    card_service.create_card(deck_id, "print() ne işe yarar?", "Ekrana çıktı verir.")
    card_service.create_card(deck_id, "len() ne döner?", "Listenin uzunluğunu.")

    # 3. Listeleme
    print(f"\n--- {my_deck['name']} Destesindeki Kartlar ---")
    cards = card_service.get_cards_by_deck(deck_id)
    for c in cards:
        print(f"Soru: {c['front']} - Cevap: {c['back']}")

else:
    print("Giriş yapılamadı, lütfen users.json dosyasını kontrol et.")