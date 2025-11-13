from flask import Flask, request, render_template
import qrcode
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    qr_code = None
    if request.method == 'POST':
        url = request.form['url']
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        qr_code = base64.b64encode(buf.getvalue()).decode('utf-8')
    return render_template('index.html', qr_code=qr_code)

if __name__ == '__main__':
    app.run(debug=True)