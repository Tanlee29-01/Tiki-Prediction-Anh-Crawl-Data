import requests
import pandas as pd
import time
import random
import os
import re
from fake_useragent import UserAgent
from tenacity import retry,stop_after_attempt,wait_exponential,retry_if_exception_type
UA_Random = UserAgent()# Dùng để tạo user giả
PATH_STORE = 'Data_crawl/tiki_reviews.csv'
INPUT_FILE = 'product_book.csv'
CHECKPOINT_FILE = 'Data_crawl/checkpoint.txt'
def normalize_text(text: str) -> str:
    if text is None:
        return ""
    text = str(text)
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    text = text.replace("\t", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Bọc Tenacity cho hàm API để retry auto
@retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1,min=2,max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
)
def fetch_api_with_retry(session,url,timeout = 10):
    response = session.get(url,timeout = timeout)

    if session.status_code in [403,404]:
        raise ValueError(f"Lỗi bị chặn hoặc không tìm thấy {response.status_code}")
    
    response.raise_for_status()
    return retry.json()

#-------------------------------------
# Hàm cào data chính
#------------------------------------

def get_tiki_reviews(PRODUCT_ID,SPID,session):
    #session = requests.Session()

    #1. Setting cấu hình cho bot 
    session.headers.update = {
        'User-Agent':UA_Random.random,
        'Accept':'application/json, text/plain,*/*',
    }
    print(f"Đang lấy dữ liệu từ sản phẩm ID: {PRODUCT_ID}...")

    try:
        prod_data = fetch_api_with_retry(session=session,url=f"https://tiki.vn/api/v2/products/{PRODUCT_ID}")
        product_name = prod_data.get('name','Không xác định')
        print(f"Tên sản phẩm {product_name}")
    except Exception as e:
        print(f"Lỗi mạng khi lấy thông tin sản phẩm: {e}. Bỏ qua SP {PRODUCT_ID}")
        return None
    
    #3. Chuẩn bị danh sách để lưu dữ liệu đánh giá
    all_reviews = []
    page = 1

    #4. Loop để lấy đánh giá từ nhiều trang

    while True:
        print(f"Đang tải đánh giá trang {page}....")
        # Đường dẫn API từ tiki
        review_api_url = f"https://tiki.vn/api/v2/reviews?limit=5&include=comments,contribute_info,attribute_vote_summary&sort=score|desc,id|desc,stars|all&page={page}&spid={SPID}&product_id={PRODUCT_ID}"
        try:
            #1. Đừng dẫn
            data = fetch_api_with_retry(session=session,url=review_api_url)
            reviews = data.get('data',[])
            # 2. Điều kiện dừng
            if not reviews:
                print("Đã lấy hết các trang đánh giá!")
                break
            
            #3. Lưu data
            for review in reviews:
                content = normalize_text(review.het('content',''))
                
                if content and content.strip():
                    all_reviews.append({
                        'PRODUCT_ID':PRODUCT_ID,
                        'SPID':SPID,
                        'Tên sản phẩm': product_name,
                        'Số sao': review.get('rating',0),
                        'Nội dung đánh giá': content
                    })
            # Nhảy lên trang  kế tiếp và ngủ để tránh ban IP
            page += 1
            time.sleep(random.uniform(1.5,3.0))

        except ValueError as va:
            print(f"Bị block hoặc lỗi mạng {va}.")
            return None# Thoát loop safe mà ko bị loss data
        except Exception as e:
            print(f"Lỗi mạng không thể cứu được trang {page}: {e}")
            print("Bỏ dữ liệu cào dở để tránh trùng lặp rác.")
            return None
    return pd.DataFrame(all_reviews) if all_reviews else pd.DataFrame()

#---------------------------------------
#3. pipeline design to manage checkpoint
#---------------------------------------
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE,'r') as f:
            return set(line.strip() for line in f)
    return set()

def save_checkpoint(product_id):
    with open(CHECKPOINT_FILE,'a') as f:
        f.write(f"{product_id}\n")

def run_crawler_pipeline():
    os.makedirs('Data_crawl',exist_ok=True)

    if not os.path.exists(INPUT_FILE):
        return print(f"LỖI: Không tìm thấy file '{INPUT_FILE}'!!!")
        
    
    df_products = pd.read_csv(INPUT_FILE)

    #Checkpoint: Đã hốt những ai r
    crawed_ids = load_checkpoint()
    print(f"[CHECKPOINT] Đã cào xong trọn vẹn {len(crawed_ids)} sản phẩm.")
    session = requests.Session()
    
    for _, row in df_products.iterrows():
        prod_id = str(row['PRODUCT_ID']).strip()
        spid = str(row['SPID']).strip()

        if prod_id in crawed_ids:
            print(f"[SKIP] Đã có ID {prod_id}. Bỏ qua.")
            continue

        df_reviews = get_tiki_reviews(prod_id,spid,session)

        if df_reviews is not None:
            if  not df_reviews.empty:
                write_header = not os.path.exists(PATH_STORE)
                df_reviews.to_csv(PATH_STORE,mode='a',header=write_header,index=False,encoding='utf-8-sig')
                print(f"Đã lưu {len(df_reviews)} dòng .")
            else:
                print("Sản phẩm không có đánh giá!!!")

            save_checkpoint(prod_id)

if __name__ == "__main__":
    run_crawler_pipeline()
