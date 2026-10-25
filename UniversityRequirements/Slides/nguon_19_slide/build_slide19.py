"""Build the 19-slide defence deck from Lân's 32-slide HTML deck of 02/10/2026.

Run from UniversityRequirements/Slides:

    python nguon_19_slide/build_slide19.py nguon_19_slide/slide_goc_32.html slide_rut_gon_19.html

The input is never modified; the output is self-contained and opens offline. The 23-slide deck is
then rebuilt from it with nguon_bo_sung_15-10/bo_sung_slide_minh.py (steps in HUONG_DAN.md).

Every text edit is an exact string replacement with an asserted match count, so a change in
the source deck stops the build instead of silently skipping a fix. Numbers follow the v4
report and results/runs.jsonl.
"""

# Slide text and verbatim lines of the source deck's JavaScript stay whole, so that every
# replacement below can be found in the deck by search.
# ruff: noqa: E501

import html
import re
import sys
from pathlib import Path

SRC, OUT = (Path(p) for p in sys.argv[1:3])


def sub(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        sys.exit(f"expected {count} match(es), found {n}: {old[:90]!r}")
    return text.replace(old, new)


s = SRC.read_text(encoding="utf-8")

# ---------------------------------------------------------------- split the file
style_end = s.index("</style>")
first_sec = s.index('<section class="slide')
last_sec_end = s.rindex("</section>") + len("</section>")
first_script = s.index("<script>", last_sec_end)
head, css = s[:s.index("<style>") + len("<style>")], s[s.index("<style>") + len("<style>"):style_end]
body_pre = s[style_end:first_sec]
body_post = s[last_sec_end:first_script]
scripts = re.findall(r"<script>(.*?)</script>", s[first_script:], flags=re.S)
tail = s[first_script:][s[first_script:].rindex("</script>") + len("</script>"):]
assert len(scripts) == 3, len(scripts)
gsap_js, data_js, figs_js = scripts
sections = re.findall(r'<section class="slide.*?</section>', s[first_sec:last_sec_end], flags=re.S)
assert len(sections) == 32, len(sections)

LOGO = re.search(r'<img class="logo rise r1" src="([^"]+)"', sections[0]).group(1)
OWL = re.search(r'<img class="owl rise r2" src="([^"]+)"', sections[1]).group(1)
BEAMS = re.search(r'<svg class="beams".*?</svg>', sections[1], flags=re.S).group(0)
# the third, faintest beam ends on the supervisor's label in the merged cover
BEAMS = sub(BEAMS, '\n    <path d="M1395 340 C 1300 640, 1100 730, 900 760" stroke-width="1.5" opacity=".14"/>', "")


def by_fig(name):
    hits = [x for x in sections if f'data-fig="{name}"' in x]
    assert len(hits) == 1, name
    return hits[0]


def run_header(label):
    return (f'<div class="run"><span class="l"><img src="{LOGO}" alt="IUH">Phát hiện ảo giác cho RAG tiếng Việt</span>'
            f'<span class="sec">{label}</span></div>')


def notes_attr(text):
    return html.escape(text, quote=True)


def restyle(sec_html, label, notes, foot, num, h2=None):
    """Swap chapter label, speaker notes, footer and slide number of a copied section."""
    out = re.sub(r'data-notes="[^"]*"', 'data-notes="' + notes_attr(notes) + '"', sec_html, count=1)
    out, n = re.subn(r'<span class="sec">[^<]*</span>', f'<span class="sec">{label}</span>', out)
    assert n == 1, label
    if h2 is not None:
        out, n = re.subn(r"<h2>.*?</h2>", "<h2>" + h2 + "</h2>", out, flags=re.S)
        assert n == 1, h2
    out, n = re.subn(r'<div class="foot"><span>.*?</span><span>\d+</span></div>',
                     f'<div class="foot"><span>{foot}</span><span>{num:02d}</span></div>', out, flags=re.S)
    assert n == 1, foot
    return out


TT = "<br><br><b>Thao tác:</b> "      # notes panel renders the attribute as HTML

CH1, CH2, CH3, CH4 = "Chương 1 · Giới thiệu", "Chương 2 · Cơ sở lý thuyết", "Chương 3 · Dữ liệu", "Chương 4 · Phương pháp đề xuất"
CH5, CH6, CH78 = "Chương 5 · Hệ thống", "Chương 6 · Thực nghiệm", "Chương 7–8 · Tự đánh giá"

# ---------------------------------------------------------------- slide 1: merged cover
COVER_NOTES = notes_attr(
    "Kính chào quý thầy cô trong hội đồng. Nhóm em gồm Nguyễn Ngọc Lân và Nguyễn Tấn Minh, dưới sự hướng dẫn của "
    "ThS. Trương Vĩnh Linh. Đề tài của nhóm là nghiên cứu và xây dựng hệ thống phát hiện ảo giác cho mô hình ngôn ngữ "
    "lớn tăng cường truy xuất tiếng Việt, dựa trên tín hiệu chú ý nội tại. Ý tưởng gói trong một câu: khi mô hình đọc "
    "lại câu trả lời cùng tài liệu, cách nó phân bổ sự chú ý cho biết câu trả lời có bám tài liệu hay không — mà không "
    "cần gọi thêm một mô hình giám khảo nào.")
cover = f'''<section class="slide cv19" data-notes="{COVER_NOTES}">
  <div class="band"></div>
  {BEAMS}
  <img class="owl rise r2" src="{OWL}" alt="Cú Lens">
  <img class="logo rise r1" src="{LOGO}" alt="Trường Đại học Công nghiệp TP. Hồ Chí Minh">
  <div class="org rise r1">Trường Đại học Công nghiệp TP. Hồ Chí Minh<span>Khoa Công nghệ Thông tin · Ngành Khoa học dữ liệu</span></div>
  <div class="title"><div class="kicker rise r2">Báo cáo khóa luận tốt nghiệp</div>
    <h1 class="rise r2">Nghiên cứu và xây dựng hệ thống phát hiện ảo giác cho mô hình ngôn ngữ lớn tăng cường truy xuất tiếng Việt <em>dựa trên tín hiệu chú ý nội tại</em></h1></div>
  <div class="team">
    <div class="who rise r3"><div class="r">Sinh viên thực hiện</div><div class="n">Nguyễn Ngọc Lân</div><div class="id">MSSV 22635801</div></div>
    <div class="who rise r3"><div class="r">Sinh viên thực hiện</div><div class="n">Nguyễn Tấn Minh</div><div class="id">MSSV 22643511</div></div>
    <div class="who rise r4"><div class="r">Giảng viên hướng dẫn</div><div class="n">ThS. Trương Vĩnh Linh</div><div class="id">Khoa Công nghệ Thông tin</div></div>
  </div>
  <div class="place rise r5">TP. Hồ Chí Minh · 2026</div>
</section>'''

# ---------------------------------------------------------------- slide 4: gaps and questions
GAPS = [("var(--ctx)", "Khoảng trống 1",
         "Chưa ai tách tỷ lệ chú ý theo <em>từng đoạn</em> ngữ cảnh và kiểm chứng nó có trùng vị trí bằng chứng không.",
         "Lookback Lens gộp cả ngữ cảnh thành một khối, nên không biết mô hình nhìn đúng đoạn hay nhìn dàn trải."),
        ("var(--res)", "Khoảng trống 2",
         "Chưa ai đặt ba hướng tiếp cận lên <em>cùng một thang đo</em> gồm cả độ chính xác lẫn chi phí.",
         "Bộ mã hóa tinh chỉnh, LLM giám khảo và hướng nội tại thường được báo cáo trên dữ liệu và cách chia tập khác nhau."),
        ("#6B4FA0", "Khoảng trống 3",
         "Chưa có công trình nào dùng tín hiệu nội tại để phát hiện ảo giác <em>tiếng Việt</em>.",
         "Các hệ thống của cuộc thi ViHallu và SemViQA đều khai thác văn bản: bộ mã hóa, LLM với prompt, truy xuất bằng chứng.")]
QUES = [("var(--ctx)", "Câu hỏi 1 · Tín hiệu",
         "Chú ý theo đoạn có cải thiện việc phát hiện ảo giác so với tỷ lệ gộp — và mô hình có thật sự nhìn vào đúng chỗ?",
         "Trả lời ở slide 12–15"),
        ("var(--res)", "Câu hỏi 2 · Chi phí",
         "So với LLM giám khảo và bộ mã hóa tinh chỉnh, hướng này đứng ở đâu về độ chính xác lẫn chi phí?",
         "Trả lời ở slide 3 và 16"),
        ("#6B4FA0", "Câu hỏi 3 · Chuyển giao",
         "Tín hiệu chú ý thêm được bao nhiêu so với đặc trưng bề mặt, và có dùng được trên bộ dữ liệu khác không?",
         "Trả lời ở slide 15 và 17")]
gq_cells = []
for k, (col, kick, stmt, note) in enumerate(GAPS):
    gq_cells.append(f'<div class="gcard rise r{k + 1}" style="--c:{col}"><div class="k">{kick}</div>'
                    f'<div class="s">{stmt}</div><div class="n">{note}</div></div>')
for col, _, _, _ in GAPS:
    gq_cells.append(f'<div class="ar rise r4" style="--c:{col}">↓</div>')
for k, (col, kick, q, a) in enumerate(QUES):
    gq_cells.append(f'<div class="qcard rise r{k + 3}" style="--c:{col}"><div class="k">{kick}</div>'
                    f'<div class="q">{q}</div><div class="a">{a}</div></div>')
GAPS_NOTES = notes_attr(
    "Từ hiện trạng đó, nhóm em xác định ba khoảng trống. Thứ nhất, chưa ai tách tỷ lệ chú ý theo từng đoạn ngữ cảnh và "
    "kiểm tra xem nó có trùng vị trí bằng chứng không. Thứ hai, ba hướng tiếp cận chưa được đặt lên cùng một thang đo gồm "
    "cả độ chính xác lẫn chi phí. Thứ ba, chưa có công trình nào dùng tín hiệu nội tại để phát hiện ảo giác tiếng Việt. "
    "Ba khoảng trống này trở thành ba câu hỏi nghiên cứu cùng màu ở hàng dưới; mỗi thẻ ghi slide nào trả lời câu hỏi đó.")
GQ_HTML = "\n    ".join(gq_cells)
gaps = f'''<section class="slide" data-notes="{GAPS_NOTES}">
  {run_header(CH1)}
  <div class="head"><h2>Khoảng trống nghiên cứu và ba câu hỏi của đề tài</h2></div>
  <div class="gq">
    {GQ_HTML}
  </div>
  <div class="foot"><span>Mục 1.2–1.3 báo cáo · Lookback Lens: Chuang và cộng sự (EMNLP 2024) · ViHallu: Nguyen và cộng sự (2026) · SemViQA: Tran và cộng sự (2025) · năm giả thuyết ở Bảng 1.1</span><span>04</span></div>
</section>'''

# ---------------------------------------------------------------- slide 18: three columns
# The ViFactCheck items and the first "next step" follow E17 (ViFactCheck) and E18 (per-sentence
# scoring), both run on 23/10/2026: TASKS.md T41 and T45C.
DONE = ["Bộ phát hiện ba lớp cho tiếng Việt từ tín hiệu chú ý: <b>0,757</b>, ngang bộ mã hóa tinh chỉnh với <b>579</b> tham số; lặp lại trên bộ tin tức ViFactCheck: <b>0,703</b>.",
        "Kiểm chứng trực tiếp cơ chế: nhìn đúng đoạn bằng chứng <b>87,8 %</b>, lặp lại trên bộ thứ hai, can thiệp đúng 4/4 hướng.",
        "Đo chi phí đầy đủ: mô hình 3B là điểm cân bằng, chỉ <b>195</b> tham số phải huấn luyện.",
        "Hệ thống hoàn chỉnh: thư viện, REST, Docker, giao diện; chạy thật bắt được ảo giác."]
NOT_DONE = ["Năm đặc trưng hình dạng <b>không</b> làm tăng điểm phân loại so với tỷ lệ gộp, kể cả trên ViFactCheck.",
            "Bộ phát hiện ba lớp không dùng được chéo bộ; chỉ quyết định nhị phân chuyển được.",
            "Chi phí biên trong hệ RAG tự giám sát chưa đo: trên T4, mô hình sinh và mô hình đọc là hai mô hình.",
            "Docker chưa kiểm trên máy có GPU."]
NEXT = ["Chấm theo từng đoạn của câu trả lời, cần dữ liệu có nhãn mức đoạn; chấm theo từng câu đã thử (E18), không hơn.",
        "Kết hợp chú ý với bộ mã hóa: chú ý mạnh ở lớp nội tại, bộ mã hóa mạnh ở lớp ngoại lai.",
        "Đo chi phí biên khi một mô hình vừa sinh vừa đọc, trên phần cứng có bfloat16 gốc.",
        "Chỉ tính hàng chú ý của token phản hồi, để dùng ngữ cảnh dài hơn 4.096 token."]


def ul(items):
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


SELF_NOTES = notes_attr(
    "Tóm lại, nhóm em đã làm được bộ phát hiện ba lớp từ tín hiệu chú ý, ngang bộ mã hóa tinh chỉnh với vài trăm tham số, "
    "lặp lại trên bộ tin tức ViFactCheck; kiểm chứng trực tiếp được cơ chế; đo đủ chi phí; và đóng gói thành hệ thống chạy "
    "thật. Những điều chưa làm được: đặc trưng hình dạng không làm tăng điểm phân loại, kể cả trên ViFactCheck; bộ ba lớp "
    "không chuyển được sang bộ dữ liệu khác; và chi phí biên trong hệ tự giám sát chưa đo. Nhóm em đã thử chấm theo từng "
    "câu nhưng không hơn; hướng tiếp theo là chấm theo từng đoạn của câu trả lời, với dữ liệu có nhãn mức đoạn.")
selfeval = f'''<section class="slide" data-notes="{SELF_NOTES}">
  {run_header(CH78)}
  <div class="head"><h2>Tự đánh giá: đã làm được gì, chưa làm được gì, và hướng tiếp theo</h2></div>
  <div class="three">
    <div class="col yes rise r1"><h3 style="color:var(--ok)">Đã làm được</h3>{ul(DONE)}</div>
    <div class="col no rise r2"><h3 style="color:var(--bad)">Chưa làm được</h3>{ul(NOT_DONE)}</div>
    <div class="col nx rise r3"><h3 style="color:var(--ctx)">Hướng phát triển</h3>{ul(NEXT)}</div>
  </div>
  <div class="foot"><span>Chương 7 và mục 8.1–8.3 báo cáo</span><span>18</span></div>
</section>'''

# ---------------------------------------------------------------- slides copied from Lân's deck
NOTES = {
    "types": "Trước hết là bài toán. Hệ RAG tìm tài liệu rồi để mô hình ngôn ngữ trả lời dựa trên đó, nhưng câu trả lời vẫn "
             "có thể bịa. Theo cách gán nhãn của bộ ViHallu có hai kiểu bịa: nội tại là đọc tài liệu rồi nói sai, như đổi "
             "triều Lý thành triều Trần; ngoại lai là nói điều tài liệu không hề có, như tháp Eiffel ở hồ Tây. Hệ thống của "
             "nhóm chấm rủi ro ba câu này là 0,001, 0,998 và 1,000 — bài toán là tách được cả ba lớp, không chỉ đúng hay sai."
             + TT + "rê chuột lên phần tô màu để đối chiếu với tài liệu; bấm một thẻ để làm nổi đường nối.",
    "costs": "Hiện có ba cách phổ biến để bắt ảo giác, và cách nào cũng phải trả một cái giá. Hỏi một LLM khác làm giám "
             "khảo như Gemini thì mỗi câu mất khoảng 8,2 giây, tính cả thời gian giãn nhịp theo hạn mức của bản miễn phí; dữ "
             "liệu phải gửi ra ngoài, và macro-F1 chỉ 0,664. Tinh chỉnh "
             "bộ mã hóa như XLM-R thì chính xác nhất, 0,776, nhưng phải huấn luyện 560 triệu tham số trên GPU. Đặc trưng bề "
             "mặt chỉ có 9 tham số nhưng chỉ đạt 0,656. Vì vậy đề tài đi tìm một tín hiệu có sẵn ngay trong lượt đọc của mô hình.",
    "lb": "Phương pháp nền là Lookback Lens, công bố ở EMNLP 2024. Với mỗi token của câu trả lời, ta xem chú ý của nó dành "
          "cho ngữ cảnh bao nhiêu và cho phần câu trả lời đã viết bao nhiêu; phần dành cho ngữ cảnh gọi là tỷ lệ nhìn lại. "
          "Lấy trung bình trên mọi token, riêng cho từng đầu chú ý, ta được 27 lớp nhân 28 đầu bằng 756 con số — lớp cuối "
          "của Qwen2.5-7B bị bỏ vì tràn số. Một bộ phân loại tuyến tính đọc 756 con số đó; nhóm em tái lập phương pháp "
          "này trên tiếng Việt với bài toán ba lớp.",
    "data": "Nhóm dùng ba bộ dữ liệu tiếng Việt công khai. ViHallu 7.000 mẫu là bộ chính, câu trả lời do GPT-4o viết; "
            "ISE-DSC01 có ngữ cảnh dài, trung vị 19 câu, và đánh dấu sẵn câu bằng chứng; ViWikiFC dùng để đối chứng. Điểm "
            "quan trọng là cách chia tập: chia ngẫu nhiên từng dòng thì các câu trả lời của cùng một tài liệu rơi vào cả "
            "tập huấn luyện lẫn tập kiểm tra, nên nhóm chia theo ngữ cảnh, tỷ lệ 80/10/10, hạt giống 42, rò rỉ bằng 0. "
            "Nhóm cũng đo được tập kiểm tra gốc của ViWikiFC dùng lại 100 % ngữ cảnh huấn luyện."
            + TT + "bấm hai nút ở góc phải để so hai cách chia.",
    "chunk": "Đây là đóng góp chính của đề tài. Hai câu trả lời có thể cùng dành 62 % chú ý cho ngữ cảnh, nhưng một câu dồn "
             "vào đúng câu chứa thông tin, câu kia rải đều. Lookback Lens gộp thành một con số nên không phân biệt được hai "
             "trường hợp này. Chunk-aware cộng chú ý theo từng đoạn ngữ cảnh rồi đo hình dạng phân bố bằng năm đặc trưng, "
             "trong đó có entropy và tỷ trọng lớn nhất. Số liệu trên hình là minh họa nguyên lý, giống Hình 2.1 của báo cáo.",
    "pipe": "Toàn bộ quy trình chỉ cần một lượt đọc, mô hình không phải sinh thêm chữ nào. Bước một, ghép câu hỏi, tài liệu "
            "và câu trả lời vào một mẫu prompt cố định và ghi lại vị trí hai vùng. Bước hai, Qwen2.5-7B đọc một lượt; ở 27 "
            "lớp, hook lấy chú ý theo đoạn rồi bỏ ma trận, lớp cuối tràn số ở float16 nên bị bỏ. Bước ba, giữ 32 đầu xếp "
            "hạng cao nhất, mỗi đầu 6 con số, tổng 192. Bước bốn, hồi quy logistic 579 tham số đổi 192 con số thành ba xác "
            "suất — câu về Hồ Hoàn Kiếm có cụm tự bịa được chấm rủi ro 0,997.",
    "hook": "Rủi ro kỹ thuật lớn nhất của đề tài là bộ nhớ. Muốn đọc trọng số chú ý phải tắt cài đặt tối ưu như "
            "FlashAttention, và với 4.096 token, ma trận chú ý của một lớp đã chiếm khoảng 0,94 GB. Giữ ma trận của cả 28 "
            "lớp cần khoảng 26 GB, nên card T4 16 GB tràn ngay từ lớp thứ 12. Nhóm dùng forward hook: lớp nào tính xong thì "
            "hook cộng chú ý theo đoạn rồi xóa ma trận, nhờ vậy bộ nhớ đỉnh đo thực tế ở ngưỡng 4.096 token chỉ 8.428 MB."
            + TT + "rê chuột lên từng lớp để xem bộ nhớ ở lớp đó.",
    "sys": "Phần hệ thống gồm bốn tầng, tầng trên chỉ gọi tầng ngay dưới: trích chú ý, tính đặc trưng, bộ phát hiện và phục "
           "vụ. Có ba cách dùng: gọi thư viện Python, gọi dịch vụ REST, hoặc chạy cả gói bằng Docker, kèm giao diện web. Bộ "
           "phát hiện chỉ là một tệp 11,5 KB; nạp lại và chấm 700 mẫu kiểm tra cho kết quả trùng 700/700 với lúc thí "
           "nghiệm. Bộ kiểm thử có 825 ca tự động."
           + TT + "rê chuột lên từng tầng để xem mô-đun tương ứng.",
    "demo": "Đây là một lượt chạy thật trên Kaggle T4 ngày 11/09/2026. Hệ thống tìm ba tài liệu trong kho 21 bài; "
            "Qwen2.5-3B sinh câu trả lời, còn Qwen2.5-7B chỉ đọc lại để chấm, vì trên T4 hai vai trò này phải tách thành hai "
            "mô hình. Câu trả lời đúng ở ý đầu nhưng tự thêm cụm “sau đó anh ta đã trở về dinh thự”. Không ai viết sẵn câu "
            "trả lời này: mô hình tự bịa, bộ phát hiện tự chấm ngoại lai với rủi ro 0,997."
            + TT + "bấm tên câu hỏi ở góc phải để xem ba ví dụ còn lại.",
    "res": "Đây là kết quả chính trên 700 mẫu kiểm tra của ViHallu. Hai mốc đầu, đặc trưng bề mặt và Gemini, quanh 0,66; "
           "lưu ý Gemini chỉ chấm trên 300 mẫu. Hai bộ mã hóa tinh chỉnh đạt 0,749 và 0,776. Hướng chú ý đạt 0,745 với "
           "lookback gộp và 0,757 với chunk-aware; khoảng tin cậy chồng với XLM-R nên nhóm kết luận là ngang, không nói là "
           "hơn. Khác biệt nằm ở số tham số phải huấn luyện: 579 so với 369 triệu của PhoBERT. Con số này không đặt cạnh "
           "84,80 % của đội dẫn đầu cuộc thi ViHallu: khác tập đánh giá, và các đội đầu tinh chỉnh LLM, còn nhóm em không "
           "tinh chỉnh mô hình nào."
           + TT + "rê chuột lên từng dòng để xem khoảng tin cậy và số tham số.",
    "loc": "Đây là phép kiểm chứng cơ chế trực tiếp, không đi qua bộ phân loại. Trên 2.376 mẫu ISE-DSC01 có bằng chứng định "
           "vị được, nhóm xem đầu chú ý mạnh nhất nhìn đoạn nào nhiều nhất. Nó trúng đúng đoạn chứa bằng chứng ở 87,8 % số "
           "mẫu, gấp 14,3 lần chọn bừa. Lặp lại trên ViWikiFC, trung bình mọi đầu là 32,9 % so với 33,2 %, chỉ lệch 0,003."
           + TT + "bấm “Mẫu khác” để xem thêm ví dụ minh họa.",
    "iv": "Các kết quả trước là tương quan, nên nhóm làm thêm một thí nghiệm can thiệp. Cùng một phát biểu được đọc trên hai "
          "ngữ cảnh mười câu, chỉ khác đúng câu bằng chứng. Trên 1.836 cặp ViWikiFC, cả bốn đặc trưng hình dạng đổi đúng "
          "hướng ở 71 đến 75 % số cặp. Hướng thay đổi được ghi trong mã trước khi chạy, nên đây không phải giải thích sau "
          "khi đã thấy số; tuy vậy mức thay đổi trung vị nhỏ, chỉ 0,013 đến 0,016."
          + TT + "ba nút ở góc phải bật riêng ngữ cảnh A, B hoặc cả hai.",
    "null": "Đây là kết quả bất lợi, và nhóm báo cáo thẳng. Chunk-aware hơn lookback gộp 0,0116 trên ViHallu, nhưng điểm tự "
            "dao động khoảng ±0,03 khi đổi tập kiểm tra. Đo lại năm lần nữa — thêm đặc trưng bề mặt, đổi sang Sailor2-8B, "
            "thu xuống 3B và 1.5B, đổi sang ViWikiFC — tất cả nằm trong vùng nhiễu và dấu còn đổi chiều. Lý do là hình dạng "
            "mang cùng tín hiệu với tỷ lệ gộp: trên ISE-DSC01, 99,9 % phần đóng góp của nó đã có sẵn trong tỷ lệ gộp; còn "
            "chính tỷ lệ gộp thì cộng thêm 0,109 vào đặc trưng bề mặt."
            + TT + "rê chuột lên từng điểm.",
    "cost": "Về chi phí, nhóm đặt mọi phương pháp lên cùng một mặt phẳng. XLM-R tốt hơn trên cả độ chính xác lẫn tốc độ: "
            "25,2 ms mỗi mẫu so với 437,6 ms của mô hình đọc 7B. Hướng chú ý nổi trội ở số tham số phải huấn luyện, từ 195 "
            "đến 2.271. Thu mô hình đọc xuống 3B thì nhanh gần gấp đôi, bộ nhớ chỉ 3.710 MB, mất khoảng 0,01 điểm; còn "
            "1.5B lại chậm hơn cả 7B vì phải chạy bfloat16 mà T4 không hỗ trợ sẵn."
            + TT + "rê chuột lên từng chấm để xem đủ số.",
    "xfer": "Câu hỏi cuối là chuyển giao. Huấn luyện trên ViHallu rồi chấm ISE-DSC01, điểm ba lớp rơi về 0,358, gần mức đoán "
            "bừa: trong 1.286 câu ngoại lai chỉ 66 câu được đoán đúng, 988 câu bị gọi thành nội tại. Chiều ngược lại mất lớp "
            "nội tại. Nhưng câu hỏi nhị phân “có ảo giác hay không” vẫn chuyển được, 0,664 và 0,776. Nguyên nhân khả dĩ là "
            "hai bộ định nghĩa nhãn khác nhau: ngoại lai của ViHallu là nội dung GPT-4o tự thêm vào, còn của ISE-DSC01 là "
            "phát biểu NEI do người viết."
            + TT + "bấm hai nút ở góc phải để đổi chiều.",
}

COPY = [  # (fig, slide number, chapter, footer, new title or None)
    ("types", 2, CH1, "Phân loại: Ji và cộng sự (ACM CSUR 2023); Maynez và cộng sự (ACL 2020) · nhãn theo ViHallu (Nguyen và cộng sự, 2026) · mục 2.3", None),
    ("costs", 3, CH1, "LLM giám khảo: Zheng và cộng sự (NeurIPS 2023) · PhoBERT: Nguyen và Nguyen (Findings EMNLP 2020) · XLM-R: Conneau và cộng sự (ACL 2020) · Bảng 6.1, 6.14",
     "Động lực: các cách bắt ảo giác hiện nay đều phải trả một cái giá lớn"),
    ("lb", 5, CH2, "Phương pháp nền: Chuang và cộng sự, “Lookback Lens”, EMNLP 2024 · minh họa nguyên lý · mục 2.5 và 4.3", None),
    ("data", 6, CH3, "ViHallu: Nguyen và cộng sự (2026) · ISE-DSC01: UIT DSC 2023 · ViWikiFC: Le và cộng sự (2024) · Bảng 3.1, 3.2, 3.4, 3.5", None),
    ("chunk", 7, CH4, "Mở rộng từ Lookback Lens (Chuang và cộng sự, EMNLP 2024) · minh họa nguyên lý, số liệu như Hình 2.1 · mục 4.4–4.5",
     "Phương pháp đề xuất: không chỉ hỏi mô hình nhìn tài liệu bao nhiêu, mà hỏi nhìn vào đoạn nào"),
    ("pipe", 8, CH4, "Mô hình đọc: Qwen2.5 (Qwen Team, 2024) · ví dụ thật: câu hỏi Hồ Hoàn Kiếm · mục 4.1, 4.2, 4.7", None),
    ("hook", 9, CH4, "Vì sao không dùng được FlashAttention: Dao và cộng sự (NeurIPS 2022) · Bảng 2.2 và mục 4.8 · đỉnh 8.428 MB đo trên Tesla T4 ở ngưỡng 4.096 token", None),
    ("sys", 10, CH5, "Chương 5 báo cáo", None),
    ("demo", 11, CH5, "Dữ liệu thật, Kaggle T4, 11/09/2026 · truy xuất BM25: Robertson và Zaragoza (2009) · mục 5.6", None),
    ("res", 12, CH6, "Bảng 6.1 · tập kiểm tra ViHallu 700 mẫu · PhoBERT: Nguyen và Nguyen (2020) · XLM-R: Conneau và cộng sự (2020) · LLM giám khảo: Zheng và cộng sự (2023)", None),
    ("loc", 13, CH6, "Bảng 6.3 và 6.7 · 2.376 mẫu ISE-DSC01 · tranh luận “chú ý có phải lời giải thích”: Jain và Wallace (2019); Wiegreffe và Pinter (2019)", None),
    ("iv", 14, CH6, "Bảng 6.6 · 1.836 cặp ViWikiFC (Le và cộng sự, 2024) · hướng dự đoán ghi trong mã trước khi chạy", None),
    ("null", 15, CH6, "Bảng 6.2, 6.8, 6.9, 6.10, 6.12 · Sailor2: Dou và cộng sự (2025)", None),
    ("cost", 16, CH6, "Bảng 6.10 và 6.14 · thời gian đo xen kẽ trên Tesla T4", None),
    ("xfer", 17, CH6, "Bảng 6.13 · nhãn SUPPORTED/REFUTED/NEI theo FEVER (Thorne và cộng sự, 2018)", None),
]
copied = {fig: restyle(by_fig(fig), ch, NOTES[fig], foot, num, h2) for fig, num, ch, foot, h2 in COPY}
# res: macro-F1 is the unweighted mean of the per-class F1 (report 3.5.1); the book uses "độ chính xác" for precision
copied["res"] = sub(copied["res"], "trung bình độ chính xác của ba lớp;", "trung bình cộng điểm F1 của ba lớp;")

thanks = sections[31]
assert 'class="slide thanks"' in thanks
thanks = re.sub(r'data-notes="[^"]*"', 'data-notes="' + notes_attr(
    "Nhóm em xin cảm ơn quý thầy cô đã lắng nghe, và rất mong nhận được câu hỏi cùng góp ý của hội đồng.") + '"', thanks, count=1)

ORDER = [cover, copied["types"], copied["costs"], gaps, copied["lb"], copied["data"], copied["chunk"], copied["pipe"],
         copied["hook"], copied["sys"], copied["demo"], copied["res"], copied["loc"], copied["iv"], copied["null"],
         copied["cost"], copied["xfer"], selfeval, thanks]
assert len(ORDER) == 19

# ---------------------------------------------------------------- figure code: drop unused, apply fixes
UNUSED = ["rag", "attn", "cut", "why", "err", "next", "ece", "leak", "fp16"]
lines = figs_js.split("\n")
starts = [i for i, ln in enumerate(lines) if ln.startswith("/* ----------") or ln.startswith("/* =====")]
drop = set()
for name in UNUSED:
    at = [i for i, ln in enumerate(lines) if ln.startswith(f"FIGS.{name} = (svg, api) => {{")]
    assert len(at) == 1, name
    head_i = at[0] - 1
    assert lines[head_i].startswith("/* ----------"), name
    nxt = min(i for i in starts if i > head_i)
    drop.update(range(head_i, nxt))
f = "\n".join(ln for i, ln in enumerate(lines) if i not in drop)
for name in UNUSED:
    assert f"FIGS.{name} =" not in f, name

# types: hover hint moves to the notes
f = sub(f, " Bài toán là tách được cả ba loại, không chỉ đúng hay sai. Rê chuột lên phần tô màu để đối chiếu.",
        " Bài toán là tách được cả ba loại, không chỉ đúng hay sai.")

# lb: the 756 ratios are the thesis' grid; the "on par with hidden states" claim is the original paper's
f = sub(f, "  tx(clf, GX, 470, 'Đây là Lookback Lens (EMNLP 2024): một bộ phân loại tuyến tính', { 'font-size': 21, fill: C.muted });\n"
           "  tx(clf, GX, 498, 'trên 756 tỷ lệ — ngang các bộ dò dùng toàn bộ trạng thái ẩn.', { 'font-size': 21, fill: C.muted });",
        "  tx(clf, GX, 470, 'Lookback Lens (EMNLP 2024): hồi quy logistic trên', { 'font-size': 21, fill: C.muted });\n"
        "  tx(clf, GX, 498, 'các tỷ lệ này — theo bài gốc, ngang bộ phân loại', { 'font-size': 21, fill: C.muted });\n"
        "  tx(clf, GX, 526, 'dùng toàn bộ trạng thái ẩn.', { 'font-size': 21, fill: C.muted });")

# data: Bảng 3.2 medians (5 / 19 / 4 câu); 22,6 and 9,8 belonged to E06 and E08's built contexts
f = sub(f, "k: 5, lab: '5,3 câu', role:", "k: 5, lab: '5 câu', role:")
f = sub(f, "k: 23, lab: '22,6 câu', role: 'ngữ cảnh dài 22,6 câu · có đánh dấu câu bằng chứng'",
        "k: 19, lab: '19 câu', role: 'ngữ cảnh dài · có đánh dấu câu bằng chứng'")
f = sub(f, "k: 10, lab: '9,8 câu', role:", "k: 4, lab: '4 câu', role:")
f = sub(f, "'ngữ cảnh trung bình ' + d.lab", "'trung vị ' + d.lab + ' mỗi ngữ cảnh'")
f = sub(f, "tập kiểm tra gốc của ViWikiFC dùng lại <b>100 %</b> ngữ cảnh của tập huấn luyện.`",
        "tập kiểm tra gốc của ViWikiFC dùng lại <b>100&nbsp;%</b> ngữ cảnh của tập huấn luyện.`")
f = sub(f, "tỷ lệ 80/10/10, seed 42. Rò rỉ bằng 0.", "tỷ lệ 80/10/10, hạt giống 42. Rò rỉ bằng 0.")
f = sub(f, "ngữ cảnh huấn luyện — nên điểm công bố trên bộ này có phần ảo. Bấm nút để so hai cách chia.",
        "ngữ cảnh huấn luyện — nên điểm trên tập đó chỉ đo việc phân loại trên ngữ cảnh đã thấy.")

# data: the highlighted button follows the split being animated (Lân's deck lit "theo ngữ cảnh" during the random step)
f = sub(f, "  buttons(api, [['Chia ngẫu nhiên', () => place(null, RANDOM, true, true)], ['Chia theo ngữ cảnh', () => place(null, BYCTX, false, true)]], 1);",
        "  const splitBtns = buttons(api, [['Chia ngẫu nhiên', () => place(null, RANDOM, true, true)], ['Chia theo ngữ cảnh', () => place(null, BYCTX, false, true)]], -1);\n"
        "  const lit = k => tl => tl.call(() => splitBtns.forEach((b, j) => b.classList.toggle('on', j === k)));")
f = sub(f, "tl.to(binG, { opacity: 1, duration: .3 }); place(tl, RANDOM, true, false); } },",
        "tl.to(binG, { opacity: 1, duration: .3 }); lit(0)(tl); place(tl, RANDOM, true, false); } },")
f = sub(f, "play: tl => { tl.call(() => { links.innerHTML = ''; }); place(tl, BYCTX, false, false); } },",
        "play: tl => { tl.call(() => { links.innerHTML = ''; }); lit(1)(tl); place(tl, BYCTX, false, false); } },")

# pipe: hooks sit on 27 layers (layer 27 overflows in float16 and is excluded); no bare task codes
f = sub(f, "hov(P, 'Mẫu prompt chốt ở T07, không đổi suốt đề tài.",
        "hov(P, 'Mẫu prompt chốt một lần, không đổi suốt đề tài.")
f = sub(f, "    hov(r, `Lớp ${i}: hook đọc ma trận chú ý, cộng theo câu ngữ cảnh rồi xóa ma trận`); lay.push({ r, tap }); }",
        "    hov(r, i === 27 ? 'Lớp 27: tràn số ở float16 nên không gắn hook, bỏ khỏi đặc trưng'\n"
        "                    : `Lớp ${i}: hook đọc ma trận chú ý, cộng theo câu ngữ cảnh rồi xóa ma trận`); lay.push({ r, tap }); }")
f = sub(f, "  tx(L, X2 + 262, 548, 'hook', { 'font-size': 18, fill: C.res, 'font-weight': 600 });",
        "  tx(L, X2 + 262, 548, 'hook', { 'font-size': 18, fill: C.res, 'font-weight': 600 });\n"
        "  tx(L, X2 + 248, 107, 'lớp 27: bỏ', { 'font-size': 16, fill: C.bad, 'font-weight': 600 });")
f = sub(f, "tl.to(tap, { opacity: 1, duration: .05 }, '<'); tl.to(r, { attr: { fill: '#9FCFCB' }, duration: .1 }, '<.06'); }); } },",
        "tl.to(tap, { opacity: i === 27 ? 0 : 1, duration: .05 }, '<'); tl.to(r, { attr: { fill: i === 27 ? C.badSoft : '#9FCFCB' }, duration: .1 }, '<.06'); }); } },")
f = sub(f, "Mô hình đọc toàn bộ một lần qua <b>28 lớp</b>. Ở mỗi lớp, <b>hook</b> lấy chú ý của vùng phản hồi lên từng câu ngữ cảnh, rồi bỏ ma trận đi.",
        "Mô hình đọc toàn bộ một lần qua <b>28 lớp</b>. Ở 27 lớp, <b>hook</b> lấy chú ý của vùng phản hồi lên từng câu ngữ cảnh rồi bỏ ma trận; lớp cuối tràn số ở float16 nên bị bỏ.")
f = sub(f, "Giữ lại <b>32 đầu chú ý</b> mang tín hiệu mạnh nhất, mỗi đầu cho 6 con số",
        "Giữ lại <b>32 đầu chú ý</b> xếp hạng cao nhất (tập dev chọn số đầu), mỗi đầu cho 6 con số")

# hook: 16,8 GB was a running sum at the moment of overflow, not a requirement; Bảng 2.2 gives 26 GB for 28 layers
f = sub(f, "  el('rect', { x: 220, y: 190, width: 360, height: 92, rx: 12, fill: C.bad }, oom);\n"
           "  tx(oom, 400, 232, 'TRÀN BỘ NHỚ', { 'text-anchor': 'middle', 'font-size': 32, 'font-weight': 700, fill: '#fff' });\n"
           "  tx(oom, 400, 266, 'ở lớp 12: 5,5 + 12 × 0,94 > 16', { 'text-anchor': 'middle', 'font-size': 21, fill: '#fff' });",
        "  el('rect', { x: 220, y: 168, width: 360, height: 124, rx: 12, fill: C.bad }, oom);\n"
        "  tx(oom, 400, 210, 'TRÀN BỘ NHỚ', { 'text-anchor': 'middle', 'font-size': 32, 'font-weight': 700, fill: '#fff' });\n"
        "  tx(oom, 400, 244, 'ở lớp 12: 5,5 + 12 × 0,94 > 16', { 'text-anchor': 'middle', 'font-size': 21, fill: '#fff' });\n"
        "  tx(oom, 400, 274, 'giữ đủ 28 lớp cần 26 GB', { 'text-anchor': 'middle', 'font-size': 21, fill: '#fff' });")
f = sub(f, "tl.to(A.layers.slice(12), { attr: { fill: '#F0D9D4' }, duration: .25 }, '<'); tl.to(oom, { opacity: 1, duration: .3 }); } },",
        "tl.to(A.layers.slice(12), { attr: { fill: '#F0D9D4' }, duration: .25 }, '<'); tl.to(oom, { opacity: 1, duration: .3 });\n"
        "        tl.call(() => { A.val.textContent = '> 16 GB'; }); } },")
f = sub(f, "Mới tới <b>lớp 12</b>, tổng bộ nhớ đã vượt 16 GB của card T4.",
        "Mới tới <b>lớp 12</b>, tổng bộ nhớ đã vượt 16 GB của card T4; giữ đủ 28 lớp cần khoảng <b>26 GB</b> chỉ riêng cho ma trận.")
f = sub(f, " — mô hình 7B chạy trọn trong một card 16 GB miễn phí của Kaggle. Rê chuột lên từng lớp để xem điều gì xảy ra ở đó.",
        " — mô hình 7B chạy trọn trong một card 16 GB miễn phí của Kaggle.")

# res: Gemini scored 300/700 (v4 Hình 6.1 note); ECE claim dropped (report 7.3 ties it to parameter count)
f = sub(f, "['Gemini giám khảo', .664, .607, .719, 0, '0 · gọi API', 'base', 'Gọi Gemini chấm từng mẫu — 8,2 giây/mẫu, không huấn luyện'],",
        "['Gemini giám khảo †', .664, .607, .719, 0, '0 · gọi API', 'base', 'Gọi Gemini chấm từng mẫu — 8,2 giây/mẫu, không huấn luyện · chấm trên 300/700 mẫu test'],")
f = sub(f, "'Đề tài · ECE 0,044 — hiệu chỉnh tốt nhất bảng'", "'Đề tài · 32 đầu × 6 đặc trưng'")
f = sub(f, "  tx(ax, (X0 + X1) / 2, 26, 'macro-F1 trên 700 mẫu kiểm tra · chấm và vạch là khoảng tin cậy 95 %', { 'text-anchor': 'middle', 'font-size': 20, fill: C.muted });",
        "  tx(ax, (X0 + X1) / 2, 26, 'macro-F1 trên 700 mẫu kiểm tra · chấm và vạch là khoảng tin cậy 95 %', { 'text-anchor': 'middle', 'font-size': 20, fill: C.muted });\n"
        "  tx(ax, 0, 556, '† Gemini chấm trên 300/700 mẫu test · các số trong hình không đặt cạnh 84,80 % của cuộc thi ViHallu: khác tập đánh giá, khác chế độ (mục 7.1)', { 'font-size': 18, fill: C.muted });")
f = sub(f, "{ cap: 'Hai mốc rẻ: <b>đặc trưng bề mặt</b>", "{ cap: 'Hai mốc đầu: <b>đặc trưng bề mặt</b>")
f = sub(f, "Khác biệt nằm ở cột phải: hướng chú ý chỉ huấn luyện <b>579 tham số</b>, ít hơn PhoBERT khoảng <b>637.000 lần</b>, và có xác suất hiệu chỉnh tốt nhất bảng (ECE 0,044). Rê chuột lên từng dòng.",
        "Khác biệt nằm ở cột phải: hướng chú ý chỉ huấn luyện <b>579 tham số</b>, ít hơn PhoBERT khoảng <b>638.000 lần</b>, và không phải tinh chỉnh mô hình nào.")

# loc
f = sub(f, " Khả năng nhìn đúng chỗ thuộc về mô hình, không phụ thuộc bộ dữ liệu. Bấm “Mẫu khác” để xem thêm.",
        " Khả năng nhìn đúng chỗ thuộc về mô hình, không phụ thuộc bộ dữ liệu.")

# null: E13 is −0,0258 (difference of raw values, Bảng 6.10); E12 adds 2 surface features
f = sub(f, "['E12 · thêm đặc trưng bề mặt', -.0071, 'cùng bộ, thêm 9 đặc trưng bề mặt']",
        "['E12 · thêm đặc trưng bề mặt', -.0071, 'cùng bộ, cả hai bên có thêm 2 đặc trưng bề mặt, cố định 32 đầu']")
f = sub(f, "['E13 · đổi sang Sailor2-8B', -.0257, 'đổi họ mô hình đọc']", "['E13 · đổi sang Sailor2-8B', -.0258, 'đổi họ mô hình đọc']")
f = sub(f, "Lý do: năm đặc trưng hình dạng <b>có</b> mang tín hiệu, nhưng đó là cùng tín hiệu mà tỷ lệ gộp đã mang.",
        "Lý do: năm đặc trưng hình dạng <b>có</b> mang tín hiệu, nhưng đó là cùng tín hiệu mà tỷ lệ gộp đã mang — chính tỷ lệ gộp cộng thêm <b>+0,109</b> vào đặc trưng bề mặt.")

# cost
f = sub(f, "Hướng chú ý với Qwen2.5-7B: <b>437 ms/mẫu</b>, độ chính xác ngang PhoBERT — chậm hơn, nhưng chỉ huấn luyện vài trăm tham số (chấm nhỏ).",
        "Hướng chú ý với Qwen2.5-7B: <b>437,6 ms/mẫu</b>, độ chính xác ngang PhoBERT — chậm hơn, nhưng chỉ huấn luyện <b>579–2.271 tham số</b> (chấm nhỏ).")
f = sub(f, "Về bộ nhớ, 3B chỉ cần <b>3,7 GB</b> — chạy được trên GPU phổ thông. Rê chuột lên từng chấm để xem đủ số.",
        "Về bộ nhớ, 3B chỉ cần <b>3,7 GB</b> — chạy được trên GPU phổ thông.")

# xfer: the deck used the predicted count (82 / 72) as the true-positive count; rows from F1 + counts in runs.jsonl
f = sub(f, "flows: [['trung thực', 216], ['nội tại', 988], ['ngoại lai', 82]], f1: [.358, .664] },",
        "flows: [['trung thực', 232], ['nội tại', 988], ['ngoại lai', 66]], f1: [.358, .664] },")
f = sub(f, "flows: [['trung thực', 26], ['nội tại', 72], ['ngoại lai', 136]], f1: [.552, .776] }];",
        "flows: [['trung thực', 44], ['nội tại', 54], ['ngoại lai', 136]], f1: [.552, .776] }];")
f = sub(f, "html(why, X + 20, 302, 520, 250, `<b style=\"font-size:23px\">Cùng tên lớp, khác cơ chế</b><br>\n"
           "    <span style=\"color:${C.bad}\">●</span> “Ngoại lai” của ViHallu: GPT-4o <b>bịa thêm</b> — mô hình đọc không nhìn ngữ cảnh.<br>\n"
           "    <span style=\"color:${C.bad}\">●</span> “Ngoại lai” của ISE-DSC01: câu <b>người viết</b> mà ngữ cảnh không xác nhận — mô hình vẫn nhìn, chỉ không tìm thấy.<br>\n"
           "    <span style=\"color:${C.ok}\">●</span> Câu hỏi “có bám tài liệu không” thuộc về mô hình đọc nên <b>chuyển được</b>.`, 'font-size:19px;line-height:1.4');",
        "html(why, X + 20, 302, 520, 250, `<b style=\"font-size:23px\">Cùng tên lớp, khác định nghĩa</b><br>\n"
        "    <span style=\"color:${C.bad}\">●</span> “Ngoại lai” của ViHallu: nội dung GPT-4o <b>tự thêm vào</b> câu trả lời.<br>\n"
        "    <span style=\"color:${C.bad}\">●</span> “Ngoại lai” của ISE-DSC01: phát biểu NEI <b>do người viết</b>, ngữ cảnh không đủ để xác nhận.<br>\n"
        "    <span style=\"color:${C.ok}\">●</span> Điều <b>chuyển được</b> là “có bám ngữ cảnh hay không”; điều không chuyển được là “ảo giác loại nào”.`, 'font-size:19px;line-height:1.4');")
# the lit direction button follows the animation, and a replay (R) rebuilds the first direction
f = sub(f, "    bars.forEach(b => gsap.set(b.b, { attr: { width: 0 } })); setF(d, true); }]), 1);",
        "    bars.forEach(b => gsap.set(b.b, { attr: { width: 0 } })); setF(d, true); }]), 0);\n"
        "  const dirLit = k => () => xferBtns.forEach((b, j) => b.classList.toggle('on', j === k));")
f = sub(f, "  buttons(api, DIR.map((d, i) => [i ? 'ISE → ViHallu' : 'ViHallu → ISE',",
        "  const xferBtns = buttons(api, DIR.map((d, i) => [i ? 'ISE → ViHallu' : 'ViHallu → ISE',")
f = sub(f, "play: tl => { build(DIR[0]); tl.to(clipR, { attr: { width: 1100 }, duration: 1, ease: 'power1.inOut' }); } },",
        "play: tl => { build(DIR[0]); tl.call(() => { build(DIR[0]); dirLit(0)(); }); tl.to(clipR, { attr: { width: 1100 }, duration: 1, ease: 'power1.inOut' }); } },")
f = sub(f, "tl.call(() => build(DIR[1]));", "tl.call(() => { build(DIR[1]); dirLit(1)(); });")
f = sub(f, "trong 1.286 câu thật sự <b>ngoại lai</b>, mô hình gọi đúng chỉ 82 — <b>988 câu</b> bị gọi thành nội tại.",
        "trong 1.286 câu thật sự <b>ngoại lai</b>, chỉ <b>66</b> câu được đoán đúng; <b>988 câu</b> bị gọi thành nội tại.")
f = sub(f, "Chiều ngược lại mất lớp còn lại: câu <b>nội tại</b> của ViHallu bị gọi thành ngoại lai.",
        "Chiều ngược lại mất lớp còn lại: trong 234 câu <b>nội tại</b> của ViHallu, 136 câu bị gọi thành ngoại lai.")
f = sub(f, "Lý do nằm ở <b>định nghĩa nhãn</b>, không ở đặc trưng. Bấm nút để xem lại từng chiều.",
        "Nguyên nhân khả dĩ nằm ở <b>định nghĩa nhãn</b> của hai bộ: cùng tên lớp nhưng tạo ra theo hai cách khác nhau.")

# sys: 825 tests pass in the pytest run of 23/10/2026 (the v4 report, Phụ lục A, still says 688); hint to notes
f = sub(f, "['783', 'ca kiểm thử tự động']", "['825', 'ca kiểm thử tự động đạt']")
f = sub(f, "'Giao diện web: dán ngữ cảnh và câu trả lời, xem rủi ro và chú ý theo đoạn'",
        "'Giao diện web: dán ngữ cảnh và câu trả lời, xem rủi ro, chú ý theo đoạn'")
f = sub(f, "trùng <b>700/700</b> với lúc thí nghiệm. Rê chuột lên từng tầng.", "trùng <b>700/700</b> với lúc thí nghiệm.")

# demo: the generator is Qwen2.5-3B; Qwen2.5-7B only reads (replay.json: generator / reading_model)
f = sub(f, "tx(ans, 18, 162, 'Mô hình sinh câu trả lời'", "tx(ans, 18, 162, 'Qwen2.5-3B sinh câu trả lời'")
f = sub(f, "Câu hỏi thật: hệ thống tìm ba tài liệu (12 câu) trong kho 21 bài và đưa cho Qwen2.5-7B.",
        "Câu hỏi thật: hệ thống tìm ba tài liệu (12 câu) trong kho 21 bài; <b>Qwen2.5-3B</b> sinh câu trả lời, Qwen2.5-7B chỉ đọc lại để chấm.")
f = sub(f, "mô hình tự bịa, hệ thống tự bắt. Bấm câu hỏi khác để xem.", "mô hình tự bịa, hệ thống tự bắt.")

# ---- second review (14/10) ----
# hook: the lanes are drawn at 4.096 token, where report 4.8 measured 8.428 MB; 8.328 MB is the ViHallu
# extraction (short inputs, Bảng 6.14). The mid-animation 7,5 GB had no source: weights 5,5 + one 0,94 GB matrix.
f = sub(f, "py = gY + gH - 8.3 / GB * gH;", "py = gY + gH - 8.4 / GB * gH;")
f = sub(f, "tx(peak, B.gx + 84, py + 7, '8,3 GB',", "tx(peak, B.gx + 84, py + 7, '8,4 GB',")
f = sub(f, "B.val.textContent = '7,5 GB'", "B.val.textContent = '≈ 6,5 GB'")
f = sub(f, "Bộ nhớ đỉnh đo thực tế trên Tesla T4 là <b>8,3 GB</b> — ",
        "Bộ nhớ đỉnh đo thực tế trên Tesla T4 ở ngưỡng 4.096 token là <b>8,4 GB</b> — ")
f = sub(f, "setG(8.3), { duration: .45 })); tl.call(() => { B.val.textContent = '8,3 GB'; });",
        "setG(8.4), { duration: .45 })); tl.call(() => { B.val.textContent = '8,4 GB'; });")
# cost: these VRAM values come from scoring ViHallu, so they differ from the 4.096-token peak on slide 9
f = sub(f, "'Bộ nhớ GPU đỉnh (MB)'", "'Bộ nhớ GPU đỉnh khi chấm ViHallu (MB)'")
f = sub(f, "· VRAM ${vr} MB<br>", "· VRAM ${vr}${vr.startsWith('—') ? '' : ' MB'}<br>")
# res: the Gemini row's label "0 · gọi API" read as "0 · gọi API tham số phải huấn luyện" in the hover
f = sub(f, "${ps} tham số phải huấn luyện", "${ps.replace(' · gọi API', '')} tham số phải huấn luyện")
# pipe: the sixth number is DRIFT (report Bảng 4.1), not a "peak chunk"; names as on slide 14
f = sub(f, "const FN = ['tỷ lệ nhìn lại', 'entropy', 'Gini', 'lớn nhất', 'khoảng cách', 'đoạn đỉnh'];",
        "const FN = ['tỷ lệ nhìn lại', 'entropy', 'Gini', 'tỷ trọng lớn nhất', 'khoảng cách đỉnh 1–2', 'độ dịch chuyển'];")
# loc and iv: the left-hand charts are generated examples, the real numbers are on the right
f = sub(f, "'Một mẫu ISE-DSC01: 22 đoạn ngữ cảnh, chú ý của đầu mạnh nhất (lớp 14, đầu 6)'",
        "'Minh họa một mẫu ISE-DSC01: 22 đoạn, chú ý của đầu mạnh nhất (lớp 14, đầu 6)'")
f = sub(f, "'Cùng một câu khẳng định, đọc hai lần trên hai ngữ cảnh mười câu'",
        "'Minh họa: cùng một câu khẳng định, đọc hai lần trên hai ngữ cảnh mười câu'")
# null: axis ticks used a hyphen while the values use the minus sign
f = sub(f, "(v > 0 ? '+' : '') + fmt(v, 2)", "(v > 0 ? '+' : v < 0 ? '−' : '') + fmt(Math.abs(v), 2)")
# costs: report 6.12 — the 8,2 s includes self-throttling to the free-tier quota; the API latency is about 5 s
f = sub(f, "hov(aD, 'Giám khảo Gemini (bản miễn phí) chấm 300 mẫu; mỗi mẫu một lượt gọi API.');",
        "hov(aD, 'Giám khảo Gemini (bản miễn phí) chấm 300 mẫu; mỗi mẫu một lượt gọi API. 8,2 giây gồm cả thời gian "
        "giãn nhịp để không vượt hạn mức; riêng độ trễ gọi API khoảng 5 giây.');")

for leftover in ("Rê chuột", "rê chuột lên từng", "Bấm nút", "Bấm “", "Bấm câu"):
    for m in re.finditer(r"cap: '[^']*'", f):
        assert leftover not in m.group(0), (leftover, m.group(0)[:120])

# ---------------------------------------------------------------- CSS additions
css += """
/* === BẢN 19 SLIDE (14/10/2026): bìa gộp, khoảng trống + câu hỏi, ba cột tự đánh giá === */
html.all .dots { display: none; }
.cv19 .band { position: absolute; left: 0; right: 0; top: 0; height: 16px; background: var(--iuh); }
.cv19 .band::after { content: ""; position: absolute; left: 0; right: 0; top: 16px; height: 6px; background: var(--iuh-gold); }
.cv19 svg.beams { position: absolute; inset: 0; width: 1920px; height: 1080px; pointer-events: none; }
.cv19 .owl { position: absolute; right: 90px; bottom: 0; height: 900px; }
.cv19 .logo { position: absolute; left: 120px; top: 74px; height: 100px; }
.cv19 .org { position: absolute; left: 120px; top: 206px; font: 600 24px/1.5 var(--sans); color: var(--iuh); letter-spacing: .04em; text-transform: uppercase; }
.cv19 .org span { display: block; font-weight: 500; color: var(--muted); font-size: 20px; letter-spacing: .1em; }
.cv19 .title { position: absolute; left: 120px; top: 318px; width: 1060px; }
.cv19 .kicker { font: 600 20px/1.4 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--ctx); }
.cv19 h1 { margin-top: 18px; font: 500 52px/1.15 var(--serif); letter-spacing: -.012em; }
.cv19 h1 em { font-style: italic; color: var(--ctx); }
.cv19 .team { position: absolute; left: 120px; top: 736px; display: flex; gap: 48px; }
.cv19 .who { border-left: 5px solid var(--iuh-gold); padding-left: 20px; }
.cv19 .who .r { font: 600 17px/1 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.cv19 .who .n { margin-top: 12px; font: 500 32px/1.2 var(--serif); }
.cv19 .who .id { margin-top: 6px; font: 400 20px/1 var(--sans); color: var(--muted); }
.cv19 .place { position: absolute; left: 120px; bottom: 56px; font: 500 22px/1 var(--sans); color: var(--muted); letter-spacing: .06em; }
.gq { position: absolute; left: 120px; right: 120px; top: 262px; display: grid; grid-template-columns: repeat(3, 1fr); column-gap: 32px; }
.gq .gcard, .gq .qcard { background: #fff; border: 2px solid var(--rule); border-top: 8px solid var(--c); border-radius: 14px; padding: 24px 30px 26px; }
.gq .k { font: 700 17px/1 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--c); }
.gq .s, .gq .q { margin-top: 14px; font: 500 29px/1.24 var(--serif); }
.gq .s em { font-style: italic; }
.gq .n, .gq .a { margin-top: 12px; font: 400 21px/1.42 var(--sans); color: var(--muted); }
.gq .ar { text-align: center; font: 700 30px/1 var(--sans); color: var(--c); padding: 10px 0 12px; }
.three { position: absolute; left: 120px; right: 120px; top: 262px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; }
.three .col { background: #fff; border-radius: 14px; border: 2px solid var(--rule); padding: 30px 32px 14px; }
.three h3 { font: 600 30px/1.2 var(--serif); margin-bottom: 18px; }
.three ul { list-style: none; }
.three li { position: relative; padding-left: 36px; margin-bottom: 18px; font: 400 23px/1.42 var(--sans); }
.three li::before { position: absolute; left: 0; top: 0; font: 700 24px/1.4 var(--sans); }
.three .yes li::before { content: "✓"; color: var(--ok); }
.three .no li::before { content: "—"; color: var(--bad); }
.three .nx li::before { content: "→"; color: var(--ctx); }
.three li b { font-weight: 600; }
"""

head = sub(head, "<title>Phát hiện ảo giác cho RAG tiếng Việt — slide khóa luận</title>",
           "<title>Phát hiện ảo giác cho RAG tiếng Việt — slide bảo vệ (19 slide)</title>")
out = (head + css + body_pre + "\n".join(ORDER) + body_post
       + "<script>" + gsap_js + "</script>\n<script>" + data_js + "</script>\n<script>" + f + "</script>" + tail)
OUT.write_text(out, encoding="utf-8")
print(f"wrote {OUT} ({len(out):,} chars, {out.count('<section class=')} slides)")
