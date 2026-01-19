import review_service
import auth
import datetime

# 1. Giriş
user = auth.login_user("test@example.com", "123456")
if not user:
    print("Giriş başarısız. Önceki adımları kontrol et.")
    exit()

print(f"\n--- Kullanıcı: {user['email']} ---")

# 2. Çalışılacak Kartları Getir (Bugün eklediklerimiz gelmeli)
print("\n--- Çalışılacak Kartlar (Due Cards) ---")
due_cards = review_service.get_due_cards(user["id"])
print(f"Bulunan kart sayısı: {len(due_cards)}")

if due_cards:
    first_card = due_cards[0]
    card_id = first_card["id"]
    print(f"Seçilen Kart ID: {card_id}")
    print(f"Soru: {first_card['front']}")
    print(f"Şu anki Box: {first_card['box']}")
    print(f"Hedef Tarih (Eski): {first_card['next_review_date']}")

    # 3. Review İşlemi (Simülasyon)
    # 5 Puan (Mükemmel) verelim
    print("\n--- Review Gönderiliyor: Puan 5 (Mükemmel) ---")
    new_state = review_service.submit_review(card_id, 5)

    print(f"Yeni Box (Repetition): {new_state['box']} (Beklenen: 1 artmalı)")
    print(f"Yeni Interval: {new_state['interval']} gün")
    print(f"Yeni Hedef Tarih: {new_state['next_review_date']}")

    # Tarih bugünden ileri mi?
    today = datetime.date.today().isoformat()
    if new_state["next_review_date"] > today:
        print("BAŞARILI: Kart ileri tarihe atıldı! ✅")
    else:
        print("HATA: Tarih güncellenmedi! ❌")

    # 4. Tekrar Sorgula (Artık listede olmamalı)
    print("\n--- Tekrar Sorgulanıyor ---")
    due_cards_after = review_service.get_due_cards(user["id"])
    print(f"Kalan kart sayısı: {len(due_cards_after)}")

else:
    print("HATA: Hiç kart bulunamadı! Önceki adımda kart eklediğinden emin misin?")