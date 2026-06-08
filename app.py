from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/gia-nong-san')
def api_gia_nong_san():
    # Tìm và đọc file lưu trữ dữ liệu tập trung do GitHub Actions đẩy về
    file_path = os.path.join('data', 'nongsan.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    
    # Trả về cấu trúc rỗng mặc định nếu file chưa kịp sinh ra
    return jsonify({"ngay_cap_nhat": "Đang cập nhật...", "danh_sach": []})
@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms.html')

if __name__ == '__main__':
    app.run(debug=True)