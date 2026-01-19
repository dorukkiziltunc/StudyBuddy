import hashlib
import os
import datetime
from typing import Optional, Dict, Any
import storage  # Oluşturduğumuz storage modülünü kullanıyoruz

USER_FILE = "users.json"


def _generate_salt() -> str:
    """Rastgele 16 byte'lık salt üretir ve hex string olarak döner."""
    return os.urandom(16).hex()


def _hash_password(password: str, salt_hex: str) -> str:
    """
    Verilen parolayı ve salt'ı kullanarak SHA256 ile hashler (PBKDF2).
    """
    password_bytes = password.encode('utf-8')
    salt_bytes = bytes.fromhex(salt_hex)

    # 100.000 iterasyon güvenli kabul edilir
    hash_bytes = hashlib.pbkdf2_hmac('sha256', password_bytes, salt_bytes, 100000)
    return hash_bytes.hex()


def register_user(email: str, password: str) -> bool:
    """
    Yeni kullanıcı kaydeder.
    Eğer email zaten varsa False döner. Başarılıysa True döner.
    """
    users = storage.load_json(USER_FILE)

    # 1. Email kontrolü (Unique Constraint)
    for user in users:
        if user["email"] == email:
            print("Hata: Bu e-posta adresi zaten kayıtlı.")
            return False

    # 2. Yeni ID üretimi (Artan sayaç mantığı)
    if users:
        new_id = max(user["id"] for user in users) + 1
    else:
        new_id = 1

    # 3. Güvenlik işlemleri
    salt = _generate_salt()
    pass_hash = _hash_password(password, salt)

    # 4. Kullanıcı nesnesini oluşturma
    new_user = {
        "id": new_id,
        "email": email,
        "password_hash": pass_hash,
        "salt": salt,
        "created_at": datetime.datetime.now().isoformat()
    }

    # 5. Kaydetme
    users.append(new_user)
    storage.save_json(USER_FILE, users)
    print(f"Kullanıcı başarıyla oluşturuldu! ID: {new_id}")
    return True


def login_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Giriş yapmayı dener.
    Başarılıysa kullanıcı sözlüğünü (dict) döner, başarısızsa None döner.
    """
    users = storage.load_json(USER_FILE)

    found_user = None
    for user in users:
        if user["email"] == email:
            found_user = user
            break

    if not found_user:
        print("Hata: Kullanıcı bulunamadı.")
        return None

    # Kayıtlı salt ile girilen şifreyi hashle
    stored_salt = found_user["salt"]
    stored_hash = found_user["password_hash"]

    calculated_hash = _hash_password(password, stored_salt)

    if calculated_hash == stored_hash:
        print(f"Giriş başarılı! Hoş geldin, {email}")
        return found_user
    else:
        print("Hata: Parola yanlış.")
        return None