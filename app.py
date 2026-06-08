from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

# --- CẤU HÌNH ROBOTS.TXT VÀ SITEMAP.XML CHO SEO ---

@app.route('/robots.txt')
def robots_txt():
    # Trả về nội dung chuỗi text trực tiếp, không cần đọc file từ ổ đĩa
    noi_dung_robots = "User-agent: *\nAllow: /\nAllow: /api/gia-nong-san\nDisallow: /data/\nSitemap: https://nongsan.timnhanh.top/sitemap.xml"
    return noi_dung_robots, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/sitemap.xml')
def sitemap_xml():
    # Trả về nội dung cấu trúc XML trực tiếp, thách thức mọi lỗi phân quyền trên VPS
    noi_dung_sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://nongsan.timnhanh.top/</loc>
    <lastmod>2026-06-08</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://nongsan.timnhanh.top/privacy-policy</loc>
    <lastmod>2026-06-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>https://nongsan.timnhanh.top/terms-of-service</loc>
    <lastmod>2026-06-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>"""
    return noi_dung_sitemap, 200, {'Content-Type': 'application/xml; charset=utf-8'}
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/gia-nong-san')
def api_gia_nong_san():
    # Đường dẫn chuẩn đến file dữ liệu tập trung trong thư mục data
    file_path = os.path.join('data', 'nongsan.json')
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            danh_sach_tong_hop = []
            ngay_cap_nhat = "Đang cập nhật..."
            
            # Duyệt qua các key (ca-phe, ho-tieu...) để gộp phẳng dữ liệu
            for slug, noi_dung in raw_data.items():
                # Lấy ngày cập nhật mới nhất từ các gói dữ liệu
                if "ngay_cap_nhat" in noi_dung:
                    ngay_cap_nhat = noi_dung["ngay_cap_nhat"]
                
                # Sửa lỗi chính tả biến noi_dung để bốc chuẩn mảng dữ liệu
                if "du_lieu" in noi_dung:
                    danh_sach_tong_hop.extend(noi_dung["du_lieu"])
            
            return jsonify({
                "ngay_cap_nhat": ngay_cap_nhat,
                "danh_sach": danh_sach_tong_hop
            })
            
        except Exception as e:
            print(f"Lỗi đọc hoặc xử lý file JSON: {e}")
            return jsonify({"ngay_cap_nhat": "Lỗi dữ liệu", "danh_sach": []})
    
    # Trả về mảng rỗng nếu file chưa kịp sinh ra
    return jsonify({"ngay_cap_nhat": "Đang cập nhật...", "danh_sach": []})

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
