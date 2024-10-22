from flask import Flask, render_template, request, stream_with_context, Response
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
stop_scanning = False

def get_info(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm thông tin title
            title_tag = soup.find('a', class_='swipebox')
            title = title_tag['title'] if title_tag else None

            # Tìm số điện thoại
            phone_number = None
            a_tags = soup.find_all('a', href=True)
            for a_tag in a_tags:
                if a_tag['href'].startswith('tel:'):
                    phone_number = a_tag['href'].replace('tel:', '')
                    break
            
            return title, phone_number
        else:
            return None, None
    except Exception as e:
        return None, None

def scan_phone_numbers(i_start):
    global stop_scanning
    base_url = "https://bannha888.com/thanh-vien/"
    i = i_start
    while not stop_scanning:
        url = f"{base_url}{i}"
        title, phone_number = get_info(url)

        if title and phone_number:
            yield f"data: i: {i} - Title: {title} - Số điện thoại: {phone_number}\n\n"
            i += 1  # Tăng giá trị i khi tìm thấy cả title và số điện thoại
        elif title and not phone_number:
            i += 1  # Tăng giá trị i nếu chỉ tìm thấy title
        else:
            time.sleep(1)  # Đợi 1 giây trước khi thử lại cùng giá trị i

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['GET'])
def scan():
    global stop_scanning
    stop_scanning = False
    i_start = int(request.args.get('i_start', 0))
    return Response(stream_with_context(scan_phone_numbers(i_start)), mimetype='text/event-stream')

@app.route('/stop', methods=['POST'])
def stop():
    global stop_scanning
    stop_scanning = True
    return 'Scanning stopped'

if __name__ == "__main__":
    app.run(debug=True)
