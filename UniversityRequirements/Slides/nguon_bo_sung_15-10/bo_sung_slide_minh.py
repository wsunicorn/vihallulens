# -*- coding: utf-8 -*-
"""Chèn bốn slide còn thiếu theo góp ý của thầy vào bộ 19 slide của Minh, giữ nguyên 19 slide gốc.

  + Bài toán                         (Chương 1, sau slide hai kiểu ảo giác)
  + Các hướng phát hiện ảo giác đã có (Chương 2, trước Lookback Lens)
  + Kiểm định năm giả thuyết          (Tự đánh giá, trước slide đã làm / chưa làm)
  + Tài liệu tham khảo chính          (trước slide cảm ơn)

Sơ đồ của ba slide đầu lấy từ figs_minh_bo_sung.js (cùng bộ hàm vẽ với file của Minh).
Số slide ở chân trang và các chỗ "Trả lời ở slide …" được đánh lại theo thứ tự mới.
"""
import io, re, sys, html as H

SRC, JS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
h = io.open(SRC, encoding='utf-8').read()

starts = [m.start() for m in re.finditer(r'<section class="slide', h)]
ends = [h.index('</section>', s) + len('</section>') for s in starts]
assert len(starts) == 19, len(starts)
head_part, tail_part = h[:starts[0]], h[ends[-1]:]
S = [h[a:b] for a, b in zip(starts, ends)]
gaps = [h[ends[i]:starts[i + 1]] for i in range(18)]
assert all(not g.strip() for g in gaps)

run_tpl = re.search(r'(<div class="run">.*?<span class="sec">)(.*?)(</span></div>)', S[1], re.S)
RUN = lambda sec: run_tpl.group(1) + sec + run_tpl.group(3)
assert 'Chương 1' in run_tpl.group(2)


def fig_slide(sec, title, fig, src, notes):
    return f'''<section class="slide" data-fig="{fig}" data-notes="{H.escape(notes)}">
  {RUN(sec)}
  <div class="head"><h2>{title}</h2></div>
  <div class="fig"><svg viewBox="0 0 1680 560"></svg></div>
  <div class="stepcap"><div class="dots"></div><div class="txt"></div></div>
  <div class="foot"><span>{src}</span><span>00</span></div>
</section>'''


TASK = fig_slide('Chương 1 · Giới thiệu',
  'Bài toán: cho ngữ cảnh, câu hỏi và câu trả lời, xác định câu trả lời trung thực, ảo giác nội tại hay ngoại lai',
  'task', 'Mục 1.3–1.4, 4.1 và 4.7 báo cáo · ví dụ thật: câu hỏi Hồ Hoàn Kiếm',
  'Đầu vào của bài toán gồm ba thành phần: ngữ cảnh hệ RAG đã truy xuất, chia thành các đoạn; câu hỏi; và câu trả lời cần chấm, của bất kỳ hệ RAG nào. Một mô hình ngôn ngữ mở đọc lại cả ba trong một lượt, rồi bộ phân loại tuyến tính, phần duy nhất phải huấn luyện, cho ra nhãn ba lớp và điểm rủi ro bằng một trừ xác suất trung thực. Tỷ trọng chú ý theo đoạn lấy từ lượt đọc. Bốn ràng buộc: không gọi mô hình giám khảo, không tinh chỉnh mô hình ngôn ngữ, vừa một GPU T4 16 GB, tiếng Việt ba lớp nhãn. Rê chuột lên khối bộ phát hiện để xem chú thích.')

MAP = fig_slide('Chương 2 · Cơ sở lý thuyết',
  'Các hướng phát hiện ảo giác và vị trí của khóa luận',
  'map', 'Bảng 2.1 · Nguyen và Nguyen (2020) · Conneau và cộng sự (2020) · Zheng và cộng sự (2023) · Manakul và cộng sự (2023) · Azaria và Mitchell (2023) · Sun và cộng sự (2025)',
  'Bảng 2.1 đặt các hướng phát hiện ảo giác lên hai trục: tham số phải huấn luyện và chi phí mỗi lần chấm. Đặc trưng bề mặt rẻ nhưng thô; bộ mã hóa tinh chỉnh như PhoBERT, XLM-R chính xác nhưng phải huấn luyện hàng trăm triệu tham số. LLM giám khảo và kiểm tra tính nhất quán như SelfCheckGPT không cần huấn luyện, nhưng mỗi lần chấm tốn một lượt gọi hoặc nhiều lượt sinh. Hướng nội tại chỉ cần một lượt đọc và một bộ dò nhỏ; khóa luận thuộc nhánh trọng số chú ý, cùng Lookback Lens và ReDeEP. Rê chuột lên từng ô để xem tín hiệu và hạn chế.')

