from flask import Flask, render_template, request, stream_with_context, Response
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
stop_scanning = False

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

def scan_phone_numbers(i_start):
    global stop_scanning
    base_url = "https://bannha888.com/thanh-vien/"
    i = i_start
    while not stop_scanning:
        url = f"{base_url}{i}"
        phone_number = get_phone_number(url)

        if phone_number:
            yield f"data: i: {i} - Số điện thoại: {phone_number}\n\n"
            i += 1  # Chỉ tăng giá trị i khi tìm thấy số điện thoại
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
