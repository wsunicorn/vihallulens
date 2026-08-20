# T13 — Hướng dẫn gán nhãn kiểm chứng ánh xạ NEI

## Việc cần làm

Mỗi người mở **đúng file của mình** trong `results/`:

- Lân: `nei_mapping_audit_lan.csv`
- Minh: `nei_mapping_audit_minh.csv`

Mỗi file có **120 dòng**. Điền cột `nhan_dinh` cho từng dòng. Cột `ghi_chu` không bắt
buộc, nhưng dòng nào thấy khó thì ghi lại một câu — phần đó vào mục thảo luận của báo cáo.

**Làm độc lập.** Không trao đổi, không xem file của nhau cho tới khi cả hai điền xong. Nếu
bàn nhau trong lúc làm thì hệ số đồng thuận đo được sẽ vô nghĩa.

## Câu hỏi phải trả lời

Đọc **ngữ cảnh**, rồi đọc **phát biểu**. Câu hỏi duy nhất:

> Phát biểu này có nêu thông tin nào **không có trong ngữ cảnh** không?

Điền một trong bốn mã sau vào cột `nhan_dinh`:

| Mã | Nghĩa |
|---|---|
| `ngoai_lai` | Phát biểu nêu thông tin mà ngữ cảnh KHÔNG hề nhắc tới |
| `noi_tai` | Mọi thông tin đều có trong ngữ cảnh, nhưng phát biểu nói SAI hoặc mâu thuẫn |
| `khong` | Phát biểu bám sát ngữ cảnh: không thêm gì mới và cũng không mâu thuẫn |
| `khong_chac` | Không quyết được |

## Phân biệt bốn đáp án

Chỗ dễ nhầm nhất là giữa `ngoai_lai` và `noi_tai`. Cách phân biệt: hỏi xem **thông tin trong
phát biểu lấy từ đâu**.

- Nếu phát biểu nhắc tới một sự vật, con số, sự kiện mà **ngữ cảnh chưa từng nói đến** → thông
  tin đó đến từ bên ngoài → `ngoai_lai`.
- Nếu **mọi thứ trong phát biểu đều xuất hiện trong ngữ cảnh**, chỉ là bị nói ngược, bị gán
  sai cho nhau, hoặc sai con số → thông tin không đến từ bên ngoài, chỉ bị dùng sai →
  `noi_tai`.
- Nếu phát biểu chỉ diễn đạt lại điều ngữ cảnh đã nói, không thêm và không sai → `khong`.

Ví dụ. Ngữ cảnh:

> Hà Nội là thủ đô của Việt Nam. Thành phố Hồ Chí Minh là thành phố đông dân nhất cả nước.

| Phát biểu | Đáp án | Vì sao |
|---|---|---|
| Hà Nội là thủ đô của Việt Nam. | `khong` | Đúng như ngữ cảnh nói |
| TP.HCM là thủ đô của Việt Nam. | `noi_tai` | Hai vế đều có, chỉ bị **ghép sai** |
| Hà Nội có 8 triệu dân. | `ngoai_lai` | Ngữ cảnh không hề nói gì về **dân số** |

Nói gọn: `noi_tai` là **xáo trộn thứ đã có**, `ngoai_lai` là **mang thứ chưa có vào**.

**Lưu ý quan trọng:** đừng đánh giá phát biểu **đúng hay sai ngoài đời**. Chỉ so với ngữ cảnh
được cho. Một phát biểu hoàn toàn đúng sự thật nhưng ngữ cảnh không nhắc tới thì vẫn là
`ngoai_lai`.

Không quyết được thì `khong_chac`. **Đừng đoán bừa** — một dòng `khong_chac` trung thực có ích
hơn nhiều so với một dòng đoán.

## Sau khi cả hai điền xong

Lưu file, giữ nguyên tên, giữ nguyên định dạng CSV (Excel: *Save As* → *CSV UTF-8*). Rồi chạy:

```
python scripts/audit_nei_mapping.py --report
```

Lệnh này sinh `results/nei_mapping_audit.csv` và in ra tỷ lệ khớp cùng hệ số đồng thuận Cohen kappa.

## Một điều chưa nói cho tới khi làm xong

Trong 120 dòng có một số dòng **không phải** nhãn NEI. Đó là chủ ý: chúng dùng để kiểm tra
việc gán nhãn có thực sự được đọc kỹ hay không, và bước `--report` sẽ tách chúng ra khỏi thống
kê chính. Không cần tìm xem dòng nào là dòng nào — cứ đọc và gán như mọi dòng khác.
