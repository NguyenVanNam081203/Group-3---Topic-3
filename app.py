import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, session,send_file
import cohere
from analyze_question import analyze_question  # Import hàm analyze_question
import mysql.connector
import requests
import stripe
import qrcode
import os
import logging

logging.basicConfig(level=logging.INFO)
QR_CODE_PATH = './static/image/qr_code.jpg'
app = Flask(__name__, static_folder='static')  

# Kết nối với MySQL
def get_db_connection():
    connection = mysql.connector.connect(
        host='',
        user='',
        password='',
        database='',
        port=''
    )
    return connection

def create_comments_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            user_name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            comment TEXT NOT NULL,
            approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()

# Tạo bảng comments nếu chưa tồn tại
create_comments_table()

@app.route('/')
def home():
    return redirect(url_for('index'))  # Chuyển hướng về '/dashboard'

@app.route('/dashboard')
def index():
    # Lấy tham số phân trang từ URL
    page = request.args.get('page', 1, type=int)
    per_page = 8  # Số mặt bằng mỗi trang

    # Lấy các tham số bộ lọc và sắp xếp từ URL
    mien = request.args.get('mien', default=None, type=str)
    thanh_pho = request.args.get('thanh_pho', default=None, type=str)
    loai_mat_bang = request.args.get('loai_mat_bang', default=None, type=str)
    price_range = request.args.get('price', default=None, type=str)
    area_range = request.args.get('area', default=None, type=str)
    keyword = request.args.get('keyword', default=None, type=str)
    sort_order = request.args.get('sort_order', default=None, type=str)  # Sắp xếp theo giá

    # Tạo điều kiện lọc
    where_conditions = []
    params = []

    if mien:
        where_conditions.append("mien = %s")
        params.append(mien)

    if thanh_pho:
        where_conditions.append("thanh_pho = %s")
        params.append(thanh_pho)

    if loai_mat_bang:
        where_conditions.append("loai_mat_bang = %s")
        params.append(loai_mat_bang)

    if price_range:
        if price_range == "0tr-10tr":
            where_conditions.append("gia >= 0 AND gia <= 10000000")
        elif price_range == "10tr-20tr":
            where_conditions.append("gia > 10000000 AND gia <= 20000000")
        elif price_range == "20tr-50tr":
            where_conditions.append("gia > 20000000 AND gia <= 50000000")
        elif price_range == ">50tr":
            where_conditions.append("gia > 50000000")

    if area_range:
        if area_range == "10m² - 30m²":
            where_conditions.append("dien_tich >= 10 AND dien_tich <= 30")
        elif area_range == "30m² - 50m²":
            where_conditions.append("dien_tich > 30 AND dien_tich <= 50")
        elif area_range == "50m² - 100m²":
            where_conditions.append("dien_tich > 50 AND dien_tich <= 100")
        elif area_range == ">100m²":
            where_conditions.append("dien_tich > 100")

    if keyword:
        if keyword.isdigit():  # Nếu keyword là một số
            where_conditions.append("mat_bang_id = %s")
            params.append(int(keyword))
        else:  # Nếu không, tìm kiếm theo từ khóa trong các cột khác
            where_conditions.append("(loai_mat_bang LIKE %s OR thanh_pho LIKE %s)")
            params.extend([f'%{keyword}%', f'%{keyword}%'])


    # Xử lý sắp xếp theo giá
    if sort_order in ['asc', 'desc']:
        order_clause = f"ORDER BY gia {sort_order}" if sort_order in ['asc', 'desc'] else ""
    else:
        order_clause = "ORDER BY mat_bang_id desc"
    # Kết nối database và truy vấn
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

    # Lấy tổng số mặt bằng
    cursor.execute(f'SELECT COUNT(*) FROM mat_bang {where_clause}', tuple(params))
    total = cursor.fetchone()['COUNT(*)']

    if total == 0:
        mat_bang = []
        total_pages = 0
    else:
        total_pages = (total // per_page) + (1 if total % per_page > 0 else 0)
        offset = (page - 1) * per_page
        query = f'''
            SELECT * FROM mat_bang 
            {where_clause} 
            {order_clause} 
            LIMIT %s OFFSET %s
        '''
        cursor.execute(query, tuple(params + [per_page, offset]))
        mat_bang = cursor.fetchall()

    cursor.close()
    connection.close()
    session['mat_bangs'] = mat_bang
    return render_template(
        'html/dashboard.html',
        mat_bangs=mat_bang,
        count=total,
        page=page,
        total_pages=total_pages,
        selected_mien=mien,
        selected_thanh_pho=thanh_pho,
        selected_loai_mat_bang=loai_mat_bang,
        selected_price_range=price_range,
        selected_area_range=area_range,
        search_keyword=keyword,
        selected_sort_order=sort_order
    )

#chatbot
COHERE_API_KEY = ""
co = cohere.Client(COHERE_API_KEY)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "Tin nhắn không được để trống"}), 400

    try:
        bot_reply = analyze_question(user_message)

        if not bot_reply:  # Nếu không có trả lời từ phân tích, gửi yêu cầu tới Cohere
            response = co.generate(
                model='command-xlarge-nightly',
                prompt=f"Người dùng: {user_message}\nAI:",
                max_tokens=1000,
                temperature=0.7
            )

            # Kiểm tra phản hồi từ Cohere
            if not response or not hasattr(response, 'generations') or not response.generations:
                raise ValueError("Phản hồi từ API Cohere không hợp lệ")

            # Kiểm tra text trong generations
            generation = response.generations[0] if response.generations else None
            if not generation or not hasattr(generation, 'text') or generation.text is None:
                raise ValueError("Không có văn bản hợp lệ trong phản hồi của Cohere")

            bot_reply = generation.text.strip()

        return jsonify({"response": bot_reply}), 200

    except Exception as e:
        print(f"Lỗi khi xử lý câu hỏi: {e}")
        return jsonify({"error": f"Có lỗi xảy ra khi xử lý câu hỏi: {str(e)}"}), 500

    
