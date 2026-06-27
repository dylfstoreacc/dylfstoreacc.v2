import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from supabase import create_client, Client

app = Flask(__name__)

# ==========================================================================
# CONFIG & KONEKSI DB CLOUD SUPABASE
# ==========================================================================
# Pastikan kamu sudah mengisi Environment Variables ini di Render 
# atau memasukkan string URL & KEY Supabase milikmu secara langsung di sini.
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xyz.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "your-supabase-anon-key")

# Inisialisasi Klien Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Peringatan: Gagal terhubung ke Supabase. Log: {e}")
    supabase = None


# ==========================================================================
# ROUTE UTAMA (MEMUAT HALAMAN WEB)
# ==========================================================================
@app.route('/')
def home():
    # Merender template index.html siber buatan kita
    return render_template('index.html')


# ==========================================================================
# ENDPOINT API: AMBIL FOTO TESTIMONI SECARA DINAMIS
# ==========================================================================
@app.route('/api/testi/<kategori>')
def ambil_testi(kategori):
    # Memastikan hanya membaca kategori 'stok' atau 'rekber'
    if kategori not in ['stok', 'rekber']:
        return jsonify([])

    folder_target = os.path.join('static', 'testi', kategori)
    urls_gambar = []

    # Cek apakah folder tersebut eksis di server
    if os.path.exists(folder_target):
        for file in os.listdir(folder_target):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                # Buat format URL web yang valid untuk dibaca oleh JavaScript Frontend
                urls_gambar.append(f'/static/testi/{kategori}/{file}')
    
    return jsonify(urls_gambar)


# ==========================================================================
# ENDPOINT API: AMBIL ULASAN YANG SUDAH DI-APPROVED DARI SUPABASE
# ==========================================================================
@app.route('/ulasan', methods=['GET'])
def ambil_ulasan():
    if not supabase:
        return jsonify([])
    
    try:
        # Mengambil ulasan yang berstatus 'approved' dan diurutkan dari yang paling baru
        respon = supabase.table('ulasan')\
            .select('*')\
            .eq('status', 'approved')\
            .order('id', desc=True)\
            .execute()
        
        return jsonify(respon.data)
    except Exception as e:
        print(f"Error ambil data ulasan: {e}")
        return jsonify([])


# ==========================================================================
# ENDPOINT API: KONSUMEN TULIS ULASAN BARU (MASUK FILTER PENDING)
# ==========================================================================
@app.route('/tambah-ulasan', methods=['POST'])
def tambah_ulasan():
    if not supabase:
        return jsonify({'success': False, 'message': 'Sistem database belum terkonfigurasi.'})
    
    try:
        nama = request.form.get('nama', 'Anonim').strip()
        rating = int(request.form.get('rating', 5))
        text = request.form.get('text', '').strip()
        tanggal_sekarang = datetime.now().strftime('%d %b %Y')

        if not text:
            return jsonify({'success': False, 'message': 'Isi ulasan tidak boleh kosong.'})

        # Data ulasan baru yang akan dimasukkan ke tabel Supabase
        data_baru = {
            'nama': nama,
            'rating': rating,
            'text': text,
            'tanggal': tanggal_sekarang,
            'status': 'pending'  # Otomatis pending agar bisa kamu saring dulu lewat dashboard Supabase
        }

        supabase.table('ulasan').insert(data_baru).execute()
        
        return jsonify({
            'success': True, 
            'message': 'Ulasan berhasil terkirim! Menunggu persetujuan saringan admin Dileppp agar muncul live.'
        })
    except Exception as e:
        print(f"Error tambah ulasan baru: {e}")
        return jsonify({'success': False, 'message': 'Terjadi kesalahan sistem saat mengirim ulasan.'})


# ==========================================================================
# EKSEKUSI SERVER DINAMIS CLOUD (ANTI-ERROR PORT RENDER)
# ==========================================================================
if __name__ == '__main__':
    # Server Render akan otomatis mengisi variabel PORT lingkungan ini secara mandiri
    port = int(os.environ.get("PORT", 5000))
    # debug di-set False agar pengeksekusi gunicorn stabil & aman di server cloud
    app.run(host='0.0.0.0', port=port, debug=False)
