import requests
import pandas as pd
import time
import random
import os
import re

PATH_STORE = 'Data_crawl/tiki_reviews.csv'
INPUT_FILE = 'product_book.csv'
def normalize_text(text: str) -> str:
    if text is None:
        return ""
    text = str(text)
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    text = text.replace("\t", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def get_tiki_reviews(PRODUCT_ID,SPID):
    #1. Setting cấu hình cho bot 
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
        'Accept':'*/*'
    }
    print(f"Đang lấy dữ liệu từ sản phẩm ID: {PRODUCT_ID}...")

    #2. Lấy tên sản phẩm từ API chi tiết sản phẩm
    product_api_url = f"https://tiki.vn/api/v2/products/{PRODUCT_ID}"
    try:
        response_product =requests.get(product_api_url,headers=headers)
        if response_product.status_code == 200:
            product_name = response_product.json().get('name','không tìm thấy tên')
            print(f"Tên sản phẩm: {product_name}")
        else:
            print("Không thể lấy thông tin sản phẩm. Bỏ qua.")
            return None,False
    except Exception as e:
        print(f"Lỗi mạng khi lấy thông tin sản phẩm: {e}")
        return None,False
    
    #3. Chuẩn bị danh sách để lưu dữ liệu đánh giá
    all_reviews = []
    page = 1
    is_interrupted = False
    
    #4. Loop để lấy đánh giá từ nhiều trang
    try:
        while True:
            print(f"Đang tải đánh giá trang {page}....")
            # Đường dẫn API từ tiki
            review_api_url = f"https://tiki.vn/api/v2/reviews?limit=5&include=comments,contribute_info,attribute_vote_summary&sort=score|desc,id|desc,stars|all&page={page}&spid={SPID}&product_id={PRODUCT_ID}"
            try:
                #1. Đừng dẫn
                response = requests.get(review_api_url,headers=headers,timeout=10)
                response.raise_for_status()
                data= response.json()
                reviews = data.get('data',[])
                # 2. Điều kiện dừng
                if not reviews:
                    print("Đã lấy hết các trang đánh giá!")
                    break
                
                #3. Lưu data
                for review in reviews:
                    review_content = review.get('content','')
                    review_content = normalize_text(review_content)
                    rating = review.get('rating',0)

                    if review_content and review_content.strip():
                        all_reviews.append({
                            'Tên sản phẩm': product_name,
                            'Số sao': rating,
                            'Nội dung đánh giá': review_content.strip()
                        })
                # Nhảy lên trang  kế tiếp và ngủ để tránh ban IP
                page += 1
                time.sleep(random.uniform(1.5,3.0))
            except Exception as e:
                print(f"Lỗi  ở trang {page}: {e}. Dừng lấy data từ sản phẩm này và lưu những gì đã cào.")
                break# Thoát loop safe mà ko bị loss data
    except KeyboardInterrupt:
        print(f"\n[Dừng khẩn câp] đang ở trang {page}. Đang cứu dữ liệu tạm...")
        is_interrupted = True
        
        # 5. Chuyển đổi list thành DF
    if all_reviews:
        df = pd.DataFrame(all_reviews)
        print(f"==> Thành công!!! Thu được {len(df)} đánh giá ")
        return df,is_interrupted
    else:
        print("==> Sản phẩm None Content Reviews!")
        return None,is_interrupted
        
def run_crawler_pipeline():
    os.makedirs('Data_crawl',exist_ok=True)

    if not os.path.exists(INPUT_FILE):
        print(f"LỖI: Không tìm thấy file '{INPUT_FILE}'!!!")
        print("Vui lòng kiểm tra lại file CSV đảm bảo có 2 cột: PRODUCT_ID VÀ SPID")
        return
    
    df_products = pd.read_csv(INPUT_FILE)

    #Checkpoint: Đã hốt những ai r
    crawed_ids = set()
    if os.path.exists(PATH_STORE):
        try:
            df_existing = pd.read_csv(PATH_STORE)
            if 'PRODUCT_ID' in df_existing.columns:
                crawed_ids = set(df_existing['PRODUCT_ID'].astype(str).unique())
                print(f"[CHECKPOINT] phát hiện {len(crawed_ids)} sản phẩm đã được cào. Bỏ quả ID này.")
        except  pd.errors.EmptyDataError:
            pass 

    for index, row in df_products.iterrows():
        prod_id = str(row['PRODUCT_ID']).strip()
        spid = str(row['SPID']).strip()

        #Bỏ qua data đã cào
        if prod_id in crawed_ids:
            print(f"\n[SKIP] Bỏ qua ID {prod_id} - Đã có trong database.")
            continue

        # Bắt đầu cào
        df_reviews,is_interrupted = get_tiki_reviews(prod_id,spid)

        # Lưu file ngay lập tức
        if df_reviews is not None and not df_reviews.empty:
            # Lưu ư cột ID để sau checkpoiny
            df_reviews['PRODUCT_ID'] = prod_id
            df_reviews['SPID'] = spid

            write_header = not os.path.exists(PATH_STORE)
            df_reviews.to_csv(PATH_STORE,mode ='a',header = write_header,index = False,encoding = 'utf-8-sig')
            print(f"[SAVE] Đã ghi an toàn dữ liệu của {prod_id} vào ổ cừng")

        # Nếu dừng đột ngootk -> Program out after store
        if is_interrupted:
            print("\n[THOÁT] Hệ thống đã lưu data an toàn và đóng chương trình.")
            break
                
        time.sleep(random.uniform(2.0,5.0))

if __name__ == "__main__":
    run_crawler_pipeline()
