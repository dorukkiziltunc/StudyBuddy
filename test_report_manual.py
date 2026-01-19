import auth
import report_service

# Giriş yap
user = auth.login_user("test@example.com", "123456")

if user:
    print(f"\n--- Rapor Testi: {user['email']} ---")

    # 1. Genel Özet
    stats = report_service.get_dashboard_stats(user["id"])
    print("GENEL DURUM:")
    print(f"- Toplam Deste: {stats['total_decks']}")
    print(f"- Toplam Kart: {stats['total_cards']}")
    print(f"- Bugün Çalışılacak: {stats['due_count']}")  # Az önceki testten sonra 1 kalmalı

    # 2. İlerleme Durumu (Kutu Dağılımı)
    print("\nİLERLEME DURUMU (Öğrenme Seviyesi):")
    box_stats = report_service.get_progress_stats(user["id"])
    for box, count in box_stats.items():
        if count > 0:
            print(f"Kutu {box}: {count} kart")

else:
    print("Giriş başarısız.")