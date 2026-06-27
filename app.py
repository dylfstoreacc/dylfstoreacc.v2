from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

# ==========================================================================
# 1. KONFIGURASI GERBANG CLOUD DATABASE SUPABASE
# ==========================================================================
SUPABASE_URL = "https://pydgbguisbkjzgoixrir.supabase.co"
SUPABASE_KEY = "eyJhY2ciOiI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInN1YiI6Im1vYjE1NzY5ImV4cCI6MTFubFub24lc2lyb252b4cmlyIiwiY210IiwicXQiOjE3MDg2YmJN5ZGdiZ3Vpc2Jranpnb2l4cmlyR2F2Fl2Kliejo"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==========================================================================
# 2. RUTE UTAMA & API TESTIMONI BERDASARKAN WAKTU UPLOAD TERBARU (DESCENDING)
# ==========================================================================

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/testi/<kategori>', methods=['GET'])
def ambil_foto_testimoni(kategori):
    """
    Fungsi khusus menyisir file testimoni dan mengurutkannya secara mutlak
    berdasarkan waktu modifikasi/upload file terakhir (paling baru di atas).
    """
    try:
        folder_path = os.path.join('static', 'testi', kategori)
        
        if not os.path.exists(folder_path):
            return jsonify([])
            
        # Saring file yang murni berformat gambar saja (.png, .jpg, .jpeg)
        daftar_file = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        # Pasangkan nama file dengan waktu modifikasi terakhirnya di komputer
        file_dengan_waktu = []
        for file_name in daftar_file:
            full_path = os.path.join(folder_path, file_name)
            waktu_modifikasi = os.path.getmtime(full_path)
            file_dengan_waktu.append((file_name, waktu_modifikasi))
            
        # Urutkan secara Descending (Menurun) berdasarkan waktu modifikasi
        file_dengan_waktu.sort(key=lambda x: x[1], reverse=True)
        
        # Ambil kembali nama filenya saja setelah berurutan rapi, lalu jadikan URL web
        urls_gambar = [f'/static/testi/{kategori}/{x[0]}' for x in file_dengan_waktu]
        return jsonify(urls_gambar)
        
    except Exception as e:
        return jsonify([])


# ==========================================================================
# 3. JALUR AMBIL & KIRIM ULASAN REAL-TIME SUPABASE CLOUD
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
        
        data_ulasan = {
            "nama": nama,
            "rating": rating,
            "text": text,
            "status": "pending"
        }
        
        supabase.table('ulasan').insert(data_ulasan).execute()
        return jsonify({"success": True, "message": "Ulasan terkirim ke antrean saringan admin Dileppp! 🌱"})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ==========================================================================
# 4. PEMICU JALUR SERVER FLASK
# ==========================================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)