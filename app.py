from flask import Flask, render_template, request, jsonify
from supabase.client import ClientOptions
from supabase import create_client, Client
from datetime import datetime
import os

app = Flask(__name__)

# ==========================================================================
# 1. KONFIGURASI GERBANG CLOUD DATABASE SUPABASE (FIX CONFURGATION BENTROK SDK)
# ==========================================================================
SUPABASE_URL = "https://pydgbguisbkjzgoixrir.supabase.co"
SUPABASE_KEY = "eyJhY2ciOiI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInN1YiI6Im1vYjE1NzY5ImV4cCI6MTFubFub24lc2lyb252b4cmlyIiwiY210IiwicXQiOjE3MDg2YmJN5ZGdiZ3Vpc2Jranpnb2l4cmlyR2F2Fl2Kliejo"

# FIX SAKTI: Memaksa ClientOptions mengabaikan konfigurasi proxy otomatis bawaan SDK lama yang bikin crash
opsi_siber = ClientOptions(
    postgrest_client_timeout=10,
    storage_client_timeout=10
)

# Buat client dengan menyuntikkan opsi bersih bebas bentrok
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=opsi_siber)


# ==========================================================================
# 2. RUTE UTAMA & API TESTIMONI BERDASARKAN WAKTU UPLOAD TERBARU (DESCENDING)
# ==========================================================================

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/testi/<kategori>', methods=['GET'])
def ambil_foto_testimoni(kategori):
    try:
        folder_path = os.path.join('static', 'testi', kategori)
        if not os.path.exists(folder_path):
            return jsonify([])
            
        daftar_file = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        file_dengan_waktu = []
        for file_name in daftar_file:
            full_path = os.path.join(folder_path, file_name)
            waktu_modifikasi = os.path.getmtime(full_path)
            file_dengan_waktu.append((file_name, waktu_modifikasi))
            
        file_dengan_waktu.sort(key=lambda x: x[1], reverse=True)
        urls_gambar = [f'/static/testi/{kategori}/{x[0]}' for x in file_dengan_waktu]
        return jsonify(urls_gambar)
    except Exception as e:
        return jsonify([])


# ==========================================================================
# 3. JALUR AMBIL & KIRIM ULASAN REAL-TIME DENGAN NOTIF AUTOMATION TANGGAL
# ==========================================================================

@app.route('/ulasan', methods=['GET'])
def ambil_ulasan():
    try:
        respon = supabase.table('ulasan').select('*').eq('status', 'approved').order('id', desc=True).execute()
        return jsonify(respon.data)
    except Exception as e:
        return jsonify([])


@app.route('/tambah-ulasan', methods=['POST'])
def tambah_ulasan():
    try:
        nama = request.form.get('nama')
        rating = int(request.form.get('rating', 5))
        text = request.form.get('text')
        
        tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        data_ulasan = {
            "nama": nama,
            "rating": rating,
            "text": text,
            "tanggal": tanggal_sekarang,
            "status": "approved"
        }
        
        supabase.table('ulasan').insert(data_ulasan).execute()
        return jsonify({"success": True, "message": f"🌱 Transaksi Berhasil! Ulasan siber {nama} sukses disuntikkan ke cloud database!"})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ==========================================================================
# 4. PEMICU JALUR SERVER PRODUCTION RENDER
# ==========================================================================
if __name__ == '__main__':
    port_render = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port_render, debug=False)
