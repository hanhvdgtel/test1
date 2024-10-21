from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Hàm lấy số điện thoại từ một URL
def get_phone_number(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            a_tags = soup.find_all('a', href=True)
            for a_tag in a_tags:
                if a_tag['href'].startswith('tel:'):
                    phone_number = a_tag['href'].replace('tel:', '')
                    return phone_number
            return None
        else:
            return None
    except Exception as e:
        return None

# Hàm quét từ i_start và tự động quét lại cùng giá trị i nếu không tìm thấy số điện thoại
def scan_phone_numbers(i_start):
    base_url = "https://bannha888.com/thanh-vien/"
    i = i_start
    results = []

    # Quét liên tục cho đến khi tìm thấy số điện thoại
    while True:
        url = f"{base_url}{i}"
        phone_number = get_phone_number(url)
        
        # Nếu tìm thấy số điện thoại, thêm vào kết quả và tăng giá trị i
        if phone_number:
            results.append({'i': i, 'phone_number': phone_number})
            print(f"Đã tìm thấy số: {phone_number} tại i={i}")
            i += 1  # Tăng i khi tìm thấy số điện thoại
        else:
            print(f"Không tìm thấy số tại i={i}, quét lại...")
        
        # Thực hiện quét lại cùng giá trị i nếu không tìm thấy số
        if not phone_number:
            continue
        else:
            break  # Thoát vòng lặp khi tìm thấy số

    return results, i  # Trả về kết quả và giá trị i cuối cùng

# Trang chủ, form để nhập giá trị bắt đầu
@app.route('/')
def index():
    return render_template('index.html')

# Xử lý yêu cầu quét số điện thoại
@app.route('/scan', methods=['POST'])
def scan():
    i_start = int(request.form['i_start'])
    
    # Gọi hàm quét số điện thoại
    results, next_i = scan_phone_numbers(i_start)
    
    # Trả về kết quả cho người dùng và tiếp tục quét nếu cần
    return render_template('results.html', results=results, next_i=next_i)

if __name__ == "__main__":
    app.run(debug=True)
