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

## Phép thử khi phân vân

Ba gạch đầu dòng trên đủ cho phần lớn dòng. Gặp ca khó thì dùng phép thử này, sắc hơn:

> **Chỉ với ngữ cảnh này thôi, tôi có BÁC BỎ được phát biểu không?**

| Trả lời | Nghĩa | Mã |
|---|---|---|
| Bác bỏ được | Ngữ cảnh nói về đúng chuyện đó, và nói khác đi | `noi_tai` |
| Không bác bỏ được, cũng không xác nhận được | Ngữ cảnh im lặng về chuyện đó | `ngoai_lai` |
| Xác nhận được | Ngữ cảnh nói đúng như vậy | `khong` |

## Số liệu sai thì tính là gì?

Câu hỏi hay gặp nhất. Trả lời ngắn: **`noi_tai`**, nếu ngữ cảnh có nói về con số đó.

Chỗ dễ nhầm: một con số sai thì bản thân **giá trị mới** không xuất hiện trong ngữ cảnh, nghe
như "mang thứ chưa có vào". Nhưng phép thử **không phải** là "con số đó có trong ngữ cảnh
không" — mà là **ngữ cảnh có nói về thuộc tính đó của thực thể đó không**. Nếu có, thì mọi sai
lệch về nó là **mâu thuẫn**, không phải thông tin mới.

Ví dụ. Ngữ cảnh: *"Khoảng 65% bệnh nhân genotype 4 đáp ứng lâu dài với 48 tuần điều trị."*

| Phát biểu | Đáp án | Vì sao |
|---|---|---|
| 65% bệnh nhân genotype 4 đáp ứng với **72 tuần**. | `noi_tai` | Ngữ cảnh nói 48, bác bỏ được |
| **30%** bệnh nhân genotype 4 đáp ứng với 48 tuần. | `noi_tai` | Ngữ cảnh nói 65%, bác bỏ được |
| 65% bệnh nhân **genotype 5** đáp ứng với 48 tuần. | `ngoai_lai` | Không nói gì về genotype 5 |
| Genotype 4 tốn **12 triệu đồng** mỗi đợt. | `ngoai_lai` | Không nói gì về chi phí |

**Diễn đạt lỏng thì khác với nói sai.** "48 tuần" viết lại thành *"gần 50 tuần"* là **diễn đạt
lại** — 48 đúng là gần 50 — nên `khong`, không phải `noi_tai`. Chỉ tính là `noi_tai` khi giá
trị mới **loại trừ** giá trị trong ngữ cảnh: "72 tuần" thì không cách nào là 48.

Ranh giới này có chỗ mờ, nhất là khi phát biểu **đổi cả cách nói** chứ không chỉ đổi số — ví dụ
*"đáp ứng lâu dài"* thành *"thích nghi"*, hai khái niệm không hẳn trùng nhau. Gặp ca mờ thì
`khong_chac` kèm một dòng `ghi_chu` là câu trả lời trung thực nhất. **Chính những dòng đó là
phần đáng bàn nhất trong báo cáo** — chúng cho thấy ranh giới giữa ba lớp nhãn mờ tới đâu.

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
