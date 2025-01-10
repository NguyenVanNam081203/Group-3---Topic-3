import mysql.connector
import re

# Kết nối cơ sở dữ liệu
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='',
            user='',
            password='',
            database='',
            port=''
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Lỗi kết nối cơ sở dữ liệu: {err}")
        return None

def get_database_results(query, params=None):
    """
    Hàm truy vấn cơ sở dữ liệu và trả về kết quả.
    """
    connection = get_db_connection()
    if not connection:
        return None, "Không thể kết nối đến cơ sở dữ liệu."
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or [])
        results = cursor.fetchall()
        cursor.close()
        return results, None
    except Exception as e:
        return None, f"Đã xảy ra lỗi khi truy vấn cơ sở dữ liệu: {e}"
    finally:
        connection.close()

# Biến toàn cục để lưu ID gần nhất
last_id = None

region_patterns = {
    r"\bmiền bắc\b": "Bắc",
    r"\bmiền trung\b": "Trung",
    r"\bmiền nam\b": "Nam",
    r"\bbắc\b": "Bắc",
    r"\btrung\b": "Trung",
    r"\bnam\b": "Nam"
}

def analyze_question(user_message):
    # Các từ khóa và trường tương ứng
    keywords = {
        'thành phố': 'thanh_pho',
        'miền': 'mien',
        'quận': 'quan',
        'huyện': 'huyen',
        'địa chỉ': 'dia_chi',
        'loại mặt bằng': 'loai_mat_bang',
        'hình ảnh': 'hinh_anh',
        'giá': 'gia',
        'diện tích': 'dien_tich',
        'mô tả': 'mo_ta',
        'hướng phong thủy': 'huong_phong_thuy'
    }

    global last_id

    # Trường hợp 1: "xem ảnh + số" hoặc "ảnh + số"
    match_specific_image = re.search(r"(?:xem )?ảnh(?:\s+id)?\s+(\d+)", user_message, re.IGNORECASE)
    if match_specific_image:
        mat_bang_id = match_specific_image.group(1)  # Lấy ID mặt bằng từ câu hỏi
        last_id = mat_bang_id  # Cập nhật ID gần nhất
        query = "SELECT hinh_anh FROM mat_bang WHERE mat_bang_id = %s"
        result, error = get_database_results(query, (mat_bang_id,))
        if error:
            return f"Lỗi khi truy vấn dữ liệu: {error}"
        if result:
            image_url = f"/static/dataImage/{result[0]['hinh_anh']}"  # Tạo đường dẫn đến ảnh
            return f"Đây là hình ảnh của mặt bằng số {mat_bang_id}: <img src='{image_url}' alt='Hình ảnh mặt bằng {mat_bang_id}' style='max-width: 100%; height: auto;'>"
        else:
            return f"Không tìm thấy ảnh của mặt bằng số {mat_bang_id}."

    # Trường hợp 2: "ảnh nó", "cho tôi xem ảnh", hoặc chỉ từ "ảnh"
    if re.search(r"(ảnh|hình ảnh)\b.*\b(nó|này|đó)?", user_message, re.IGNORECASE):
        if last_id:
            query = "SELECT hinh_anh FROM mat_bang WHERE mat_bang_id = %s"
            result, error = get_database_results(query, (last_id,))
            if error:
                return f"Lỗi khi truy vấn dữ liệu: {error}"
            if result:
                image_url = f"/static/dataImage/{result[0]['hinh_anh']}"  # Tạo đường dẫn đến ảnh
                return f"Đây là hình ảnh của mặt bằng số {last_id}: <img src='{image_url}' alt='Hình ảnh mặt bằng {last_id}' style='max-width: 100%; height: auto;'>"
            else:
                return f"Không tìm thấy ảnh của mặt bằng số {last_id}."
        else:
            return "Bạn chưa hỏi về ID nào trước đó. Vui lòng cung cấp ID để tôi có thể hiển thị ảnh."

    # Trường hợp 3: "id + số" hoặc chỉ số
    match_id = re.search(r"\b(?:id\s*)?(\d+)\b", user_message, re.IGNORECASE)
    if match_id:
        mat_bang_id = match_id.group(1)  # Lấy ID mặt bằng từ câu hỏi
        last_id = mat_bang_id  # Cập nhật ID gần nhất
        query = "SELECT mo_ta FROM mat_bang WHERE mat_bang_id = %s"
        result, error = get_database_results(query, (mat_bang_id,))
        if error:
            return f"Lỗi khi truy vấn dữ liệu: {error}"
        if result:
            return f"Mô tả chi tiết mặt bằng với ID {mat_bang_id}: {result[0]['mo_ta']}"
        else:
            return f"Không có mặt bằng nào với ID {mat_bang_id}."


    # Kiểm tra câu hỏi có chứa từ khóa nào không
    for keyword, field in keywords.items():
        if re.search(keyword, user_message, re.IGNORECASE):
            query = f"SELECT {field} FROM mat_bang LIMIT 1"
            result, error = get_database_results(query)
            if error:
                return error
            if result:
                return f"Thông tin {keyword}: {result[0][field]}"
            else:
                return f"Không có dữ liệu {keyword} trong bảng 'mat_bang'."

    # # Kiểm tra nếu câu hỏi có chứa ID mặt bằng
    # match = re.search(r"\b(\d+)\b", user_message)  # Tìm kiếm bất kỳ con số nào trong câu hỏi
    # if match:
    #     mat_bang_id = match.group(1)  # Lấy ID mặt bằng từ câu hỏi
    #     query = "SELECT mo_ta FROM mat_bang WHERE mat_bang_id = %s"
    #     result, error = get_database_results(query, (mat_bang_id,))
    #     if error:
    #         return error
    #     if result:
    #         return f"Mô tả chi tiết mặt bằng với ID {mat_bang_id}: {result[0]['mo_ta']}"
    #     else:
    #         return f"Không có mặt bằng nào với ID {mat_bang_id}."

    # Lấy danh sách thành phố từ cơ sở dữ liệu
    query = "SELECT DISTINCT thanh_pho FROM mat_bang"
    cities, error = get_database_results(query)
    if error:
        return error
    cities = [row['thanh_pho'] for row in cities]

    # Kiểm tra nếu câu hỏi có chứa thông tin về thành phố
    city_pattern = r"\b(" + "|".join(map(re.escape, cities)) + r")\b"
    city_match = re.search(city_pattern, user_message, re.IGNORECASE)

    if city_match:
        city = city_match.group(0)
        query = "SELECT mat_bang_id, loai_mat_bang, gia, thanh_pho, dien_tich FROM mat_bang WHERE thanh_pho = %s"
        results, error = get_database_results(query, (city,))
        if error:
            return error
        if results:
            reply = f"Dưới đây là một số mặt bằng tại {city}:" 
            for result in results:
                reply += f"\n\n---\nID: {result['mat_bang_id']} - Loại mặt bằng: {result['loai_mat_bang']} - Thành Phố: {result['thanh_pho']}- Diện tích: {result['dien_tich']}m^2 - Giá: {result['gia']:,} VND "
            return reply
        else:
            return f"Hiện chưa có mặt bằng ở {city}."

    region_patterns = {
        r"\bmiền bắc\b": "Bắc",
        r"\bmiền trung\b": "Trung",
        r"\bmiền nam\b": "Nam",
        r"\bbắc\b": "Bắc",
        r"\btrung\b": "Trung",
        r"\bnam\b": "Nam"
    }

    # Ưu tiên kiểm tra cụm từ đầy đủ trước
    for region_key, normalized_region in region_patterns.items():
        if re.search(region_key, user_message, re.IGNORECASE):
            # Truy vấn dựa trên miền
            query = """
                SELECT mat_bang_id, thanh_pho, gia, loai_mat_bang
                FROM mat_bang 
                WHERE mien = %s
            """
            results, error = get_database_results(query, (normalized_region,))
            if error:
                return error
            if results:
                reply = f"Dưới đây là một số mặt bằng tại miền {normalized_region}:"
                for result in results:
                    reply += (
                        f"\n\n---\nID: {result['mat_bang_id']} - Thành phố: {result['thanh_pho']} "
                        f"- Giá: {result['gia']:,} VND - Loại mặt bằng: {result['loai_mat_bang']}"
                    )
                return reply
            else:
                return f"Hiện chưa có mặt bằng ở miền {normalized_region}."

        # Trường hợp hỏi về loại mặt bằng (chung cư, căn hộ, nhà ở, trọ)
    loai_mat_bang_keywords = {
        r"\bchung cư\b": "Chung cư",
        r"\bcăn hộ\b": "Căn hộ",
        r"\bnhà ở\b": "Nhà ở",
        r"\btrọ\b": "Trọ"
    }

    for keyword_pattern, loai_mat_bang in loai_mat_bang_keywords.items():
        if re.search(keyword_pattern, user_message, re.IGNORECASE):
            query = """
                SELECT mat_bang_id, thanh_pho, gia, dien_tich 
                FROM mat_bang 
                WHERE loai_mat_bang = %s
            """
            results, error = get_database_results(query, (loai_mat_bang,))
            if error:
                return f"Lỗi khi truy vấn dữ liệu: {error}"
            if results:
                reply = f"Dưới đây là danh sách các mặt bằng loại {loai_mat_bang}:"
                for result in results:
                    reply += (
                        f"\n\n---\nID: {result['mat_bang_id']} - Thành phố: {result['thanh_pho']} "
                        f"- Giá: {result['gia']:,} VND - Diện tích: {result['dien_tich']}m²"
                    )
                return reply
            else:
                return f"Hiện chưa có mặt bằng nào thuộc loại {loai_mat_bang}."

    return None


