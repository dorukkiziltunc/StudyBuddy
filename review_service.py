import datetime
from typing import List, Dict, Any
import storage
import card_service
import deck_service

SRS_FILE = "srs_state.json"
REVIEW_LOG_FILE = "reviews.json"


def get_due_cards(user_id: int) -> List[Dict[str, Any]]:
    """
    Kullanıcının 'bugün' veya 'geçmişte' çalışması gereken kartları getirir.
    Bu fonksiyon 3 farklı JSON dosyasını birleştirmek (JOIN) zorundadır.
    """
    # 1. Kullanıcının destelerini bul
    user_decks = deck_service.get_user_decks(user_id)
    user_deck_ids = {d["id"] for d in user_decks}

    # 2. Bu destelerdeki kartları bul
    all_cards = storage.load_json(card_service.CARD_FILE)
    user_cards = {c["id"]: c for c in all_cards if c["deck_id"] in user_deck_ids}

    # 3. SRS durumlarını kontrol et
    srs_states = storage.load_json(SRS_FILE)
    today_str = datetime.date.today().isoformat()

    due_cards = []
    for state in srs_states:
        card_id = state["card_id"]

        # Eğer bu kart mevcut kullanıcınınsa
        if card_id in user_cards:
            next_date = state["next_review_date"]

            # Tarih gelmiş mi? (next_date <= today)
            if next_date <= today_str:
                # Kartın detaylarını SRS verisiyle birleştirip listeye ekle
                card_info = user_cards[card_id].copy()
                card_info.update(state)  # box, next_review_date bilgilerini ekle
                due_cards.append(card_info)

    return due_cards


def submit_review(card_id: int, quality: int) -> Dict[str, Any]:
    """
    SM-2 Algoritmasını uygular ve kartın yeni tarihini belirler.
    quality: 0 (Unuttum) - 5 (Çok Kolay) arası puan.
    """
    srs_states = storage.load_json(SRS_FILE)

    # İlgili kartın durumunu bul
    state_index = -1
    current_state = None
    for i, state in enumerate(srs_states):
        if state["card_id"] == card_id:
            current_state = state
            state_index = i
            break

    if not current_state:
        return {}  # Hata durumu

    # --- SM-2 ALGORİTMASI BAŞLANGICI ---
    # Mevcut değerleri al (yoksa varsayılanları kullan)
    repetition = current_state.get("box", 0)  # n
    ease_factor = current_state.get("ease_factor", 2.5)  # EF
    interval = current_state.get("interval", 0)  # I

    if quality >= 3:
        # Başarılı hatırlama
        if repetition == 0:
            interval = 1
        elif repetition == 1:
            interval = 6
        else:
            interval = int(interval * ease_factor)

        repetition += 1

        # Ease Factor Formülü: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        ef_modifier = (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease_factor = ease_factor + ef_modifier

        # EF 1.3'ten küçük olamaz
        if ease_factor < 1.3:
            ease_factor = 1.3

    else:
        # Başarısız (Unuttum) -> Başa dön
        repetition = 0
        interval = 1
        # Orijinal SM-2'de EF değişmez ama bazı varyasyonlarda azalır.
        # Biz basit tutup EF'yi ellemiyoruz.

    # Yeni tarih hesapla
    next_review = datetime.date.today() + datetime.timedelta(days=interval)

    # Durumu güncelle
    current_state["box"] = repetition
    current_state["ease_factor"] = round(ease_factor, 2)
    current_state["interval"] = interval
    current_state["next_review_date"] = next_review.isoformat()
    current_state["last_review_date"] = datetime.date.today().isoformat()
    # --- SM-2 BİTİŞ ---

    # Listeyi güncelle ve kaydet
    srs_states[state_index] = current_state
    storage.save_json(SRS_FILE, srs_states)

    # LOGLAMA (reviews.json)
    _log_review(card_id, quality, current_state)

    return current_state


def _log_review(card_id: int, quality: int, state: Dict[str, Any]):
    """Review geçmişini kaydeder."""
    logs = storage.load_json(REVIEW_LOG_FILE)
    log_entry = {
        "card_id": card_id,
        "review_date": datetime.datetime.now().isoformat(),
        "quality": quality,
        "new_box": state["box"],
        "new_interval": state["interval"]
    }
    logs.append(log_entry)
    storage.save_json(REVIEW_LOG_FILE, logs)