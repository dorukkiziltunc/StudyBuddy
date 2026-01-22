import datetime
from typing import List, Dict, Any
import storage

CARD_FILE = "cards.json"
SRS_FILE = "srs_state.json"


def create_card(deck_id: int, front: str, back: str) -> Dict[str, Any]:
    """
    Yeni kart oluşturur.
    AYNI ZAMANDA srs_state.json dosyasına başlangıç takip verisini ekler.
    """
    cards = storage.load_json(CARD_FILE)
    srs_data = storage.load_json(SRS_FILE)

    # Yeni ID üretimi
    new_id = 1
    if cards:
        new_id = max(c["id"] for c in cards) + 1

    # 1. Kart İçeriği
    new_card = {
        "id": new_id,
        "deck_id": deck_id,
        "front": front,
        "back": back,
        "created_at": datetime.datetime.now().isoformat()
    }

    # 2. SRS Başlangıç Durumu (Kutu 1, Bugün çalışılmalı)
    initial_srs = {
        "card_id": new_id,
        "box": 1,  # 1. Kutu (Her gün)
        "next_review_date": datetime.date.today().isoformat(),  # Hemen başla
        "last_review_date": None
    }

    cards.append(new_card)
    srs_data.append(initial_srs)

    storage.save_json(CARD_FILE, cards)
    storage.save_json(SRS_FILE, srs_data)

    print(f"Kart eklendi (ID: {new_id})")
    return new_card


def get_cards_by_deck(deck_id: int) -> List[Dict[str, Any]]:
    """
    Bir desteye ait kartları listeler.
    """
    cards = storage.load_json(CARD_FILE)
    deck_cards = [c for c in cards if c["deck_id"] == deck_id]
    return deck_cards


def update_card(card_id: int, new_front: str, new_back: str, user_id: int) -> bool:
    """
    Kartı günceller. (Sahiplik kontrolü için user_id gerekebilir ama şimdilik basitleştirdik)
    """
    cards = storage.load_json(CARD_FILE)

    for card in cards:
        if card["id"] == card_id:
            card["front"] = new_front
            card["back"] = new_back
            storage.save_json(CARD_FILE, cards)
            print("Kart güncellendi.")
            return True

    print("Kart bulunamadı.")
    return False


def delete_card(card_id: int) -> bool:
    """
    Kartı ve SRS durumunu siler.
    """
    cards = storage.load_json(CARD_FILE)
    srs_data = storage.load_json(SRS_FILE)

    # Kartı bul ve sil
    original_len = len(cards)
    cards = [c for c in cards if c["id"] != card_id]

    if len(cards) == original_len:
        print("Kart bulunamadı.")
        return False

    # SRS verisini de temizle
    srs_data = [s for s in srs_data if s["card_id"] != card_id]

    storage.save_json(CARD_FILE, cards)
    storage.save_json(SRS_FILE, srs_data)
    print("Kart silindi.")
    return True
