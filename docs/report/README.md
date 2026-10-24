# Nguồn của báo cáo khóa luận

Thư mục này chứa **bản thảo theo chương** của `docs/BaoCao_KLTN.md`. Sửa báo cáo thì sửa ở
đây, không sửa trực tiếp `BaoCao_KLTN.md` — tệp đó được sinh ra và sẽ bị ghi đè.

## Quy trình ba bước

```bash
python docs/media/src/charts.py          # 1a. vẽ lại biểu đồ (matplotlib)
python docs/media/src/method_figs.py     # 1b. vẽ lại sơ đồ (SVG + Chrome headless)
python docs/media/src/concept_figs.py
python docs/media/src/fig_tong_quat_he_thong.py
python docs/media/src/fig_terminal.py

python docs/tools/resolve.py             # 2. ghép chương, đánh số, dựng mục lục và tài liệu
python docs/tools/build_docx.py          # 3. dựng .docx theo mẫu của Khoa + xuất PDF
```

Bước 3 cần Microsoft Word (dùng COM để cập nhật trường, mục lục và dựng công thức) và
`pandoc`. **Word phải đang đặt chế độ nhập công thức là LaTeX** (Insert → Equation →
Conversions → LaTeX); nếu không, bản dựng sẽ dừng và báo lỗi.

## Công cụ cần có

Chuỗi dựng chạy trên Windows. Cột phải là phiên bản đã dựng ra quyển nộp (22/10/2026):

| Công cụ                                 | Dùng ở bước                              | Phiên bản đã dùng                 |
| --------------------------------------- | ---------------------------------------- | --------------------------------- |
| Python, matplotlib, Pillow              | 1 — vẽ hình                              | 3.11.6, 3.10.0, 12.0.0            |
| Google Chrome (chạy không giao diện)    | 1 — chụp sơ đồ SVG/HTML thành PNG        | 155.0.8059.80                     |
| Font Arial                              | 1 — `svgkit` đo chữ để ngắt dòng         | có sẵn trên Windows               |
| Node.js                                 | chụp lại ảnh trang web (`shoot_site.mjs`) | 22.15.0                          |
| pandoc                                  | 3                                        | 3.9.0.2                           |
| python-docx, pywin32                    | 3                                        | 1.2.0, 308                        |
| Microsoft Word                          | 3                                        | 16.0.20430                        |

Môi trường `uv sync` của dự án có matplotlib (nhóm `dev`) nhưng không có python-docx và pywin32,
nên cài thêm vào trình thông dịch dùng để dựng:

```bash
pip install matplotlib pillow python-docx pywin32
```

Chrome cài ở chỗ khác `C:\Program Files\Google\Chrome\Application\` thì đặt biến môi trường
`CHROME_PATH` trỏ tới `chrome.exe`; `method_figs.py`, `concept_figs.py`, `render.sh` và
`shoot_site.mjs` đều đọc biến này. Thiếu Arial, `svgkit` ước lượng độ rộng chữ thay vì đo, nên
chỗ ngắt dòng trong sơ đồ sẽ khác bản trong quyển.

## Cách viết trong bản thảo

Bản thảo dùng **nhãn** thay cho số, nên chèn thêm một hình hay một mục ở giữa chương không
làm sai số của những phần sau.

| Việc cần làm              | Viết trong bản thảo                                  | Kết quả sau khi ghép |
| ------------------------- | ---------------------------------------------------- | -------------------- |
| Đề mục                    | `## [[sec:c3-chia-tap]] Chia tập theo ngữ cảnh`       | `## 3.4 Chia tập …`  |
| Chú thích hình            | `*[[fig:hook]] Cơ chế trích đặc trưng*`               | `*Hình 4.4 Cơ chế …*`|
| Chú thích bảng            | `*[[tab:dac-trung]] Năm đặc trưng*`                   | `*Bảng 4.1 Năm …*`   |
| Số công thức              | `\tag{[[eq:lookback]]}`                               | `\tag{2.4}`          |
| Nhắc tới hình/bảng/mục    | `[[fig:hook]]`, `[[tab:dac-trung]]`, `[[sec:c3-…]]`   | `Hình 4.4`, `Bảng 4.1`, `mục 3.4` |
| Trích dẫn tài liệu        | `[@chuang2024]` hoặc `[@a; @b]`                       | `[4]` hoặc `[4], [9]`|

Danh mục tài liệu tham khảo nằm trong từ điển `BIB` của `docs/tools/resolve.py`; thứ tự
đánh số do họ tác giả quyết định, không do thứ tự trích dẫn.