@app.route('/blogs')
def blogs():
    return render_template('html/blogs.html')

# Định nghĩa hàm tạo mã QR ở đây
def create_qr_code(client_secret):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(client_secret)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        img.save(QR_CODE_PATH)  # Lưu tệp
        logging.info("Mã QR đã được tạo thành công.")
    except Exception as e:
        logging.error(f"Lỗi khi tạo mã QR: {str(e)}")
        
@app.route('/cart')
def cart():
    return render_template('html/cart.html')

@app.route('/promote')
def promote():
    return render_template('html/promote.html')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        
                # Lấy thông tin mặt bằng
        cursor.execute("SELECT * FROM mat_bang WHERE mat_bang_id = %s", (product_id,))
        mat_bang = cursor.fetchone()

        if mat_bang:
            # Lấy loại mặt bằng của mặt bằng hiện tại
            loai_mat_bang = mat_bang['loai_mat_bang']
            # Truy vấn các mặt bằng cùng loại
            cursor.execute("""
                SELECT * FROM mat_bang 
                WHERE loai_mat_bang = %s AND mat_bang_id != %s
                LIMIT 4  -- Giới hạn kết quả
            """, (loai_mat_bang, product_id))
            similar_mats = cursor.fetchall()  # Lưu các mặt bằng tương tự
        else:
            similar_mats = []

    mat_bangs = session.get('mat_bangs', [])
    mat_bang = next((item for item in mat_bangs if item['mat_bang_id'] == product_id), None)
    address = (mat_bang['dia_chi'] or "") + ", " + (mat_bang['huyen'] or "") + ", " + (mat_bang['quan'] or "") + ", " + (mat_bang['thanh_pho'] or "")
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {
        'access_token': ''
    }
    response = requests.get(url, params=params)

    # Trích xuất tọa độ từ kết quả trả về
    data = response.json()
    if data['features']:
        lat = data['features'][0]['geometry']['coordinates'][1]  # Vĩ độ
        lon = data['features'][0]['geometry']['coordinates'][0]  # Kinh độ
    else:
        lat = lon = None

    return render_template('html/product_detail.html', 
                           mat_bang=mat_bang, 
                           similar_mats=similar_mats,  # Truyền dữ liệu mặt bằng tương tự
                           latitude=lat, 
                           longitude=lon)

