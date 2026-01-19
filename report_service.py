import storage
import card_service
import deck_service
import review_service

SRS_FILE = "srs_state.json"
REVIEW_FILE = "reviews.json"


def get_dashboard_stats(user_id: int) -> dict:
    """
    Ana ekran için özet istatistikler döner.
    """
    # 1. Kullanıcının desteleri
    decks = deck_service.get_user_decks(user_id)
    deck_ids = {d["id"] for d in decks}

    # 2. Toplam kart sayısı
    all_cards = storage.load_json(card_service.CARD_FILE)
    user_card_count = sum(1 for c in all_cards if c["deck_id"] in deck_ids)

    # 3. Çalışılması gereken (Due) kart sayısı
    # review_service'deki fonksiyonu tekrar kullanabiliriz ama
    # performans için sadece sayısını bulmak yeterli.
    due_cards = review_service.get_due_cards(user_id)

    return {
        "total_decks": len(decks),
        "total_cards": user_card_count,
        "due_count": len(due_cards)
    }


def get_progress_stats(user_id: int) -> dict:
    """
    Kutulara (Boxes) göre dağılımı gösterir.
    Örn: Kutu 1 (Yeni): 10 kart, Kutu 5 (Uzman): 2 kart
    """
    # Kullanıcıya ait kart ID'lerini bul
    decks = deck_service.get_user_decks(user_id)
    deck_ids = {d["id"] for d in decks}
    all_cards = storage.load_json(card_service.CARD_FILE)
    user_card_ids = {c["id"] for c in all_cards if c["deck_id"] in deck_ids}

    # SRS durumlarını incele
    srs_data = storage.load_json(SRS_FILE)

    # İstatistik sözlüğü (Kutu numarası -> Kart sayısı)
    box_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, "6+": 0}

    for state in srs_data:
        if state["card_id"] in user_card_ids:
            box = state.get("box", 1)

            if box >= 6:
                box_stats["6+"] += 1
            else:
                # Eğer box anahtarı yoksa 1 varsay (güvenlik için)
                if box in box_stats:
                    box_stats[box] += 1
                else:
                    # Beklenmedik durum (Box 0 veya negatif ise 1'e say)
                    box_stats[1] += 1

    return box_stats