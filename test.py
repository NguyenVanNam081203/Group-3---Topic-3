from vncorenlp import VnCoreNLP

# Cập nhật đường dẫn đến thư mục chứa mô hình VnCoreNLP
vncorenlp = VnCoreNLP("D:/HTKDTM/business_premises_2/VnCoreNLP/VnCoreNLP.jar")

# Phân tích câu
sentence = "Thành phố Hà Nội có mặt bằng văn phòng nào?"
words = vncorenlp.tokenize(sentence)

# In kết quả phân tích từ VnCoreNLP
print(words)
