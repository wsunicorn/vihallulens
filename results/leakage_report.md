# Báo cáo rò rỉ ngữ cảnh

Sinh tự động bởi `scripts/split_data.py` ngày 23/08/2026. Đừng sửa tay — chạy lại lệnh.

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
| vihallu | train | 5,598 | 80.0 % | 3,089 | — | — |
| vihallu | dev | 702 | 10.0 % | 389 | 0/389 | 0/702 |
| vihallu | test | 700 | 10.0 % | 387 | 0/387 | 0/700 |
| isedsc01 | train | 29,082 | 80.0 % | 3,819 | — | — |
| isedsc01 | dev | 3,653 | 10.0 % | 489 | 0/489 | 0/3653 |
| isedsc01 | test | 3,634 | 10.0 % | 485 | 0/485 | 0/3634 |

### Phân bố nhãn sau khi chia

Chia theo nhóm ngữ cảnh thì **không** ép được cân bằng nhãn cùng lúc — hai ràng buộc
đó xung khắc nhau. Bảng này để thấy việc chia có làm lệch nhãn hay không.

| Bộ | Tập | no | intrinsic | extrinsic |
|---|---|---|---|---|
| vihallu | train | 1,798 (32.1 %) | 1,943 (34.7 %) | 1,857 (33.2 %) |
| vihallu | dev | 227 (32.3 %) | 257 (36.6 %) | 218 (31.1 %) |
| vihallu | test | 220 (31.4 %) | 248 (35.4 %) | 232 (33.1 %) |
| isedsc01 | train | 10,269 (35.3 %) | 8,755 (30.1 %) | 10,058 (34.6 %) |
| isedsc01 | dev | 1,278 (35.0 %) | 1,109 (30.4 %) | 1,266 (34.7 %) |
| isedsc01 | test | 1,239 (34.1 %) | 1,136 (31.3 %) | 1,259 (34.6 %) |

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
