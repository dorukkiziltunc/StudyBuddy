import auth

print("--- TEST 1: Kayıt ---")
auth.register_user("test@example.com", "123456")

print("\n--- TEST 2: Aynı mail ile tekrar kayıt (Hata vermeli) ---")
auth.register_user("test@example.com", "yeni_sifre")

print("\n--- TEST 3: Yanlış giriş ---")
user = auth.login_user("test@example.com", "yanlis_sifre")

print("\n--- TEST 4: Doğru giriş ---")
user = auth.login_user("test@example.com", "123456")
if user:
    print("User Data:", user)