# Bí kíp HTML slide — bộ skill đã cài và luật dùng chung

> Cài ngày 18/09/2026 vào `~/.claude/skills/` (mức người dùng, dùng được cho mọi dự án về sau).
> Nguồn: thư viện tuyển chọn [ToseaAI/awesome-html-slide-skills](https://github.com/ToseaAI/awesome-html-slide-skills)
> (bài Medium chỉ là bản tóm tắt của README này). Xếp hạng Tier theo số sao GitHub, cập nhật 06/2026.

## 1. Đã cài gì, vì sao chọn

| Skill | Tier · sao | Vai trò trong bộ | Sức mạnh thật sự (đọc từ mã nguồn, không phải quảng cáo) |
|---|---|---|---|
| **frontend-slides** (zarazhangrui) | S · 22,6 k — #1 toàn danh sách | **Phương pháp và khung sàn** | Quy tắc bất di bất dịch: sân khấu **1920 × 1080 cố định**, phóng nguyên khối theo cửa sổ (`viewport-base.css`), không reflow theo màn hình → không bao giờ tràn chữ như bản slide cũ. Quy trình "show, don't tell": làm 3 bản xem trước rồi mới chọn. 12 preset an toàn + 34 bản mẫu "bold" có chỉ mục theo mood/formality. Danh sách **cấm "AI slop"** (Inter/Roboto, tím-trên-trắng, mọi thứ căn giữa). `animation-patterns.md`: bảng *cảm giác → hoạt ảnh*. Chế độ chỉnh chữ trong trình duyệt, xuất PDF, deploy. Đây là skill Anthropic lấy làm ví dụ mẫu. |
| **html-ppt** (lewislulu) | S · 6,4 k | **Kho chuyển động và runtime** | Nhiều tính năng nhất danh sách: **27 hoạt ảnh CSS** (`data-anim`) + **20 hiệu ứng canvas** (`data-fx`: hạt, sao, mưa ma trận, đồ thị lực, mạng nơ-ron…), 36 theme dạng token CSS, 36 bố cục trang, **chế độ diễn giả** (phím S: xem trước slide kế, kịch bản nói, đồng hồ). Mượn: hệ hoạt ảnh vào/ra theo bước, hiệu ứng nền lặp, presenter mode. |
| **visual-explainer** (nicobailon) | S · 8,8 k | **Sơ đồ SVG inline cho nội dung kỹ thuật** | Mạnh nhất ở kiến trúc, luồng xử lý, so sánh, bảng dữ liệu, diff/plan review — đúng thứ đề tài cần (hook trong lớp, chunk-aware, bốn tầng). Bốn mỹ học có sẵn: Midnight Editorial (navy + serif + vàng), Terminal Mono, Warm Signal (giấy kem + đất nung), Swiss Clean (trắng + lưới). Sơ đồ là SVG vẽ trong file, sắc nét mọi cỡ, hoạt ảnh được từng phần tử. |
| **visual-cognition-slides** (edu-ai-builders) | B · 72 | **Sư phạm: mỗi slide một hành động nhận thức** | Khoa học nhận thức + thiết kế dạy học: mỗi slide trả lời "khán giả phải *làm gì trong đầu* ở đây?" — nhận ra, so sánh, theo dõi chuỗi, ghi nhớ một con số. Dành cho giảng viên, nghiên cứu sinh, bảo vệ luận văn. Có `PEDAGOGY.md`, `ANIMATIONS.md` (hoạt ảnh phục vụ hiểu, không trang trí), `INTERACTION.md`. |
| **beautiful-html-templates** (zarazhangrui) | Thư viện mẫu · 3,1 k | **Mẫu tham chiếu thị giác** | 32 bộ mẫu, mỗi bộ 3 slide (bìa · giữa · cuối) — là "sự thật thị giác" mà nhiều skill khác trích. Không có logic sinh; dùng để soi cách một hệ thị giác xử lý ba loại slide khác nhau trước khi cam kết. Đã bỏ thư mục ảnh chụp (64 MB) khi cài, giữ HTML gốc. |

**Không cài** (và vì sao): *huashu-design* (19,5 k) — mạnh về prototype/app/MP4, cần `npx`, rộng hơn nhu cầu; *guizang-ppt-skill* (18,6 k) — giọng "tạp chí điện tử", nền WebGL, tự nhận không hợp dữ liệu dày; *open-slide* — framework React, trái với nguyên tắc một file không phụ thuộc; *skills-slides* (checklist anti-slop) — luật đã có trong frontend-slides.

## 2. Bộ này hòa hợp thế nào — phân vai rõ, không giẫm chân

```
frontend-slides  → khung sàn 1920×1080 + quy trình chọn style + luật anti-slop   (LUẬT)
visual-cognition → quyết định slide này khán giả làm gì; bao nhiêu slide          (NỘI DUNG)
visual-explainer → vẽ sơ đồ SVG cho cơ chế, kiến trúc, so sánh                    (HÌNH)
html-ppt         → hoạt ảnh vào/ra, hiệu ứng nền, chế độ diễn giả               (CHUYỂN ĐỘNG)
beautiful-templates → soi mẫu thật khi phân vân một bố cục                        (THAM CHIẾU)
```

Khi ba skill cùng đòi trigger ("presentation"), gọi **frontend-slides** làm chủ; hai skill kia đọc như tài liệu tham khảo (`animation-patterns`, `ANIMATIONS.md`, `references/animations.md`).

## 3. Luật vàng rút ra (áp dụng cho mọi bộ slide từ nay)

1. **Sân khấu cố định 1920 × 1080**, JS phóng nguyên khối; dán trọn `viewport-base.css`; đổi slide bằng `visibility/opacity`, không `display:none`.
2. **Một ý một slide.** Speaker-led: ≤ 3 gạch đầu dòng, chữ lớn, nhiều slide hơn thay vì nhồi. Vượt là **tách slide**, không thu chữ.
3. **Hình trước, chữ sau.** Mỗi slide có một *thiết bị thị giác* (sơ đồ SVG, biểu đồ, ảnh, con số lớn). Chữ chỉ là nhãn cho hình.
4. **Hai loại hoạt ảnh, dùng đúng chỗ:** *lặp vô hạn* cho nền/không khí và ẩn dụ (tia chú ý chảy, mắt chớp, hạt trôi); *chạy một lần rồi dừng* cho cơ chế và số liệu (sơ đồ dựng lên, cột mọc, bộ đếm) — để khán giả còn đọc được trạng thái cuối. Reveal theo bước (phím) cho lập luận nhiều nhịp.
5. **Một khoảnh khắc lớn hơn mười vi tương tác:** mỗi slide tối đa một chuỗi vào có dàn nhịp (`animation-delay` bậc thang); chuyển slide 400–600 ms, easing `cubic-bezier(.16,1,.3,1)`.
6. **Font có cá tính, không Inter/Roboto/Arial**; luôn kèm fallback vì phòng bảo vệ có thể không có mạng.
7. **Bảng màu cam kết:** một nền, một chữ, **một** màu nhấn mạnh + một màu phụ. Không tím-gradient-trên-trắng.
8. **Sơ đồ = SVG inline** trong file; không ảnh chụp sơ đồ. Mọi số liệu chép từ `results/` + `docs/EXPERIMENTS.md`, ghi nguồn nhỏ ở chân slide.
9. **Kiểm bằng ảnh chụp thật** (Edge headless 1920 × 1080, cả trạng thái cuối `?all`), không tin `scrollHeight`.
10. **Chế độ diễn giả và PDF dự phòng** là bắt buộc trước khi mang đi trình bày.

## 4. Cách gọi trong Claude Code

- Làm mới: "Dùng skill frontend-slides, density speaker-led, style X, nội dung ở `ke_hoach_slide_v2.md`".
- Thêm sơ đồ: "Dùng visual-explainer vẽ sơ đồ SVG cho …".
- Thêm chuyển động: "Theo `~/.claude/skills/html-ppt/references/animations.md`, thêm hiệu ứng … cho slide …".
- Soát sư phạm: "Theo visual-cognition-slides, slide này khán giả phải làm gì? Có cần tách không?"
