# Báo Cáo Thực Hành MLOps: Từ Thực Nghiệm Cục Bộ Đến CI/CD & CT

- **Họ và tên:** Ngô Khánh Trương
- **Mã sinh viên:** 2a202601477
- **Repo GitHub:** https://github.com/khanhtruong04/Day21-Track2-NgoKhanhTruong-2a202601477
- **Cloud Provider sử dụng:** AWS (Amazon S3 + EC2)
- **Public IP Máy ảo EC2:** 35.175.112.195

---

## 1. Kết Quả Bước 1 - Siêu tham số tối ưu (MLflow Tracking)
- **Bộ siêu tham số tốt nhất:**
  - `n_estimators`: 300
  - `max_depth`: 15
  - `min_samples_split`: 2
- **Lý do lựa chọn:** Khi tăng số lượng cây (`n_estimators`) lên 300 và độ sâu (`max_depth`) lên 15, mô hình RandomForest học được các đặc trưng phi tuyến tốt hơn của tập Wine Quality, giúp cân bằng giữa độ chính xác và tránh overfitting.

---

## 2. Kết Quả So Sánh Bước 2 và Bước 3 (Mục 3.6)

| Chỉ số | Bước 2 (Phase 1: 2998 mẫu) | Bước 3 (Phase 1 + 2: 5996 mẫu) | Mức độ cải thiện |
|---|---|---|---|
| **Accuracy** | **0.6700** | **0.7480** | **+7.80%** |
| **F1 Score** | **0.6685** | **0.7468** | **+7.83%** |

- **Đánh giá Eval Gate:**
  - Ở Bước 2, với 2998 mẫu, mô hình chỉ đạt accuracy `0.6700` (< 0.70) ➔ Hệ thống kích hoạt Eval Gate và tự động **chặn Deploy** thành công.
  - Ở Bước 3, khi bổ sung 2998 mẫu dữ liệu mới (`train_phase2`), accuracy tăng vọt lên `0.7480` (>= 0.70) ➔ Hệ thống vượt qua Eval Gate và tự động **Deploy lên EC2**.

---

## 3. Khó Khăn Gặp Phải & Cách Giải Quyết
1. **Lỗi Region S3 khi DVC pull:** S3 bucket được tạo ở Region `ap-southeast-1` (Singapore) trong khi pipeline ban đầu cấu hình `us-east-1` ➔ *Giải pháp:* Cập nhật cấu hình region đồng bộ sang `ap-southeast-1` trong `mlops.yml` và DVC remote.
2. **Lỗi SSH Timeout trên GitHub Actions:** AWS Security Group mặc định chỉ cho phép IP cá nhân kết nối SSH port 22 ➔ *Giải pháp:* Cấu hình Inbound Rules mở port 22 và port 8000 sang `0.0.0.0/0` (Anywhere-IPv4).
3. **Thời gian tải model từ S3 trên EC2:** Service FastAPI cần thời gian tải model khi khởi động ➔ *Giải pháp:* Thiết lập vòng lặp retry health check trong job Deploy với timeout phù hợp.
