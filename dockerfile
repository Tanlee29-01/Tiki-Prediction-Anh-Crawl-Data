# 1. GÓC KHUẤT 1: Đừng dùng Python bản full (nặng 1GB). Dùng bản 'slim' (nặng 150MB) để server chạy nhanh, tiết kiệm tiền RAM.
FROM python:3.11-slim

# 2. Tạo một thư mục làm việc bên trong chiếc hộp (ảo)
WORKDIR /app

# 3. GÓC KHUẤT 2: Tối ưu Cache của Docker
# Chỉ copy file requirement vào trước. 
COPY requirement.txt .

# Chạy lệnh cài đặt thư viện. 
# Tại sao không copy toàn bộ code vào rồi mới cài? Vì nếu làm thế, mỗi lần bạn sửa 1 dòng code chữ lỗi chính tả, Docker sẽ phải tải lại toàn bộ scikit-learn rất mất thời gian!
RUN pip install --no-cache-dir -r requirement.txt

# 4. Sau khi cài xong thư viện, mới copy toàn bộ thư mục backend (chứa api.py và model.pkl) vào trong hộp.
COPY backend/ ./backend/

# 5. Mở cổng 8000 để chiếc hộp có thể giao tiếp với thế giới bên ngoài
EXPOSE 8000

# 6. Lệnh khởi động Server khi chiếc hộp được bật lên
# Lưu ý: Vì file api.py nằm trong thư mục backend, ta phải gọi là backend.api:app
# Cờ --host 0.0.0.0 bắt buộc phải có để Docker cho phép truy cập từ mạng ngoài.
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]