`resolve.py` báo lỗi hoặc cảnh báo khi: thiếu khóa tài liệu, nhãn trùng, hình hoặc bảng
không được nhắc tới trong thân bài (hoặc chỉ được nhắc sau khi đã xuất hiện), một mục chỉ
có đúng một mục con, và khi tệp ảnh không tồn tại.

## Công thức

Viết LaTeX trong khối `$$ … $$` và kết thúc bằng `\tag{[[eq:key]]}`. Word dựng công thức từ
chính đoạn LaTeX đó, nên chỉ dùng các lệnh Word hiểu: `\frac`, `\sum_{}^{}`, `\max_{}`,
`\arg\max`, `\ln`, `\exp`, `\sqrt`, `\mathrm`, `\operatorname`, `\text{}` (có dấu tiếng
Việt được), `\mathbf`, `\mathcal`, `\mathbb`, `\hat`, `\overline`, `\left…\right`,
`\lVert`, `\top`, `\mid`, `\cdot`, `\times`, `\in`, `\le`, `\ge`, `\neq`, `\approx`,
`\propto`, `\cdots`, `\,` `\;` `\quad` `\qquad`, `\underbrace`, `\underset`, `\%`. Dấu phẩy
thập phân viết là `0{,}75`. Công thức dài thì ngắt dòng bằng `\\`. Không dùng `\begin{…}`,
`#()` hay `\tag` bên trong công thức để đánh số — số do trường SEQ của Word tự sinh.

## Ảnh chụp trang web

Bảy hình `anh_*.png` là ảnh chụp trang giới thiệu, giao diện quan sát và trang tài liệu
OpenAPI (`/docs`), **đều ở chế độ nền sáng** (`?theme=light`) cho dễ in. Khung chụp mặc định
rộng **780 px** ở mật độ điểm ảnh ×2 (`--width`, `--scale`, đổi từ 1.100 px ngày 09/10/2026):
in rộng 15,5 cm thì một px CSS là 0,56 pt, nên chữ thân 16 px của trang in ra khoảng 9 pt. Ở bề
rộng này phần demo xuống một cột và ba thẻ "cách dùng" xếp chồng, nên mỗi ảnh được cắt (`clip`)
sát khối mà chú thích của nó nói tới thay vì theo chiều cao cửa sổ. Riêng `anh_trang_chu_hero`
giữ bố cục máy tính (thẻ tiêu đề cạnh con cú) — hẹp hơn khoảng 1.000 px thì thẻ tràn mép trái —
nên chụp khung 1.100 px rồi cắt lấy thẻ và con cú. Chụp lại bằng hai bước — chạy dịch vụ ở chế độ
phát lại (không cần GPU, kết quả lấy từ `replay.json`, tức phiên Kaggle 11/09/2026), rồi
chạy script điều khiển Chrome không giao diện qua DevTools protocol:

```bash
python -c "import sys; sys.path.insert(0,'src'); import uvicorn;   from vihallulens.serve.app import create_app;   uvicorn.run(create_app(detector=None, load_on_startup=False), port=8000)" &

node docs/media/src/shoot_site.mjs --out docs/media
```

Script tự bấm nút giúp: hình `anh_demo_rag` và `anh_giao_dien_quan_sat` cần bấm câu hỏi
RAG thứ hai, `anh_phat_hien_ngoai_lai` cần bấm ví dụ "Ngoại lai". Nó cũng ẩn bong bóng
thoại của con cú và con cú nhỏ ở góc phải dưới (`#buddy`, nút "ẩn cú") — cả hai hay che
mất chữ — và chờ thanh trạng thái hết "đang kiểm dịch vụ…" rồi mới chụp.

Khối hero của trang có nền đen **cứng trong CSS** (`#hero { background: #000 }`), không
theo biến theme, nên `anh_trang_chu_hero` vẫn là nền tối dù chụp ở chế độ sáng — đây là
lựa chọn có chủ ý, không sửa `src/`. Script chụp nó ở `?p=1`, tức nhịp cuối của khối
hero, nơi thẻ tiêu đề sáng màu chiếm phần lớn khung.

## Hình vẽ

Hình `hinh_trich_huanluyen_phucvu` vẽ bằng JavaScript (rough.js) nên **không chụp được qua
`file://`** — Chrome chặn script của trang cục bộ và ảnh chụp sẽ trắng. Chạy một máy chủ
tĩnh ở thư mục `docs/media` rồi chụp qua HTTP:

