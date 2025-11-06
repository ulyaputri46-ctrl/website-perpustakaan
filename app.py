from flask import Flask, render_template, request, redirect, url_for, flash, session
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests
import json

app = Flask(__name__)
app.secret_key = "rahasia-aman"

# ========= INISIALISASI FIREBASE =========
cred = credentials.Certificate("maksum.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

FIREBASE_API_KEY = "AIzaSyAlAwr6Acnt8W0RYaPxCbAg4BJbLZVcANE"


# ========= ROUTE ROOT =========
@app.route('/')
def home():
    return redirect(url_for('login'))


# ========= REGISTER =========
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash("Password tidak cocok!", "danger")
            return redirect(url_for('register'))

        try:
            user = auth.create_user(email=email, password=password)
            db.collection('users').document(user.uid).set({'email': email})
            flash("Registrasi berhasil! Silakan login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Gagal mendaftar: {e}", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')


# ========= LOGIN =========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
            payload = {"email": email, "password": password, "returnSecureToken": True}
            r = requests.post(url, json=payload)
            data = r.json()

            if 'idToken' in data:
                session['user'] = email
                flash("Login berhasil!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash(data.get('error', {}).get('message', 'Login gagal'), 'danger')
                return redirect(url_for('login'))
        except Exception as e:
            flash(f"Terjadi kesalahan: {e}", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


# ========= DASHBOARD =========
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Silakan login terlebih dahulu.", "warning")
        return redirect(url_for('login'))

    # Ambil semua buku dari Firestore
    books = db.collection('books').stream()
    daftar_buku = [{'id': doc.id, **doc.to_dict()} for doc in books]

    return render_template('dashboard.html', user=session['user'], books=daftar_buku)


# ========= TAMBAH BUKU =========
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        judul = request.form['judul']
        penulis = request.form['penulis']
        tahun = request.form['tahun']

        db.collection('books').add({
            'judul': judul,
            'penulis': penulis,
            'tahun': tahun
        })
        flash("Buku berhasil ditambahkan!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_book.html')


# ========= EDIT BUKU =========
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_book(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    book_ref = db.collection('books').document(id)
    book = book_ref.get().to_dict()

    if request.method == 'POST':
        judul = request.form['judul']
        penulis = request.form['penulis']
        tahun = request.form['tahun']
        book_ref.update({'judul': judul, 'penulis': penulis, 'tahun': tahun})
        flash("Buku berhasil diperbarui!", "info")
        return redirect(url_for('dashboard'))

    return render_template('edit_book.html', book=book, id=id)


# ========= HAPUS BUKU =========
@app.route('/delete/<id>')
def delete_book(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    db.collection('books').document(id).delete()
    flash("Buku berhasil dihapus!", "danger")
    return redirect(url_for('dashboard'))


# ========= LOGOUT =========
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Berhasil logout.", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