HYP = fig_slide('Chương 7–8 · Tự đánh giá',
  'Tự đánh giá: ba trên năm giả thuyết được ủng hộ, giả thuyết chính về chunk-aware thì không',
  'hyp', 'Bảng 1.1 và Bảng 7.1 báo cáo',
  'Nhóm em đối chiếu kết quả với năm giả thuyết ở Bảng 1.1, phát biểu lại từ ba câu hỏi nghiên cứu. H1 được ủng hộ: tỷ lệ lookback gộp đạt 0,745, vượt đặc trưng bề mặt, ngang PhoBERT. H2, giả thuyết chính về chunk-aware, không được ủng hộ: +0,012 nằm trong khoảng tin cậy, chỉ +0,007 trên ngữ cảnh dài, và đổi dấu theo mô hình đọc. H3, H4 được ủng hộ: đầu mạnh nhất nhìn đúng đoạn bằng chứng ở 87,8 % số mẫu; thay câu bằng chứng thì bốn đặc trưng đổi đúng hướng ở 71–75 % số cặp. H5 bị bác bỏ ở bài toán ba lớp, nhưng quyết định nhị phân vẫn chuyển được. Rê chuột để xem thí nghiệm tương ứng.')

REFS = [
  ('Phương pháp nền', [
    (3, 'Chuang, Y.-S., Qiu, L., Hsieh, C.-Y., Krishna, R., Kim, Y., Glass, J. (2024). Lookback Lens: Detecting and Mitigating Contextual Hallucinations in Large Language Models Using Only Attention Maps. <i>EMNLP 2024</i>, 1419–1436.'),
    (29, 'Vaswani, A. và cộng sự (2017). Attention Is All You Need. <i>NeurIPS 30</i>, 5998–6008.'),
    (24, 'Sun, Z. và cộng sự (2025). ReDeEP: Detecting Hallucination in Retrieval-Augmented Generation via Mechanistic Interpretability. <i>ICLR 2025</i>.')]),
  ('Dữ liệu', [
    (20, 'Nguyen, A. T.-H. và cộng sự (2026). DSC2025 – ViHallu Challenge: Detecting Hallucination in Vietnamese LLMs. <i>arXiv:2601.04711</i>.'),
    (28, 'UIT Data Science Challenge 2023, Group B (bộ ISE-DSC01). <i>codalab.lisn.upsaclay.fr/competitions/15497</i>.'),
    (15, 'Le, H. T., To, L. T., Nguyen, M. T., Nguyen, K. V. (2024). ViWikiFC: Fact-Checking for Vietnamese Wikipedia-Based Textual Knowledge Source. <i>arXiv:2405.07615</i>.')]),
  ('Mốc so sánh', [
    (21, 'Nguyen, D. Q., Nguyen, A. T. (2020). PhoBERT: Pre-trained Language Models for Vietnamese. <i>Findings of EMNLP 2020</i>, 1037–1042.'),
    (4, 'Conneau, A. và cộng sự (2020). Unsupervised Cross-lingual Representation Learning at Scale. <i>ACL 2020</i>, 8440–8451.'),
    (32, 'Zheng, L. và cộng sự (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. <i>NeurIPS 36</i>.'),
    (26, 'Tran, D. X. và cộng sự (2025). SemViQA: A Semantic Question Answering System for Vietnamese Information Fact-Checking. <i>arXiv:2503.00955</i>.')]),
  ('Mô hình và nền tảng', [
    (22, 'Qwen Team (2024). Qwen2.5 Technical Report. <i>arXiv:2412.15115</i>.'),
    (16, 'Lewis, P. và cộng sự (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. <i>NeurIPS 33</i>, 9459–9474.'),
    (12, 'Ji, Z. và cộng sự (2023). Survey of Hallucination in Natural Language Generation. <i>ACM Computing Surveys 55 (12)</i>, 1–38.')])]
