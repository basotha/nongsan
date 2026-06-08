import requests
from bs4 import BeautifulSoup
import re
import cloudscraper
import json
import os
from datetime import datetime

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "nongsan.json")

DANH_SACH_NGUON = {
    "ca-phe": {"ten": "Giá Cà Phê", "url": "https://banggianongsan.com/bang-gia-ca-phe/", "nhom_macdinh": "cafe", "don_vi": "đ/kg"},
    "ho-tieu": {"ten": "Giá Hồ Tiêu", "url": "https://banggianongsan.com/bang-gia-tieu/", "nhom_macdinh": "tieu", "don_vi": "đ/kg"},
    "hat-dieu": {"ten": "Giá Hạt Điều", "url": "https://banggianongsan.com/bang-gia-hat-dieu/", "nhom_macdinh": "dieu", "don_vi": "đ/kg"},
    "cao-su": {"ten": "Giá Cao Su", "url": "https://banggianongsan.com/bang-gia-cao-su-hom-nay/", "nhom_macdinh": "cao_su", "don_vi": "đ/kg"},
    "cacao": {"ten": "Giá Cacao", "url": "https://banggianongsan.com/bang-gia-cacao-hom-nay/", "nhom_macdinh": "cacao", "don_vi": "đ/kg"},
    "ot": {"ten": "Giá Ớt", "url": "https://banggianongsan.com/bang-gia-ot/", "nhom_macdinh": "ot", "don_vi": "đ/kg"},
    "khoai-lang": {"ten": "Giá Khoai Lang", "url": "https://banggianongsan.com/gia-khoai-lang/", "nhom_macdinh": "khoai_lang", "don_vi": "đ/kg"},
    "macca": {"ten": "Giá Mắc Ca", "url": "https://banggianongsan.com/bang-gia-macca-hom-nay/", "nhom_macdinh": "macca", "don_vi": "đ/kg"},
    "bo": {"ten": "Giá Bơ", "url": "https://banggianongsan.com/bang-gia-bo-hom-nay/", "nhom_macdinh": "bo", "don_vi": "đ/kg"},
    "sau-rieng": {"ten": "Giá Sầu Riêng", "url": "https://banggianongsan.com/bang-gia-sau-rieng/", "nhom_macdinh": "sau_rieng", "don_vi": "đ/kg"}
}

def xu_ly_gia(gia_raw):
    """Hàm xử lý khoảng giá thông minh chống lỗi dính chữ thành tỷ đồng"""
    gia_raw = gia_raw.replace('–', '-').replace('—', '-').replace('to', '-')
    if '-' in gia_raw:
        cac_muc = gia_raw.split('-')
        so_thanh_phan = []
        for muc in cac_muc:
            so_sach = re.sub(r'[^\d]', '', muc)
            if so_sach.isdigit():
                so_thanh_phan.append(int(so_sach))
        if len(so_thanh_phan) == 2:
            return int(sum(so_thanh_phan) / 2)
        elif len(so_thanh_phan) == 1:
            return so_thanh_phan[0]
            
    gia_so = re.sub(r'[^\d]', '', gia_raw)
    if gia_so.isdigit():
        return int(gia_so)
    return None

def cao_chi_tiet_nguon(url, nhom_macdinh, don_vi_macdinh):
    danh_sach_item = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return danh_sach_item

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ten_goc = cols[0].get_text().replace('\xa0', ' ').strip()
                    gia_raw = cols[1].get_text().replace('\xa0', ' ').strip()
                    
                    if not ten_goc or not gia_raw or any(keyword in ten_goc for keyword in ["Thị trường", "Địa phương", "Sàn", "Ngày", "Loại"]):
                        continue
                    
                    gia_chuan = xu_ly_gia(gia_raw)
                    
                    if gia_chuan is not None:
                        ten_lower = ten_goc.lower()
                        don_vi = don_vi_macdinh
                        nhom = nhom_macdinh
                        
                        # Xử lý cắt bỏ phần nội dung nằm trong dấu ngoặc đơn ở tên gốc (ví dụ: "(đ/kg)", "(đ/độ)")
                        ten_sach = re.sub(r'\(.*?\)', '', ten_goc).strip()
                        
                        # Phân loại Thị trường Quốc tế dựa trên từ khóa gốc
                        if "usd" in ten_lower or "usd/tấn" in ten_lower or "usd/tan" in ten_lower:
                            nhom = "quoc_te"
                            don_vi = "USD/Tấn"
                            ten_hien_thi = ten_sach
                        elif "cent" in ten_lower or "lb" in ten_lower:
                            nhom = "quoc_te"
                            don_vi = "US Cent/lb"
                            ten_hien_thi = ten_sach
                        elif "london" in ten_lower or "robusta" in ten_lower:
                            nhom = "quoc_te"
                            ten_hien_thi = "Cà phê Robusta (London)"
                            don_vi = "USD/Tấn"
                        elif "new york" in ten_lower or "arabica" in ten_lower:
                            nhom = "quoc_te"
                            ten_hien_thi = "Cà phê Arabica (New York)"
                            don_vi = "US Cent/lb"
                        elif "tokyo" in ten_lower or "tocom" in ten_lower:
                            nhom = "quoc_te"
                            ten_hien_thi = f"Cao su Kỳ hạn Tokyo ({ten_sach})"
                            don_vi = "Yen/Kg"
                        elif "thế giới" in ten_lower or "quốc tế" in ten_lower:
                            nhom = "quoc_te"
                            ten_hien_thi = ten_sach
                            don_vi = "USD/Tấn"
                        else:
                            # Hàng nội địa: Sử dụng tên đã được dọn sạch chữ (đ/kg) thừa
                            nhom = nhom_macdinh
                            ten_hien_thi = ten_sach
                            don_vi = don_vi_macdinh
                        
                        danh_sach_item.append({
                            "nhom": nhom,
                            "ten": ten_hien_thi,
                            "gia": gia_chuan,
                            "don_vi": don_vi,
                            "bien_dong": "equal"
                        })
    except Exception as e:
        print(f"Lỗi xử lý URL [{url}]: {e}")
        
    return danh_sach_item

def chay_tong_hop_luu_json():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    all_output = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                all_output = json.load(f)
        except:
            all_output = {}

    ngay_hom_nay = datetime.now().strftime("%d/%m/%Y")
    co_it_nhat_mot_cap_nhat = False
    
    for slug, info in DANH_SACH_NGUON.items():
        print(f"-> Tiến hành cào dữ liệu: {info['ten']}...")
        du_lieu_quet = cao_chi_tiet_nguon(info['url'], info['nhom_macdinh'], info['don_vi'])
        
        if du_lieu_quet:
            all_output[slug] = {
                "ten": info['ten'],
                "ngay_cap_nhat": ngay_hom_nay,
                "du_lieu": du_lieu_quet
            }
            co_it_nhat_mot_cap_nhat = True
            print(f"   [Thành công] Đã bốc {len(du_lieu_quet)} dòng.")
        else:
            print(f"   [Cảnh báo] Thất bại link {info['ten']}. Giữ nguyên data phiên cũ.")

    if co_it_nhat_mot_cap_nhat:
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_output, f, ensure_ascii=False, indent=4)
            print(f"\n🎉 Đã đồng bộ sạch dữ liệu vào file: {DATA_FILE}")
        except Exception as e:
            print(f"Lỗi ghi dữ liệu: {e}")

if __name__ == "__main__":
    chay_tong_hop_luu_json()