```bash
cd docs/media && python -m http.server 8932 &
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless --disable-gpu \
  --hide-scrollbars --force-device-scale-factor=2 --virtual-time-budget=6000 \
  --window-size=1720,1140 --screenshot=hinh_trich_huanluyen_phucvu.png \
  http://localhost:8932/src/fig_trich_huanluyen_phucvu.html
```

Sơ đồ được vẽ trên khung rộng **900 px** (xem ghi chú đầu `docs/media/src/method_figs.py`):
một hình in ngang khổ chữ 15,5 cm bị thu theo tỷ lệ 439 pt / bề rộng khung, nên chữ 15 px
trên khung 900 px còn 7,3 pt trên giấy — đọc được; cũng nội dung ấy trên khung 1.600 px chỉ
còn 4 pt. Vì vậy sơ đồ xếp theo chiều dọc chứ không dàn ngang.

Cỡ chữ trong sơ đồ dùng các cỡ đặt tên ở đầu `method_figs.py` (`T_SMALL` 18 px ≈ 8,8 pt là
sàn, `T_BODY` 19,5 px ≈ 9,5 pt, `T_LABEL`, `T_TITLE`); `concept_figs.py` và
`fig_tong_quat_he_thong.py` dùng chung. Một sơ đồ cao tối đa khoảng **1.250 px** trên khung 900
px (≈ 21,5 cm) để vừa một trang cùng chú thích. `svgkit.wrap` đo độ rộng chữ bằng chính font
Arial (qua PIL) nên ngắt dòng đúng chỗ; nhãn căn giữa được ngắt **cân bằng** (không để một
chữ lẻ ở dòng cuối).

Biểu đồ matplotlib (`bieudo_*`) luôn in rộng 14 cm, nên `charts.py` tự co khung hình trước
khi lưu (`fit_to_print`) sao cho chữ in ra đúng `PRINT_SCALE` × cỡ khai báo — hiện là 1,0, tức
nhãn 10 pt in ra 10 pt. Muốn chữ to hơn thì tăng `PRINT_SCALE`, **đừng** sửa `figsize` — cỡ
khung chỉ còn quyết định tỷ lệ cao/rộng. Trục hai chữ số thập phân dùng `vn_axis` để không bao
giờ có bước 0,025 (in thành "0,03", "0,08"). Sau khi vẽ lại, xem từng hình xem nhãn có đè nhau
không.

Hình ngang `hinh_trich_huanluyen_phucvu` bị giới hạn bởi **chiều cao** trang ngang (hình +
chú thích chung 14 cm, vì trang ngang giữ lề 3,5 cm ở cả hai mép dài — xem mục dàn trang
dưới đây), nên rộng 19,2 cm dù trang còn 23,7 cm. Cỡ chữ của nó chỉnh bằng `TEXT_SCALE` trong
tệp HTML (hiện 1,3 — thử 1,45 thì nhãn đè nhau và tràn hộp), không phải bằng bề rộng in.

Hình terminal (`fig_terminal.py`) và thuật toán (`method_figs.fig_thuat_toan`) dựng từ HTML;
`render(..., trim=True)` cắt phần trắng thừa dưới chân nên cửa sổ chụp có thể để dư chiều cao.
Pandoc tự giới hạn ảnh ở 14,82 cm; `build_docx.py` trả các hình rộng về đủ 15,5 cm.

## Dàn trang

Quyển in **một mặt** giấy, đúng chữ trong mẫu của Khoa ("trình bày trên một mặt giấy"); GVHD
chốt điều này ngày 05/10/2026, sau khi nhóm thử dàn hai mặt từ 28/09. `build_docx.py`, hàm
`build_sections()`, `page_header()` và `page_footer()`:

- **Lề** trái 3,5 cm, phải 2 cm, trên và dưới 3 cm ở mọi trang dọc.
- **Chân trang** (tên hai sinh viên bên trái, số trang góc phải) có từ trang ABSTRACT, đánh số
  La Mã; **header** (tên khóa luận, căn trái) bắt đầu từ Chương 1. Bìa không có cả hai.
- Mỗi bìa và mỗi phần (trang đầu, các chương, tài liệu tham khảo – phụ lục) sang trang mới.
- **Trang ngang** (Hình 5.1) vẫn giữ lề 3,5 cm ở cả hai mép dài và header/chân trang cách mép
  2,2 cm như hồi dàn hai mặt; nhóm giữ nguyên thay vì nới hình lên 21,4 cm.

Khi đưa đi in: in toàn bộ PDF **một mặt**, cỡ thật 100 % (không "fit to page"). Trang ngang in
trên tờ A4 thường; dặn tiệm in để máy tự xoay trang.
