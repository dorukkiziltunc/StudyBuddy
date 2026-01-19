import datetime
from typing import List, Dict, Any, Optional
import storage

DECK_FILE = "decks.json"
CARD_FILE = "cards.json"  # Silme işlemi için lazım olacak


def create_deck(user_id: int, name: str) -> Dict[str, Any]:
    """
    Yeni bir deste oluşturur ve kaydeder.
    """
    decks = storage.load_json(DECK_FILE)

    # Yeni ID üretimi
    new_id = 1
    if decks:
        new_id = max(d["id"] for d in decks) + 1

    new_deck = {
        "id": new_id,
        "user_id": user_id,
        "name": name,
        "created_at": datetime.datetime.now().isoformat()
    }

    decks.append(new_deck)
    storage.save_json(DECK_FILE, decks)
    print(f"Deste oluşturuldu: {name}")
    return new_deck


def get_user_decks(user_id: int) -> List[Dict[str, Any]]:
    """
    Sadece belirtilen kullanıcıya ait desteleri listeler.
    """
    decks = storage.load_json(DECK_FILE)
    # List comprehension ile filtreleme
    user_decks = [d for d in decks if d["user_id"] == user_id]
    return user_decks


def delete_deck(deck_id: int, user_id: int) -> bool:
    """
    Desteyi ve (opsiyonel ama önerilen) içindeki kartları siler.
    Sadece destenin sahibi silebilir.
    """
    decks = storage.load_json(DECK_FILE)

    # Desteyi bul ve sahibi mi kontrol et
    deck_to_delete = None
    for d in decks:
        if d["id"] == deck_id and d["user_id"] == user_id:
            deck_to_delete = d
            break

    if not deck_to_delete:
        print("Hata: Deste bulunamadı veya silme yetkiniz yok.")
        return False

    # 1. Desteyi listeden çıkar
    decks.remove(deck_to_delete)
    storage.save_json(DECK_FILE, decks)

    # 2. (Bonus) Bu desteye ait kartları da temizle
    # Bu işlem veri tutarlılığı için önemlidir.
    cards = storage.load_json(CARD_FILE)
    new_cards = [c for c in cards if c["deck_id"] != deck_id]

    if len(cards) != len(new_cards):
        storage.save_json(CARD_FILE, new_cards)
        print(f"Desteye ait {len(cards) - len(new_cards)} kart da silindi.")

    print("Deste başarıyla silindi.")
    return True