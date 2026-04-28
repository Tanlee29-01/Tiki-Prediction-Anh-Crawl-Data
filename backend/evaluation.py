from sklearn.metrics import accuracy_score,precision_score,recall_score
from typing import Dict,List
def evaluation_fraud_model(y_true: List[int], y_pred: List[int]) -> Dict[str,float]:
    """
    Đánh giá model phát hiện gian lận.
    Use zẻo_division =0 để tránh lỗi log khi lên production khi model dự đoán = 0
    """
    return{
        "accuracy":accuracy_score(y_true,y_pred),
        "precision":precision_score(y_true,y_pred),
        "recall":recall_score(y_true,y_pred),
    }

# Cho trước dữ liệu (9 hợp lệ, 1 gian lận)
y_true = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1] 

# Model đoán toàn bộ là hợp lệ (0)
y_pred = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
metrics = evaluation_fraud_model(y_true,y_pred)
print(metrics)