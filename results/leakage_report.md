# Báo cáo rò rỉ ngữ cảnh

Sinh tự động bởi `scripts/split_data.py` ngày 27/08/2026. Đừng sửa tay — chạy lại lệnh.

## Rò rỉ là gì và vì sao phải đo

Hai mẫu dùng chung một ngữ cảnh thì không độc lập với nhau: mô hình đã thấy một mẫu
lúc huấn luyện thì cũng đã thấy gần hết phần vật liệu của mẫu kia. Nếu chúng nằm ở
hai tập khác nhau, điểm trên tập test đo **trí nhớ** nhiều ngang đo **khả năng khái
quát hóa**, và con số báo cáo sẽ đẹp hơn sự thật.

Vì vậy đơn vị chia tập là `context_id` chứ không phải dòng — mục 5 `docs/DATA.md`.
Bảng dưới đếm hai kiểu: theo **ngữ cảnh** cho biết bao nhiêu vật liệu bị dùng lại,
theo **dòng** cho biết bao nhiêu phần điểm số thật sự dựa lên đó. Con số theo dòng
thường lớn hơn và mới là con số đáng lo.

## Tập do nhóm tự chia — ViHallu và ISE-DSC01

Chia 80/10/10 theo `context_id`, seed 42, bằng `group_split`.
Hàm này raise nếu có bất kỳ ngữ cảnh nào lọt vào hai tập, nên **rò rỉ ở đây bằng 0
theo thiết kế**; bảng dưới là bằng chứng chứ không phải kỳ vọng.

| Bộ | Tập | Dòng | Tỷ lệ | Ngữ cảnh | Rò rỉ ngữ cảnh | Rò rỉ dòng |
|---|---|---|---|---|---|---|
| vihallu | train | 5,600 | 80.0 % | 3,092 | — | — |
| vihallu | dev | 700 | 10.0 % | 394 | 0/394 | 0/700 |
| vihallu | test | 700 | 10.0 % | 379 | 0/379 | 0/700 |
| isedsc01 | train | 29,077 | 79.9 % | 3,811 | — | — |
| isedsc01 | dev | 3,646 | 10.0 % | 493 | 0/493 | 0/3646 |
| isedsc01 | test | 3,646 | 10.0 % | 489 | 0/489 | 0/3646 |

### Phân bố nhãn sau khi chia

Chia theo nhóm ngữ cảnh thì **không** ép được cân bằng nhãn cùng lúc — hai ràng buộc
đó xung khắc nhau. Bảng này để thấy việc chia có làm lệch nhãn hay không.

| Bộ | Tập | no | intrinsic | extrinsic |
|---|---|---|---|---|
| vihallu | train | 1,780 (31.8 %) | 1,984 (35.4 %) | 1,836 (32.8 %) |
| vihallu | dev | 225 (32.1 %) | 230 (32.9 %) | 245 (35.0 %) |
| vihallu | test | 240 (34.3 %) | 234 (33.4 %) | 226 (32.3 %) |
| isedsc01 | train | 10,193 (35.1 %) | 8,856 (30.5 %) | 10,028 (34.5 %) |
| isedsc01 | dev | 1,291 (35.4 %) | 1,086 (29.8 %) | 1,269 (34.8 %) |
| isedsc01 | test | 1,302 (35.7 %) | 1,058 (29.0 %) | 1,286 (35.3 %) |

## Tập giữ nguyên split gốc — ViWikiFC và ViFactCheck

Hai bộ này **giữ split gốc** để so được với số đã công bố, nên nhóm phải nhận luôn
phần rò rỉ có sẵn trong đó. Không sửa được, chỉ báo cáo được.

| Bộ | Tập | Dòng | Ngữ cảnh | Rò rỉ ngữ cảnh | Rò rỉ dòng |
|---|---|---|---|---|---|
| viwikifc | dev | 2,090 | 838 | 836/838 (99.8 %) | 2088/2090 (99.9 %) |
| viwikifc | test | 2,091 | 845 | 845/845 (100.0 %) | 2091/2091 (100.0 %) |
| vifactcheck | dev | 723 | 496 | 495/496 (99.8 %) | 721/723 (99.7 %) |
| vifactcheck | test | 1,447 | 758 | 753/758 (99.3 %) | 1433/1447 (99.0 %) |

**Hệ quả bắt buộc ghi vào báo cáo:** không dùng ViWikiFC và ViFactCheck để kết luận
về khả năng khái quát hóa. Tập test của ViWikiFC dùng lại **toàn bộ** ngữ cảnh của
train, nên điểm trên đó không nói gì về dữ liệu chưa từng thấy. Chúng vẫn dùng được
làm đối chứng ngoài phân phối huấn luyện của ViHallu, và để so với số đã công bố.

## File public test — không dùng, nhưng là lý do phải tự chia

ViHallu và ISE-DSC01 có file public test nhưng **không có nhãn dùng được**, nên nhóm
không dùng chúng. Vẫn đo phần rò rỉ của chúng, vì đây là bằng chứng cho thấy split do
ban tổ chức phát hành cũng rò rỉ — tức việc nhóm tự chia không phải là làm khó mình.

| Bộ | Ngữ cảnh test public có trong train |
|---|---|
| vihallu | 713/919 (77.6 %) |
| isedsc01 | 1,004/1,319 (76.1 %) |

## Cách tái lập

```
python scripts/normalize_data.py --all
python scripts/split_data.py
```

Dữ liệu đọc từ `data/interim`. Chạy lại cho ra đúng kết quả này: nhóm
ngữ cảnh được sắp theo `context_id` trước khi xáo, nên seed 42 là đủ.