REF_BODY = '<div class="refs">' + ''.join(
    f'<div class="grp rise r{k + 1}"><h3>{grp}</h3><ul>' + ''.join(f'<li><span class="rn">[{n}]</span>{t}</li>' for n, t in items) + '</ul></div>'
    for k, (grp, items) in enumerate(REFS)) + '</div>'
REF = f'''<section class="slide" data-notes="{H.escape('Đây là các công trình chính mà đề tài dựa vào, đánh số theo danh mục 32 tài liệu của quyển. Phương pháp nền là Lookback Lens, xây trên cơ chế chú ý của Transformer; ReDeEP là hướng gần nhất cùng khai thác tín hiệu nội tại cho RAG. Dữ liệu gồm ViHallu, ISE-DSC01 và ViWikiFC. Các mốc so sánh là PhoBERT, XLM-R, LLM giám khảo, và SemViQA trên ViWikiFC. Mô hình đọc là Qwen2.5. Danh mục đầy đủ nằm ở cuối quyển khóa luận.')}">
  {RUN('Tài liệu tham khảo')}
  <div class="head"><h2>Tài liệu tham khảo chính</h2></div>
  {REF_BODY}
  <div class="foot"><span>Số trong ngoặc theo danh mục 32 tài liệu của quyển khóa luận</span><span>00</span></div>
</section>'''

# thứ tự mới: chỉ số 0..18 là 19 slide gốc của Minh
ORDER = [S[0], S[1], TASK, S[2], S[3], MAP, *S[4:17], HYP, S[17], REF, S[18]]
assert len(ORDER) == 23

out = []
for pos, s in enumerate(ORDER, 1):
    s = re.sub(r'(<div class="foot"><span>.*?</span><span>)[^<]*(</span></div>)', lambda m: f'{m.group(1)}{pos:02d}{m.group(2)}', s, flags=re.S)
    out.append(s)
deck = '\n'.join(out)

# slide 12–15 cũ (kết quả, định vị, can thiệp, vùng nhiễu) giờ là 14–17; 3 → 4, 16 → 18, 15 → 17, 17 → 19
for a, b in [('Trả lời ở slide 12–15', 'Trả lời ở slide 14–17'), ('Trả lời ở slide 3 và 16', 'Trả lời ở slide 4 và 18'),
             ('Trả lời ở slide 15 và 17', 'Trả lời ở slide 17 và 19')]:
    assert deck.count(a) == 1, a
    deck = deck.replace(a, b)

CSS = '''
/* === BỔ SUNG 15/10: slide tài liệu tham khảo chính === */
.refs { position: absolute; left: 120px; right: 120px; top: 210px; display: grid; grid-template-columns: 1fr 1fr; gap: 26px 56px; }
.refs .grp h3 { margin: 0 0 10px; font: 700 18px/1 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--ctx); }
.refs ul { margin: 0; padding: 0; list-style: none; }
.refs li { position: relative; padding-left: 58px; font: 400 21px/1.4 var(--sans); margin-bottom: 10px; }
.refs li .rn { position: absolute; left: 0; top: 0; font-weight: 700; color: var(--ctx); }
.refs li i { color: var(--muted); }
'''
i = head_part.rindex('</style>')
head_part = head_part[:i] + CSS + head_part[i:]

js = io.open(JS, encoding='utf-8').read()
k = tail_part.index("const stage = document.querySelector('.deck-stage')")
k = tail_part.rindex('/* =====', 0, k)
tail_part = tail_part[:k] + '/* === BỔ SUNG 15/10: sơ đồ bài toán, các hướng đã có, kiểm định giả thuyết === */\n' + js + '\n' + tail_part[k:]

io.open(OUT, 'w', encoding='utf-8').write(head_part + deck + tail_part)
print(OUT, len(ORDER), 'slide')
