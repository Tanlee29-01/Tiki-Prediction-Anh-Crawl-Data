import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from backend.utils import clean_text
import joblib

# 1. Chuẩn bị dữ liệu (Dùng data thật hoặc data giả lập này để test luồng)
data = {
    'Nội dung đánh giá': [
        'sản phẩm sách này rất tốt, bìa đẹp', 
        'giao hàng quá chậm, bực mình', 
        'nội dung tuyệt vời, 10 điểm', 
        'sách rách nát, shop lừa đảo', 
        'đóng gói cẩn thận, sẽ ủng hộ tiếp',
        'Sản phẩm quá tệ'
    ],
    'Nhãn': [1, 0, 1, 0, 1,0]  # 1 là Tích cực, 0 là Tiêu cực
}
df = pd.DataFrame(data)

# 2. Chia dữ liệu
# Với 5 mẫu và stratify theo 2 lớp, test_size=0.2 chỉ tạo 1 mẫu test -> gây lỗi.
# Tăng test_size để tập test có ít nhất 2 mẫu.
X_train, X_test, y_train, y_test = train_test_split(
    df['Nội dung đánh giá'],
    df['Nhãn'],
    test_size=0.2,   # 2 mẫu test
    random_state=42,
    stratify=df['Nhãn']
)

# 3. Khởi tạo và Huấn luyện Pipeline
model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(preprocessor=clean_text)),
    ('classifier', LogisticRegression())
])

print("Đang huấn luyện mô hình...")
model_pipeline.fit(X_train, y_train)
print("Huấn luyện xong!")

# 4. ĐÓNG BĂNG VÀ XUẤT MÔ HÌNH RA Ổ CỨNG (Bước quan trọng nhất)
joblib.dump(model_pipeline, 'model.pkl')
print("Đã lưu file model.pkl thành công! Hãy kiểm tra thư mục của bạn.")