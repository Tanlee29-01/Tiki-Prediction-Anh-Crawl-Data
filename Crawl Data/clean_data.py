import pandas as pd

def clean_duplicate_reviews(csv_file):
    print(f"Đang guets rác cho file: {csv_file}")

    try:
        df = pd.read_csv(csv_file)
        initial_rows = len(df)
        print(f"Dữ liệu ban đầu có {len(initial_rows)} dòng.")

        df_cleaned = df.drop_duplicates(
            subset=['PRODUCT_ID','Nội dung đánh giá'],
            keep='first'
        )

        df_cleaned = df_cleaned.dropna(subset=['Nội dung đá]nh giá'])

        final_rows = len(df_cleaned)
        duplicate_removed = initial_rows - final_rows

        if duplicate_removed > 0:
            df_cleaned.to_csv(csv_file,index=False,encoding='utf-8-sig')
            print(f"Đã dọng sạch! Đã xóa {duplicate_removed} dòng rác hoặc trùng lặp.")
            print(f"Dữ liệu sạch còn lại {final_rows} dòng.")
        else:
            print("File sạch, không có rác hoặc trùng lặp nào cả")
    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")

if __name__ == "__main__":
    clean_duplicate_reviews('Data_crawl/tike_reviews.csv')