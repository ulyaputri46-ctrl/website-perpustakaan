import firebase_admin
from firebase_admin import credentials, firestore

# Inisialisasi koneksi ke Firebase
try:
    cred = credentials.Certificate("maksum.json")  # pastikan path file ini benar
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Tes koneksi ke Firestore
    users_ref = db.collection("users")
    docs = list(users_ref.limit(1).stream())

    if docs:
        print("✅ Firebase Firestore terhubung! Koleksi 'users' memiliki data.")
    else:
        print("⚠️ Firebase Firestore terhubung, tapi koleksi 'users' masih kosong.")

except Exception as e:
    print(f"❌ Gagal terhubung ke Firebase Firestore: {e}")