def get_comments(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM comments WHERE product_id = %s AND approved = TRUE', (product_id,))
    comments = cursor.fetchall()
    cursor.close()
    connection.close()
    return comments

@app.route('/product/<int:product_id>/comments', methods=['POST'])
def add_comment(product_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    user_name = request.form['user_name']
    email = request.form['email']
    comment = request.form['comment']

    cursor.execute('''
        INSERT INTO comments (product_id, user_name, email, comment, approved)
        VALUES (%s, %s, %s, %s, TRUE)
    ''', (product_id, user_name, email, comment))
    connection.commit()

    cursor.close()
    connection.close()

    return product_detail(product_id)

@app.route('/admin/comments')
def admin_comments():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute('SELECT * FROM comments WHERE approved = FALSE')
    pending_comments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('html/admin_comments.html', comments=pending_comments)

@app.route('/admin/comments/<int:comment_id>/approve', methods=['POST'])
def approve_comment(comment_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('UPDATE comments SET approved = TRUE WHERE id = %s', (comment_id,))
    connection.commit()

    cursor.close()
    connection.close()

    return admin_comments()

def create_orders_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            address TEXT NOT NULL,
            phone VARCHAR(20) NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()
    
@app.route('/qr_code')
def get_qr_code():
    return send_file(QR_CODE_PATH)

@app.route('/checkout', methods=['POST'])
def checkout():
    create_orders_table()
    name = request.form['name']
    email = request.form['email']
    address = request.form['address']
    phone = request.form['phone']
    
    # Lấy số tiền từ biểu mẫu
    amount = int(request.form.get('amount', 50000))  # Giá trị mặc định là 50000

    # Đảm bảo số tiền nằm trong khoảng cho phép
    if amount < 50000 or amount > 99999999:
        return "Số tiền phải nằm trong khoảng từ 50.000 đến 99.999.999 VND", 400

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount * 100,  # Chuyển đổi sang đơn vị nhỏ nhất (đồng)
            currency='vnd',
            receipt_email=email,
        )

        # Lưu thông tin thanh toán vào bảng `orders`
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO orders (name, email, address, phone, amount, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        ''', (name, email, address, phone, amount))
        connection.commit()
        cursor.close()
        connection.close()

        # Tạo mã QR từ client_secret
        create_qr_code(intent['client_secret'])

        return render_template('html/payment_success.html', client_secret=intent['client_secret'])

    except Exception as e:
        return f"Lỗi khi xử lý thanh toán: {str(e)}", 400


@app.route('/submit_request', methods=['POST'])
def submit_request():
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        customer_name = request.form['customer_name']
        area = request.form['area']
        phone_email = request.form['phone_email']
        finance_range = request.form['finance_range']
        location = request.form['location']
        other_requirements = request.form.get('other_requirements', '')  # Yêu cầu khác có thể rỗng
        connection = get_db_connection()
        cursor = connection.cursor()
        # Lưu dữ liệu vào MySQL
        query = """INSERT INTO property_requests 
                   (customer_name, area, phone_email, finance_range, location, other_requirements)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (customer_name, area, phone_email, finance_range, location, other_requirements))
        print(customer_name)
        connection.commit()
        cursor.close()
        connection.close()
        # Sau khi gửi yêu cầu, chuyển hướng về trang cảm ơn hoặc thông báo
        return redirect(url_for('index'))
    

# Nhờ liên hệ trong detail admin
@app.route('/add-contact/<int:mat_bang_id>', methods=['POST'])
def add_contact(mat_bang_id):
    ten_khach_hang = request.form['ten_khach_hang']
    so_dien_thoai = request.form['so_dien_thoai']

    # Kết nối đến cơ sở dữ liệu
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Thêm dữ liệu vào bảng nho_lien_he
        query = """
            INSERT INTO nho_lien_he (id_mat_bang, ten_khach_hang, so_dien_thoai)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (mat_bang_id, ten_khach_hang, so_dien_thoai))
        conn.commit()

        # Trả về thông báo thành công dưới dạng JSON
        return jsonify({'success': True, 'message': 'Liên hệ đã được gửi thành công!'})
    except Exception as e:
        print(f"Lỗi: {e}")
        return jsonify({'success': False, 'message': 'Đã xảy ra lỗi khi thêm liên hệ.'})
    finally:
        cursor.close()
        conn.close()


# Route hiển thị trang đăng nhập
@app.route('/login')
def login_page():
    return render_template('html/Login.html')

# Route xử lý đăng nhập
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Kiểm tra tài khoản và mật khẩu
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session['token']=username+password
            # Đăng nhập thành công
            return redirect('/accept')
        else:
            # Sai tài khoản hoặc mật khẩu
            error = "Invalid username or password."
            return render_template('html/Login.html', error=error)
    except Exception as e:
        # Lỗi hệ thống
        print(f"Error: {e}")
        error = "An error occurred. Please try again later."
        return render_template('html/Login.html', error=error)
    finally:
        cursor.close()
        conn.close()

@app.route('/accept')
def accept():
    if 'token' in session:
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query_nho_quang_ba = "SELECT ho_va_ten, vi_tri_mat_bang,gia_thue, mo_ta, hinh_anh, id FROM nho_quang_ba"
            cursor.execute(query_nho_quang_ba)
            data_quang_ba = cursor.fetchall()
            # Truy vấn dữ liệu từ bảng `nho_lien_he`
            query = "SELECT id_mat_bang, ten_khach_hang, so_dien_thoai FROM nho_lien_he"
            cursor.execute(query)
            rows = cursor.fetchall()
            # Đóng kết nối
            cursor.close()
            conn.close()
        # Render dữ liệu ra template
            return render_template('html/accept.html', contacts=rows,danh_sach_quang_ba=data_quang_ba)
        except Exception as e:
            print(f"Lỗi: {e}")
            return "Đã xảy ra lỗi khi truy vấn dữ liệu."
    else:
        return redirect('/login')


# Route xử lý đăng xuất
@app.route('/logout')
def logout():
    # Xóa thông tin đăng nhập (nếu có session)
    session.clear()  # Xóa toàn bộ session (nếu sử dụng session)
    # Chuyển hướng về trang đăng nhập
    return redirect('/')
@app.route('/submit_promotion', methods=['POST'])
def submit():
    if request.method == 'POST':
        ho_va_ten = request.form['name']
        vi_tri_mat_bang = request.form['location']
        gia_thue = request.form['price']
        mo_ta = request.form['description']
        hinh_anh_mat_bang = request.files['image'].filename
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''INSERT INTO nho_quang_ba (ho_va_ten, vi_tri_mat_bang, gia_thue, mo_ta, hinh_anh)
                          VALUES (%s, %s, %s, %s, %s)''',
                       (ho_va_ten, vi_tri_mat_bang, gia_thue, mo_ta, hinh_anh_mat_bang))
        conn.commit()
        cursor.close()
        return redirect(url_for('index'))
@app.route('/approve_promotion', methods=['POST'])
def approve_promotion():
    action = request.form['action']  # Lấy giá trị hành động "approve" hoặc "reject"
    image = request.form['image']  # Lấy ID của chương trình khuyến mãi
    customer_name = request.form['customer_name']  # Lấy họ tên khách
    location = request.form['location']  # Lấy vị trí mặt bằng
    rent_price = request.form['rent_price']  # Lấy giá thuê
    description = request.form['description']  # Lấy mô tả
    id_pro = request.form['id_pro']

    # Kết nối tới cơ sở dữ liệu MySQL
    conn = get_db_connection()
    cursor = conn.cursor()

    # Chèn dữ liệu vào MySQL (giả sử bạn có một bảng tên là `promotions`)
    if action == 'approve':
        query = """
        INSERT INTO mat_bang (dia_chi, gia, mo_ta, hinh_anh)
        VALUES (%s, %s, %s, %s)
        """
        values = (location, rent_price, description,image)
        cursor.execute(query, values)
        conn.commit()
        query2 = """
                DELETE FROM nho_quang_ba WHERE id = %s
                """
        cursor.execute(query2, (id_pro,))
        conn.commit()
    elif action == 'reject':
        query = """
                        DELETE FROM nho_quang_ba WHERE id = %s
                        """
        cursor.execute(query, (id_pro,))
        conn.commit()
    # Đóng kết nối
    cursor.close()
    conn.close()
    return redirect(url_for('accept'))  # Sau khi xử lý, chuyển hướng người dùng về trang chủ

if __name__ == '__main__':

    app.run(debug=True)
