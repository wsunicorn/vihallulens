"""Final pass on the committee deck: academic titles, agenda, part dividers and the E19 result.

Reads the 23-slide deck produced by ``b2_bo_sung.py`` and writes the 31-slide deck that
is presented to the committee. Nothing here changes a figure's data; it changes wording and
structure only:

  * every slide title names its content instead of stating a conclusion; the conclusion moves
    to a one-line summary under the title (``<p class="lede">``)
  * colloquial wording in on-slide text, figure labels, step captions and speaker notes is
    replaced by academic wording consistent with the thesis
  * an agenda slide after the cover, and a divider before each of the seven parts
  * slide 15 (localisation) gains a fifth step with experiment E19 (attention vs. ablation)
  * footer page numbers and the "Trả lời ở slide …" pointers are renumbered

Every text replacement states how many times its source string must occur, so a change in an
earlier stage fails loudly here instead of silently leaving old wording on a slide.

Step 3 of the deck build; ``dung_lai.py`` runs all steps. Alone:

    python b3_hoan_thien.py ../_build/slide_hoi_dong_23.html ../slide_hoi_dong.html
"""

# ruff: noqa: E501 — replacement pairs are exact slide strings, kept whole so each stays greppable

import html
import json
import re
import sys
from pathlib import Path

SRC, OUT = (Path(p) for p in sys.argv[1:3])
page = SRC.read_text(encoding="utf-8")

starts = [m.start() for m in re.finditer(r'<section class="slide', page)]
ends = [page.index("</section>", s) + len("</section>") for s in starts]
assert len(starts) == 23, len(starts)
head_part, tail_part = page[: starts[0]], page[ends[-1] :]
S = [page[a:b] for a, b in zip(starts, ends, strict=True)]
FIG = [(re.search(r'data-fig="([^"]*)"', s) or [None, None])[1] for s in S]

# index of each slide of the 23-slide deck, by its figure name or role
IDX = {name: k for k, name in enumerate(FIG) if name}
IDX.update(cover=0, gaps=4, done=20, refs=21, thanks=22)
assert FIG[4] is None and FIG[20] is None and FIG[21] is None, FIG

problems: list[str] = []


def sub(text: str, old: str, new: str, n: int = 1, where: str = "") -> str:
    """Replace ``old`` with ``new``; record a problem unless it occurs exactly ``n`` times."""
    got = text.count(old)
    if got != n:
        problems.append(f"{where or 'deck'}: expected {n}× got {got}× — {old[:90]}")
    return text.replace(old, new)


# ---------------------------------------------------------------------------------------------
# 1. Titles and one-line summaries
# ---------------------------------------------------------------------------------------------
TITLES = {
    "types": (
        "Phân loại ảo giác: nội tại và ngoại lai",
        "Ba lớp nhãn theo bộ ViHallu: trung thực, ảo giác nội tại và ảo giác ngoại lai.",
    ),
    "task": (
        "Phát biểu bài toán",
        "Đầu vào: ngữ cảnh, câu hỏi, câu trả lời. Đầu ra: nhãn ba lớp, điểm rủi ro và tỷ "
        "trọng chú ý theo đoạn.",
    ),
    "costs": (
        "Động lực nghiên cứu: hạn chế của các phương pháp hiện có",
        "Mỗi phương pháp phổ biến có một hạn chế: chi phí gọi API, số tham số huấn luyện "
        "lớn, hoặc độ chính xác thấp.",
    ),
    "gaps": ("Khoảng trống và câu hỏi nghiên cứu", None),
    "map": (
        "Các hướng phát hiện ảo giác và vị trí của khóa luận",
        "Khóa luận thuộc hướng nội tại, nhánh trọng số chú ý: một lượt đọc, không tinh chỉnh, "
        "không gọi API.",
    ),
    "lb": (
        "Phương pháp nền: Lookback Lens",
        "Mỗi đầu chú ý được mô tả bằng tỷ lệ chú ý dành cho ngữ cảnh so với phần câu trả lời "
        "đứng trước.",
    ),
    "data": (
        "Dữ liệu và phương pháp chia tập theo ngữ cảnh",
        "Ba bộ dữ liệu chính chia tập theo ngữ cảnh để tránh rò rỉ; ViFactCheck dùng cho thí "
        "nghiệm chuyển miền (E17).",
    ),
    "chunk": (
        "Phương pháp đề xuất: chunk-aware lookback ratio",
        "Tách tỷ lệ chú ý theo từng đoạn ngữ cảnh để đo vị trí và hình dạng phân bố chú ý, "
        "không chỉ tổng lượng.",
    ),
    "pipe": (
        "Quy trình phát hiện ảo giác trong một lượt đọc",
        "Mô hình đọc câu trả lời có sẵn, không sinh thêm token; chỉ bộ phân loại tuyến tính "
        "cần huấn luyện.",
    ),
    "hook": (
        "Trích xuất trọng số chú ý bằng forward hook",
        "Đặc trưng được tính tại từng lớp rồi giải phóng ma trận: bộ nhớ đỉnh 8,4 GB trên "
        "GPU Tesla T4 16 GB.",
    ),
    "sys": (
        "Kiến trúc hệ thống ViHalluLens",
        "Bốn tầng: trích chú ý, đặc trưng, bộ phát hiện, phục vụ; dùng qua thư viện Python, "
        "REST, Docker, giao diện web.",
    ),
    "demo": (
        "Minh họa hệ thống trên hệ RAG",
        "Hệ thống phát hiện mệnh đề không có căn cứ do mô hình tự sinh và gán nhãn ngoại lai, "
        "điểm rủi ro 0,997.",
    ),
    "res": (
        "Kết quả phân loại trên ViHallu",
        "Bộ phân loại tuyến tính trên đặc trưng chú ý tương đương PhoBERT tinh chỉnh toàn bộ, "
        "với 579 tham số.",
    ),
    "loc": (
        "Kiểm chứng cơ chế: định vị đoạn chứa bằng chứng",
        "Đầu chú ý mạnh nhất xác định đúng đoạn bằng chứng ở 87,8 % số mẫu, chính xác hơn cắt "
        "bỏ ngữ cảnh (E19).",
    ),
    "iv": (
        "Thí nghiệm can thiệp: loại bỏ câu bằng chứng",
        "Khi thay câu bằng chứng, cả bốn đặc trưng hình dạng thay đổi đúng hướng đã dự đoán "
        "trước khi chạy.",
    ),
    "null": (
        "Đóng góp của đặc trưng hình dạng vào phân loại",
        "Mức tăng của chunk-aware so với lookback gộp nằm trong vùng nhiễu ở cả sáu phép đo.",
    ),
    "cost": (
        "Đánh đổi độ chính xác và chi phí theo kích thước mô hình đọc",
        "Mô hình đọc 3B nhanh gấp đôi, dùng ít hơn 55 % bộ nhớ so với 7B; macro-F1 chỉ giảm "
        "khoảng 0,01.",
    ),
    "xfer": (
        "Khái quát hóa chéo bộ dữ liệu",
        "Quyết định nhị phân chuyển giao được sang bộ dữ liệu khác; phân loại ba lớp thì không.",
    ),
    "hyp": (
        "Kiểm định năm giả thuyết nghiên cứu",
        "Ba giả thuyết được ủng hộ (H1, H3, H4); H2 về chunk-aware không được ủng hộ; H5 bị bác "
        "bỏ ở bài toán ba lớp.",
    ),
    "done": ("Kết quả đạt được, hạn chế và hướng phát triển", None),
    "refs": ("Tài liệu tham khảo", None),
}

for key, (title, lede) in TITLES.items():
    k = IDX[key]
    s = S[k]
    m = re.search(r"<h2>(.*?)</h2>", s, re.S)
    assert m, key
    new = f"<h2>{title}</h2>" + (f'<p class="lede">{lede}</p>' if lede else "")
    S[k] = s[: m.start()] + new + s[m.end() :]

# ---------------------------------------------------------------------------------------------
# 2. Speaker notes, rewritten in full (academic wording, figures unchanged)
# ---------------------------------------------------------------------------------------------
OP = "<br><br><b>Thao tác:</b> "
NOTES = {
    "cover": "Kính chào quý thầy cô trong hội đồng. Nhóm em gồm Nguyễn Ngọc Lân và Nguyễn Tấn Minh, "
    "dưới sự hướng dẫn của ThS. Trương Vĩnh Linh. Đề tài của nhóm là nghiên cứu và xây dựng hệ "
    "thống phát hiện ảo giác cho mô hình ngôn ngữ lớn tăng cường truy xuất tiếng Việt, dựa trên tín "
    "hiệu chú ý nội tại. Ý tưởng chính: khi mô hình đọc lại câu trả lời cùng ngữ cảnh đã truy xuất, "
    "cách mô hình phân bổ chú ý cho biết câu trả lời có dựa trên ngữ cảnh hay không, mà không cần "
    "gọi thêm một mô hình giám khảo nào.",
    "types": "Hệ RAG truy xuất tài liệu rồi để mô hình ngôn ngữ trả lời dựa trên tài liệu đó, nhưng "
    "câu trả lời vẫn có thể chứa thông tin không có căn cứ. Theo cách gán nhãn của bộ ViHallu, ảo "
    "giác có hai loại. Ảo giác nội tại là nội dung dựa trên ngữ cảnh nhưng mâu thuẫn với ngữ cảnh, "
    "ví dụ đổi triều Lý thành triều Trần. Ảo giác ngoại lai là thông tin không có trong ngữ cảnh, "
    "ví dụ tháp Eiffel ở hồ Tây. Hệ thống của nhóm cho điểm rủi ro của ba câu trả lời này lần lượt "
    "là 0,001, 0,998 và 1,000. Bài toán vì vậy là phân loại ba lớp, không chỉ phân biệt đúng và sai."
    + OP
    + "rê chuột lên phần tô màu để đối chiếu với tài liệu; bấm một thẻ để làm nổi đường nối.",
    "task": "Đầu vào của bài toán gồm ba thành phần: ngữ cảnh mà hệ RAG đã truy xuất, chia thành các "
    "đoạn; câu hỏi; và câu trả lời cần đánh giá, có thể đến từ bất kỳ hệ RAG nào. Một mô hình ngôn "
    "ngữ mã nguồn mở đọc cả ba thành phần trong một lượt; bộ phân loại tuyến tính phía sau, phần "
    "duy nhất cần huấn luyện, cho ra nhãn ba lớp và điểm rủi ro, bằng một trừ xác suất trung thực. "
    "Tỷ trọng chú ý theo đoạn được lấy từ chính lượt đọc đó. Đề tài có bốn ràng buộc: không gọi mô "
    "hình giám khảo, không tinh chỉnh mô hình ngôn ngữ, chạy trên một GPU Tesla T4 16 GB, và xử lý "
    "tiếng Việt với ba lớp nhãn." + OP + "rê chuột lên khối bộ phát hiện để xem chú thích.",
    "costs": "Các phương pháp phát hiện ảo giác phổ biến hiện nay đều có hạn chế về chi phí hoặc độ "
    "chính xác. Dùng một LLM khác làm giám khảo, như Gemini, mất khoảng 8,2 giây cho mỗi mẫu, tính "
    "cả thời gian giãn nhịp theo hạn mức của bản miễn phí; dữ liệu phải gửi ra ngoài, và macro-F1 "
    "chỉ đạt 0,664. Tinh chỉnh bộ mã hóa như XLM-R cho độ chính xác cao nhất, 0,776, nhưng phải "
    "huấn luyện 560 triệu tham số trên GPU. Đặc trưng bề mặt chỉ có 9 tham số nhưng chỉ đạt 0,656. "
    "Vì vậy đề tài tìm một tín hiệu có sẵn ngay trong lượt đọc của mô hình.",
    "gaps": "Từ hiện trạng đó, nhóm em xác định ba khoảng trống nghiên cứu. Thứ nhất, chưa có công "
    "trình tách tỷ lệ chú ý theo từng đoạn ngữ cảnh và kiểm chứng phân bố đó có trùng với vị trí "
    "bằng chứng hay không. Thứ hai, ba hướng tiếp cận chưa được đặt trên cùng một thang đo gồm cả "
    "độ chính xác lẫn chi phí. Thứ ba, chưa có công trình nào dùng tín hiệu nội tại để phát hiện ảo "
    "giác tiếng Việt. Ba khoảng trống này tương ứng với ba câu hỏi nghiên cứu cùng màu ở hàng dưới; "
    "mỗi thẻ ghi các slide trả lời câu hỏi đó.",
    "map": "Bảng 2.1 đặt các hướng phát hiện ảo giác trên hai trục: số tham số phải huấn luyện và "
    "chi phí mỗi lần đánh giá. Đặc trưng bề mặt có chi phí thấp nhưng chỉ nắm được mẫu hình thô; bộ "
    "mã hóa tinh chỉnh như PhoBERT, XLM-R chính xác nhưng phải huấn luyện hàng trăm triệu tham số. "
    "LLM giám khảo và kiểm tra tính nhất quán như SelfCheckGPT không cần huấn luyện, nhưng mỗi lần "
    "đánh giá cần một lượt gọi API hoặc nhiều lượt sinh. Hướng nội tại chỉ cần một lượt đọc và một "
    "bộ phân loại nhỏ; khóa luận thuộc nhánh trọng số chú ý, cùng với Lookback Lens và ReDeEP."
    + OP
    + "rê chuột lên từng ô để xem tín hiệu và hạn chế.",
    "lb": "Phương pháp nền là Lookback Lens, công bố tại EMNLP 2024. Với mỗi token của câu trả lời, "
    "phương pháp đo phần chú ý dành cho ngữ cảnh và phần dành cho các token câu trả lời đứng trước; "
    "tỷ lệ giữa hai phần này gọi là tỷ lệ lookback. Lấy trung bình trên mọi token, riêng cho từng "
    "đầu chú ý, ta được 27 lớp nhân 28 đầu, tức 756 giá trị; lớp cuối của Qwen2.5-7B bị loại vì "
    "tràn số ở float16. Một bộ phân loại tuyến tính nhận 756 giá trị này làm đầu vào. Nhóm em tái "
    "lập phương pháp này trên tiếng Việt với bài toán ba lớp.",
    "data": "Nhóm sử dụng ba bộ dữ liệu tiếng Việt công khai. ViHallu gồm 7.000 mẫu là bộ chính, câu "
    "trả lời do GPT-4o sinh; ISE-DSC01 có ngữ cảnh dài, trung vị 19 câu, và có đánh dấu sẵn câu "
    "bằng chứng; ViWikiFC dùng làm đối chứng ngoài. Bộ thứ tư, ViFactCheck thuộc miền tin tức, được "
    "dùng ở thí nghiệm chuyển miền E17. Điểm quan trọng là phương pháp chia tập: nếu chia ngẫu "
    "nhiên từng dòng, các câu trả lời của cùng một tài liệu sẽ nằm ở cả tập huấn luyện lẫn tập kiểm "
    "tra, gây rò rỉ dữ liệu. Vì vậy nhóm chia theo ngữ cảnh, tỷ lệ 80/10/10, hạt giống 42, mức rò rỉ "
    "bằng 0. Nhóm cũng xác định tập kiểm tra gốc của ViWikiFC dùng lại 100 % ngữ cảnh của tập huấn "
    "luyện." + OP + "bấm hai nút ở góc phải để so sánh hai cách chia.",
    "chunk": "Đây là đóng góp chính của đề tài. Hai câu trả lời có thể cùng dành 62 % chú ý cho ngữ "
    "cảnh, nhưng một câu tập trung chú ý vào đúng câu chứa thông tin, còn câu kia phân bố đều. "
    "Lookback Lens tổng hợp thành một giá trị duy nhất nên không phân biệt được hai trường hợp này. "
    "Chunk-aware lookback ratio cộng chú ý theo từng đoạn ngữ cảnh, rồi mô tả hình dạng phân bố "
    "bằng năm đặc trưng, trong đó có entropy và tỷ trọng lớn nhất. Số liệu trên hình là minh họa "
    "nguyên lý, tương ứng Hình 2.1 của báo cáo.",
    "pipe": "Toàn bộ quy trình chỉ cần một lượt đọc; mô hình không sinh thêm token nào. Bước một, "
    "ghép câu hỏi, ngữ cảnh và câu trả lời vào một mẫu prompt cố định và ghi lại vị trí của hai "
    "vùng. Bước hai, Qwen2.5-7B đọc một lượt; tại 27 lớp, forward hook tính chú ý theo đoạn rồi "
    "giải phóng ma trận; lớp cuối bị loại vì tràn số ở float16. Bước ba, giữ 32 đầu chú ý xếp hạng "
    "cao nhất, mỗi đầu 6 giá trị, tổng cộng 192 đặc trưng. Bước bốn, hồi quy logistic với 579 tham "
    "số chuyển 192 đặc trưng thành ba xác suất. Câu trả lời về Hồ Hoàn Kiếm, có chứa một mệnh đề "
    "không có căn cứ, nhận điểm rủi ro 0,997.",
    "hook": "Rủi ro kỹ thuật lớn nhất của đề tài là bộ nhớ. Muốn đọc trọng số chú ý thì phải tắt các "
    "cài đặt tối ưu như FlashAttention; với 4.096 token, ma trận chú ý của một lớp đã chiếm khoảng "
    "0,94 GB. Giữ ma trận của cả 28 lớp cần khoảng 26 GB, nên GPU Tesla T4 16 GB sẽ tràn bộ nhớ từ "
    "lớp thứ 12. Nhóm dùng forward hook: khi một lớp tính xong, hook cộng chú ý theo đoạn rồi giải "
    "phóng ma trận. Nhờ vậy, bộ nhớ đỉnh đo thực tế ở ngưỡng 4.096 token chỉ là 8.428 MB."
    + OP
    + "rê chuột lên từng lớp để xem bộ nhớ tại lớp đó.",
    "sys": "Hệ thống gồm bốn tầng, tầng trên chỉ gọi tầng ngay bên dưới: trích chú ý, tính đặc "
    "trưng, bộ phát hiện và phục vụ. Hệ thống có ba cách sử dụng: gọi thư viện Python, gọi dịch vụ "
    "REST, hoặc triển khai toàn bộ bằng Docker, kèm giao diện web. Bộ phát hiện chỉ là một tệp "
    "11,5 KB; khi nạp lại và chấm 700 mẫu kiểm tra, kết quả trùng 700/700 với lúc thí nghiệm. Bộ "
    "kiểm thử gồm 825 ca tự động." + OP + "rê chuột lên từng tầng để xem mô-đun tương ứng.",
    "demo": "Đây là một lượt vận hành trên hệ RAG, thực hiện trên GPU Tesla T4 của Kaggle ngày "
    "11/09/2026. Hệ thống truy xuất ba tài liệu trong kho 21 bài; Qwen2.5-3B sinh câu trả lời, còn "
    "Qwen2.5-7B chỉ đọc lại để đánh giá, vì trên T4 hai vai trò này phải tách thành hai mô hình. Câu "
    "trả lời đúng ở ý đầu nhưng bổ sung cụm “sau đó anh ta đã trở về dinh thự”, không có trong ngữ "
    "cảnh. Câu trả lời này không được soạn sẵn: mô hình tự sinh ra mệnh đề không có căn cứ, và bộ "
    "phát hiện gán nhãn ngoại lai với điểm rủi ro 0,997."
    + OP
    + "bấm tên câu hỏi ở góc phải để xem ba ví dụ còn lại.",
    "res": "Đây là kết quả chính trên 700 mẫu kiểm tra của ViHallu. Hai mốc đầu, đặc trưng bề mặt và "
    "Gemini, đạt khoảng 0,66; lưu ý Gemini chỉ được chấm trên 300 mẫu. Hai bộ mã hóa tinh chỉnh đạt "
    "0,749 và 0,776. Hướng chú ý đạt 0,745 với lookback gộp và 0,757 với chunk-aware; khoảng tin cậy "
    "chồng lên khoảng tin cậy của XLM-R, nên nhóm kết luận là tương đương, không khẳng định cao hơn. "
    "Khác biệt nằm ở số tham số phải huấn luyện: 579 so với 369 triệu của PhoBERT. Kết quả này không "
    "so sánh trực tiếp với 84,80 % của đội dẫn đầu cuộc thi ViHallu, vì khác tập đánh giá, và các "
    "đội dẫn đầu tinh chỉnh LLM, còn nhóm em không tinh chỉnh mô hình nào."
    + OP
    + "rê chuột lên từng dòng để xem khoảng tin cậy và số tham số.",
    "loc": "Đây là phép kiểm chứng cơ chế trực tiếp, không đi qua bộ phân loại. Trên 2.376 mẫu "
    "ISE-DSC01 có bằng chứng định vị được, nhóm xác định đoạn mà đầu chú ý mạnh nhất phân bổ chú ý "
    "nhiều nhất. Đoạn đó trùng với đoạn chứa bằng chứng ở 87,8 % số mẫu, gấp 14,3 lần mức ngẫu "
    "nhiên. Lặp lại trên ViWikiFC, trung bình mọi đầu đạt 32,9 % so với 33,2 %, chênh lệch 0,003. "
    "Thí nghiệm E19 so sánh với phương pháp cắt bỏ từng đoạn ngữ cảnh trên 300 mẫu ViWikiFC: đầu chú "
    "ý mạnh nhất xác định đúng 85,0 %, cắt bỏ ngữ cảnh đạt 73,3 %; đầu chú ý cần một lượt đọc, cắt "
    "bỏ cần trung bình 10,9 lượt. Một đầu chọn trên ISE-DSC01 vẫn đạt 79,7 %, cao hơn cắt bỏ, nên ưu "
    "thế không đến từ việc chọn đầu trên dữ liệu đích." + OP + "bấm “Mẫu khác” để xem thêm ví dụ "
    "minh họa.",
    "iv": "Các kết quả trước là tương quan, nên nhóm thực hiện thêm một thí nghiệm can thiệp. Cùng "
    "một phát biểu được đọc trên hai ngữ cảnh mười câu, chỉ khác nhau ở câu bằng chứng. Trên 1.836 "
    "cặp ViWikiFC, cả bốn đặc trưng hình dạng thay đổi đúng hướng ở 71 đến 75 % số cặp. Hướng thay "
    "đổi được ghi trong mã trước khi chạy, nên đây không phải giải thích sau khi đã biết kết quả; "
    "tuy vậy, mức thay đổi trung vị nhỏ, chỉ từ 0,013 đến 0,016."
    + OP
    + "ba nút ở góc phải hiển thị riêng ngữ cảnh A, ngữ cảnh B hoặc cả hai.",
    "null": "Đây là kết quả không ủng hộ giả thuyết chính, và nhóm trình bày đầy đủ. Chunk-aware cao "
    "hơn lookback gộp 0,0116 trên ViHallu, nhưng điểm số dao động khoảng ±0,03 khi đổi tập kiểm tra. "
    "Nhóm đo lại thêm năm lần: thêm đặc trưng bề mặt, đổi sang Sailor2-8B, thu nhỏ xuống 3B và 1.5B, "
    "đổi sang ViWikiFC; tất cả đều nằm trong vùng nhiễu, và dấu của chênh lệch còn đổi chiều. Nguyên "
    "nhân là đặc trưng hình dạng mang cùng tín hiệu với tỷ lệ gộp: trên ISE-DSC01, 99,9 % phần đóng "
    "góp của nhóm hình dạng đã có sẵn trong tỷ lệ gộp, trong khi chính tỷ lệ gộp cộng thêm 0,109 vào "
    "đặc trưng bề mặt. Trên bộ tin tức ViFactCheck (E17), khi so cùng số đầu, hình dạng chỉ thêm "
    "0,009; chấm theo từng câu của phản hồi (E18) cũng không cho kết quả cao hơn."
    + OP
    + "rê chuột lên từng điểm.",
    "cost": "Về chi phí, nhóm đặt mọi phương pháp trên cùng một mặt phẳng. XLM-R tốt hơn cả về độ "
    "chính xác lẫn tốc độ: 25,2 ms mỗi mẫu so với 437,6 ms của mô hình đọc 7B. Hướng chú ý có ưu thế "
    "về số tham số phải huấn luyện, từ 195 đến 2.271. Thu nhỏ mô hình đọc xuống 3B thì tốc độ tăng "
    "gần gấp đôi, bộ nhớ chỉ 3.710 MB, macro-F1 giảm khoảng 0,01; còn mô hình 1.5B lại chậm hơn cả "
    "7B, vì phải chạy bfloat16 mà T4 không hỗ trợ ở mức phần cứng."
    + OP
    + "rê chuột lên từng điểm để xem đầy đủ số liệu.",
    "xfer": "Nội dung cuối của phần thực nghiệm là khả năng khái quát hóa. Khi huấn luyện trên "
    "ViHallu rồi đánh giá trên ISE-DSC01, macro-F1 ba lớp giảm còn 0,358, gần mức ngẫu nhiên: trong "
    "1.286 câu ngoại lai, chỉ 66 câu được phân loại đúng, 988 câu bị phân loại thành nội tại. Chiều "
    "ngược lại mất lớp nội tại. Tuy nhiên, quyết định nhị phân có ảo giác hay không vẫn chuyển giao "
    "được, đạt 0,664 và 0,776. Nguyên nhân khả dĩ là hai bộ định nghĩa nhãn khác nhau: ngoại lai "
    "trong ViHallu là nội dung do GPT-4o bổ sung, còn trong ISE-DSC01 là phát biểu NEI do người viết."
    + OP
    + "bấm hai nút ở góc phải để đổi chiều.",
    "hyp": "Nhóm em đối chiếu kết quả với năm giả thuyết ở Bảng 1.1, phát biểu từ ba câu hỏi nghiên "
    "cứu. H1 được ủng hộ: tỷ lệ lookback gộp đạt 0,745, cao hơn đặc trưng bề mặt, tương đương "
    "PhoBERT. H2, giả thuyết chính về chunk-aware, không được ủng hộ: mức tăng 0,012 nằm trong khoảng "
    "tin cậy, chỉ 0,007 trên ngữ cảnh dài, và đổi dấu theo mô hình đọc. H3 và H4 được ủng hộ: đầu chú "
    "ý mạnh nhất xác định đúng đoạn bằng chứng ở 87,8 % số mẫu và chính xác hơn cắt bỏ ngữ cảnh; khi "
    "thay câu bằng chứng, bốn đặc trưng thay đổi đúng hướng ở 71–75 % số cặp. H5 bị bác bỏ ở bài "
    "toán ba lớp, nhưng quyết định nhị phân vẫn chuyển giao được."
    + OP
    + "rê chuột để xem thí nghiệm tương ứng.",
    "done": "Tóm lại, nhóm em đã xây dựng bộ phát hiện ba lớp từ tín hiệu chú ý, tương đương bộ mã "
    "hóa tinh chỉnh với vài trăm tham số, và lặp lại kết quả trên bộ tin tức ViFactCheck; kiểm chứng "
    "trực tiếp cơ chế, kể cả khi so sánh với phương pháp cắt bỏ ngữ cảnh; đo đầy đủ chi phí; và tổng "
    "hợp thành hệ thống vận hành được trên hệ RAG. Các hạn chế: đặc trưng hình dạng không làm tăng "
    "điểm phân loại, kể cả trên ViFactCheck; bộ phân loại ba lớp không chuyển giao được sang bộ dữ "
    "liệu khác; và chi phí biên trong hệ RAG tự giám sát chưa được đo. Nhóm đã thử chấm theo từng "
    "câu (E18) nhưng không cho kết quả cao hơn; hướng phát triển tiếp theo là chấm theo từng đoạn "
    "của câu trả lời, với dữ liệu có nhãn ở mức đoạn.",
}
NOTE_RE = re.compile(r'data-notes="[^"]*"')
for key, text in NOTES.items():
    k = IDX[key]
    assert len(NOTE_RE.findall(S[k])) == 1, key
    S[k] = NOTE_RE.sub(lambda _m, t=text: f'data-notes="{html.escape(t)}"', S[k], count=1)

# ---------------------------------------------------------------------------------------------
# 3. On-slide HTML text (terms boxes, footers, text slides)
# ---------------------------------------------------------------------------------------------
HTML_SUBS = {
    "types": [
        (
            "<b>Ảo giác nội tại</b> — có dựa vào tài liệu nhưng nói sai so với nó. <b>Ảo giác ngoại "
            "lai</b> — nói điều tài liệu không hề có.",
            "<b>Ảo giác nội tại</b> — nội dung dựa trên ngữ cảnh nhưng mâu thuẫn với ngữ cảnh. "
            "<b>Ảo giác ngoại lai</b> — thông tin không có trong ngữ cảnh.",
        ),
    ],
    "lb": [
        (
            "<b>Tỷ lệ nhìn lại (lookback ratio)</b> — phần chú ý dành cho ngữ cảnh chia cho tổng chú "
            "ý dành cho ngữ cảnh và cho phần câu trả lời đã viết.",
            "<b>Tỷ lệ lookback (lookback ratio)</b> — phần chú ý dành cho ngữ cảnh chia cho tổng chú "
            "ý dành cho ngữ cảnh và cho phần câu trả lời đứng trước.",
        ),
    ],
    "chunk": [
        (
            "<b>Chunk-aware</b> — cộng chú ý theo từng đoạn để thấy hình dạng của nó.",
            "<b>Chunk-aware</b> — cộng chú ý theo từng đoạn để mô tả hình dạng phân bố chú ý.",
        ),
    ],
    "pipe": [
        (
            "đưa sẵn câu trả lời cho mô hình đọc, thay vì để nó tự sinh; nhờ vậy chấm được câu trả "
            "lời của bất kỳ ai.",
            "đưa câu trả lời có sẵn vào mô hình đọc thay vì để mô hình tự sinh; nhờ vậy đánh giá "
            "được câu trả lời của bất kỳ hệ thống nào.",
        ),
    ],
    "hook": [
        (
            "một hàm nhỏ gắn vào mỗi lớp của mô hình, tự chạy ngay khi lớp đó tính xong.",
            "một hàm gắn vào từng lớp của mô hình, tự động thực thi ngay khi lớp đó tính xong.",
        ),
    ],
    "demo": [
        (
            "1 trừ xác suất câu trả lời trung thực; càng gần 1 càng đáng ngờ.",
            "1 trừ xác suất câu trả lời trung thực; càng gần 1, khả năng có ảo giác càng cao.",
        ),
        (
            "Dữ liệu thật, Kaggle T4, 11/09/2026",
            "Dữ liệu thực tế, GPU Tesla T4 trên Kaggle, 11/09/2026",
        ),
    ],
    "res": [
        (
            "trung bình cộng điểm F1 của ba lớp; đoán bừa được khoảng 0,33.",
            "trung bình cộng điểm F1 của ba lớp; mức ngẫu nhiên khoảng 0,33.",
        ),
        (
            "vùng điểm có thể dao động nếu đổi tập kiểm tra.",
            "khoảng giá trị mà điểm số có thể dao động khi đổi tập kiểm tra.",
        ),
    ],
    "loc": [
        (
            "Bảng 6.3 và 6.7 · 2.376 mẫu ISE-DSC01 · tranh luận “chú ý có phải lời giải thích”: Jain "
            "và Wallace (2019); Wiegreffe và Pinter (2019)",
            "Bảng 6.3, 6.7, 6.17 · 2.376 mẫu ISE-DSC01, 300 mẫu ViWikiFC (E19) · ARC-JSD: Li và cộng "
            "sự (2026) · Jain và Wallace (2019); Wiegreffe và Pinter (2019)",
        ),
    ],
    "null": [
        (
            "chênh lệch nhỏ hơn mức dao động tự nhiên của điểm số thì không thể kết luận là hơn hay "
            "kém.",
            "khi chênh lệch nhỏ hơn mức dao động tự nhiên của điểm số, không thể kết luận phương pháp "
            "nào tốt hơn.",
        ),
        ("Bảng 6.2, 6.8, 6.9, 6.10, 6.12 ·", "Bảng 6.2, 6.8, 6.9, 6.10, 6.12, 6.18 ·"),
    ],
    "cost": [
        ("mô hình càng nhỏ càng nhẹ.", "mô hình càng nhỏ càng sử dụng ít bộ nhớ."),
    ],
    "gaps": [
        ("Chưa ai tách tỷ lệ chú ý", "Chưa có công trình tách tỷ lệ chú ý"),
        ("Chưa ai đặt ba hướng tiếp cận", "Chưa có công trình đặt ba hướng tiếp cận"),
        (
            "nên không biết mô hình nhìn đúng đoạn hay nhìn dàn trải.",
            "nên không xác định được chú ý tập trung vào đúng đoạn hay phân bố dàn trải.",
        ),
        (
            "so với tỷ lệ gộp — và mô hình có thật sự nhìn vào đúng chỗ?",
            "so với tỷ lệ gộp — và chú ý có tập trung vào đúng đoạn chứa bằng chứng?",
        ),
        # pointers: res..null are slides 21–24, costs is 6, cost is 25, xfer is 26
        ("Trả lời ở slide 14–17", "Trả lời ở slide 21–24"),
        ("Trả lời ở slide 4 và 18", "Trả lời ở slide 6 và 25"),
        ("Trả lời ở slide 17 và 19", "Trả lời ở slide 24 và 26"),
    ],
    "done": [
        (
            '<h3 style="color:var(--ok)">Đã làm được</h3>',
            '<h3 style="color:var(--ok)">Kết quả đạt được</h3>',
        ),
        (
            '<h3 style="color:var(--bad)">Chưa làm được</h3>',
            '<h3 style="color:var(--bad)">Hạn chế</h3>',
        ),
        (
            "<b>0,757</b>, ngang bộ mã hóa tinh chỉnh",
            "<b>0,757</b>, tương đương bộ mã hóa tinh chỉnh",
        ),
        (
            "Kiểm chứng trực tiếp cơ chế: nhìn đúng đoạn bằng chứng <b>87,8 %</b>, lặp lại trên bộ "
            "thứ hai, can thiệp đúng 4/4 hướng.",
            "Kiểm chứng trực tiếp cơ chế: định vị đúng đoạn bằng chứng <b>87,8 %</b>, chính xác hơn "
            "cắt bỏ ngữ cảnh (<b>0,850</b> so với 0,733); can thiệp đúng 4/4 hướng.",
        ),
        (
            "Hệ thống hoàn chỉnh: thư viện, REST, Docker, giao diện; chạy thật bắt được ảo giác.",
            "Hệ thống hoàn chỉnh: thư viện, REST, Docker, giao diện; vận hành trên hệ RAG.",
        ),
        (
            "Bộ phát hiện ba lớp không dùng được chéo bộ; chỉ quyết định nhị phân chuyển được.",
            "Bộ phát hiện ba lớp không khái quát hóa sang bộ dữ liệu khác; chỉ quyết định nhị phân "
            "chuyển giao được.",
        ),
        (
            "Chi phí biên trong hệ RAG tự giám sát chưa đo:",
            "Chi phí biên trong hệ RAG tự giám sát chưa được đo:",
        ),
        ("Docker chưa kiểm trên máy có GPU.", "Ảnh Docker chưa được kiểm thử trên máy có GPU."),
        (
            "chấm theo từng câu đã thử (E18), không hơn.",
            "chấm theo từng câu (E18) đã thử, không cho kết quả cao hơn.",
        ),
    ],
}
for key, pairs in HTML_SUBS.items():
    for old, new in pairs:
        S[IDX[key]] = sub(S[IDX[key]], old, new, where=key)

# ---------------------------------------------------------------------------------------------
# 3b. Less text: icons, shorter terms, the gaps and results slides as icon cards, short references
# ---------------------------------------------------------------------------------------------
# One stroke-icon set (24 × 24 grid, drawn here, no external library), coloured by the slide tokens.
ICONS = {
    "intro": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    "theory": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5"/><path d="M8 7h7M8 11h7"/>',
    "data": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "method": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 10.5h8M8 18.5h5"/><rect x="7" y="13" width="10" height="3" rx="1" fill="currentColor"/>',
    "system": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 12.5l9 5 9-5"/><path d="M3 17l9 5 9-5"/>',
    "results": '<path d="M3 21h18"/><rect x="5" y="11" width="3" height="7"/><rect x="10.5" y="6" width="3" height="12"/><rect x="16" y="13" width="3" height="5"/>',
    "conclusion": '<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>',
    "locate": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/><path d="M7.5 12.5v-2M10.5 12.5v-4.5M13.5 12.5v-1"/>',
    "scale": '<path d="M12 4v16M7 20h10M5 7h14"/><path d="M5 7l-3 6a3 3 0 0 0 6 0z"/><path d="M19 7l-3 6a3 3 0 0 0 6 0z"/>',
    "lang": '<path d="M4 4h16v11H9l-5 4z"/><path d="M8 7.5l2 4.5 2-4.5"/><path d="M15 9v3M15 7.2v.1"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.7 2.7L16 9.8"/>',
    "alert": '<path d="M12 3l9.5 17h-19z"/><path d="M12 10v4.5M12 17.2v.1"/>',
    "next": '<circle cx="12" cy="12" r="9"/><path d="M8 12h8M13 8.5l3.5 3.5-3.5 3.5"/>',
    "noapi": '<path d="M7 18h10a4 4 0 0 0 .5-8 6 6 0 0 0-11.4 1.6A3.3 3.3 0 0 0 7 18z"/><path d="M3 3l18 18"/>',
    "frozen": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "gpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
}


def icon(name: str, cls: str = "ic") -> str:
    """One stroke icon as inline SVG; its colour follows the surrounding text colour."""
    return (
        f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f"{ICONS[name]}</svg>"
    )


# Terms: one short line each (the full definitions stay in the notes and in the thesis)
TERMS = {
    "types": "<b>Nội tại</b> — mâu thuẫn với ngữ cảnh. <b>Ngoại lai</b> — thông tin không có trong ngữ cảnh.",
    "lb": "<b>Tỷ lệ lookback</b> — phần chú ý dành cho ngữ cảnh so với phần dành cho câu trả lời đứng trước.",
    "data": "<b>Chia theo ngữ cảnh</b> — các câu trả lời cùng một tài liệu nằm chung một tập.",
    "chunk": "<b>Đoạn</b> — một câu của ngữ cảnh. <b>Chunk-aware</b> — chú ý tính theo từng đoạn.",
    "pipe": "<b>Teacher forcing</b> — đưa câu trả lời có sẵn cho mô hình đọc, không để mô hình tự sinh.",
    "hook": "<b>Forward hook</b> — hàm tự chạy ngay khi một lớp của mô hình tính xong.",
    "demo": "<b>Điểm rủi ro</b> — 1 trừ xác suất trung thực; càng gần 1 càng có khả năng ảo giác.",
    "res": "<b>macro-F1</b> — trung bình F1 ba lớp, ngẫu nhiên ≈ 0,33. <b>KTC 95 %</b> — khoảng dao động khi đổi tập kiểm tra.",
    "loc": "<b>Đầu chú ý</b> — một phép chú ý song song trong một lớp; xét đủ 27 × 28 = 756 đầu.",
    "iv": "<b>Thí nghiệm can thiệp</b> — chỉ thay đúng một yếu tố rồi đo lại.",
    "null": "<b>Vùng nhiễu</b> — chênh lệch nhỏ hơn mức dao động tự nhiên, không kết luận được hơn kém.",
    "cost": "<b>7B, 3B, 1.5B</b> — số tỷ tham số của mô hình đọc.",
    "xfer": "<b>Chéo bộ</b> — huấn luyện trên bộ này, kiểm tra trên bộ kia.",
}
TERMS_RE = re.compile(r'(<p class="terms"><span class="tag">Thuật ngữ</span>).*?(</p>)', re.S)
for key, text in TERMS.items():
    k = IDX[key]
    assert len(TERMS_RE.findall(S[k])) == 1, key
    S[k] = TERMS_RE.sub(lambda m, t=text: m.group(1) + t + m.group(2), S[k], count=1)

# Slide 7: three icon columns, gap → question → where it is answered (details stay in the notes)
GAPS = [
    (
        "locate",
        "var(--ctx)",
        "Khoảng trống 1",
        "Chưa tách chú ý theo <em>từng đoạn</em>, chưa đối chiếu với vị trí bằng chứng",
        "Câu hỏi 1 · Tín hiệu",
        "Chú ý theo đoạn có cải thiện phát hiện và có tập trung đúng đoạn bằng chứng?",
        "slide 21–24",
    ),
    (
        "scale",
        "var(--res)",
        "Khoảng trống 2",
        "Ba hướng tiếp cận chưa được so trên <em>cùng thang</em> độ chính xác – chi phí",
        "Câu hỏi 2 · Chi phí",
        "So với LLM giám khảo và bộ mã hóa, độ chính xác và chi phí ra sao?",
        "slide 6 và 25",
    ),
    (
        "lang",
        "#6B4FA0",
        "Khoảng trống 3",
        "Chưa có công trình dùng tín hiệu nội tại cho ảo giác <em>tiếng Việt</em>",
        "Câu hỏi 3 · Chuyển giao",
        "Chú ý thêm được bao nhiêu so với bề mặt, có dùng được trên bộ khác?",
        "slide 24 và 26",
    ),
]
gap_html = (
    '<div class="gq3">'
    + "".join(
        f'<div class="gcol rise r{n + 1}" style="--c:{c}"><div class="gtop">{icon(ic)}<div class="k">{k}</div>'
        f'<div class="s">{gs}</div></div><div class="gar">↓</div><div class="qc"><div class="k">{qk}</div>'
        f'<div class="q">{q}</div><div class="a">Trả lời ở {a}</div></div></div>'
        for n, (ic, c, k, gs, qk, q, a) in enumerate(GAPS)
    )
    + "</div>\n  "
)
g = IDX["gaps"]
a_, b_ = S[g].index('<div class="gq">'), S[g].index('<div class="foot">')
S[g] = S[g][:a_] + gap_html + S[g][b_:]

# Slide 29: big numbers with short labels; limitations and next steps as one-line items
DONE = [
    (
        "check",
        "var(--ok)",
        "Kết quả đạt được",
        [
            ("0,757", "macro-F1 ba lớp, 579 tham số — tương đương PhoBERT"),
            ("87,8 %", "định vị đúng đoạn bằng chứng; hơn cắt bỏ ngữ cảnh"),
            ("0,703", "lặp lại trên bộ tin tức ViFactCheck"),
            ("195", "tham số với mô hình đọc 3B — điểm cân bằng"),
            ("825", "ca kiểm thử; thư viện, REST, Docker, giao diện"),
        ],
    ),
    (
        "alert",
        "var(--bad)",
        "Hạn chế",
        [
            ("", "Đặc trưng hình dạng không tăng điểm phân loại"),
            ("", "Ba lớp không khái quát sang bộ khác; nhị phân thì được"),
            ("", "Chưa đo chi phí biên khi một mô hình vừa sinh vừa đọc"),
            ("", "Docker chưa được kiểm thử trên máy có GPU"),
        ],
    ),
    (
        "next",
        "var(--ctx)",
        "Hướng phát triển",
        [
            ("", "Chấm theo từng đoạn câu trả lời, với nhãn mức đoạn"),
            ("", "Kết hợp chú ý (mạnh ở nội tại) với bộ mã hóa (mạnh ở ngoại lai)"),
            ("", "Đo chi phí biên trên GPU có bfloat16 gốc"),
            ("", "Chỉ tính hàng chú ý của phản hồi để đọc ngữ cảnh dài hơn"),
        ],
    ),
]
done_html = (
    '<div class="res3">'
    + "".join(
        f'<div class="rcol rise r{n + 1}" style="--c:{c}"><h3>{icon(ic)}{title}</h3><ul>'
        + "".join(
            f'<li class="{"num" if v else "line"}">'
            + (f'<span class="v">{v}</span>' if v else "")
            + f"<span>{t}</span></li>"
            for v, t in items
        )
        + "</ul></div>"
        for n, (ic, c, title, items) in enumerate(DONE)
    )
    + "</div>\n  "
)
d = IDX["done"]
a_, b_ = S[d].index('<div class="three">'), S[d].index('<div class="foot">')
S[d] = S[d][:a_] + done_html + S[d][b_:]

# Slide 30: short references (author, year, title, venue); numbers follow the thesis list
REFS_SHORT = [
    (
        "Phương pháp nền và đối chiếu",
        [
            (3, "Chuang và cộng sự (2024). Lookback Lens. <i>EMNLP 2024</i>."),
            (32, "Vaswani và cộng sự (2017). Attention Is All You Need. <i>NeurIPS</i>."),
            (27, "Sun và cộng sự (2025). ReDeEP. <i>ICLR 2025</i>."),
            (4, "Cohen-Wang và cộng sự (2024). ContextCite. <i>NeurIPS 37</i>."),
            (18, "Li và cộng sự (2026). ARC-JSD. <i>ICLR 2026</i>."),
        ],
    ),
    (
        "Dữ liệu",
        [
            (22, "Nguyen và cộng sự (2026). DSC2025 – ViHallu Challenge. <i>arXiv:2601.04711</i>."),
            (31, "UIT Data Science Challenge 2023 (bộ ISE-DSC01)."),
            (16, "Le và cộng sự (2024). ViWikiFC. <i>arXiv:2405.07615</i>."),
        ],
    ),
    (
        "Mốc so sánh",
        [
            (23, "Nguyen và Nguyen (2020). PhoBERT. <i>Findings of EMNLP 2020</i>."),
            (5, "Conneau và cộng sự (2020). XLM-R. <i>ACL 2020</i>."),
            (36, "Zheng và cộng sự (2023). LLM-as-a-Judge. <i>NeurIPS 36</i>."),
            (29, "Tran và cộng sự (2025). SemViQA. <i>arXiv:2503.00955</i>."),
        ],
    ),
    (
        "Mô hình và nền tảng",
        [
            (25, "Qwen Team (2024). Qwen2.5 Technical Report. <i>arXiv:2412.15115</i>."),
            (17, "Lewis và cộng sự (2020). Retrieval-Augmented Generation. <i>NeurIPS 33</i>."),
            (
                13,
                "Ji và cộng sự (2023). Survey of Hallucination in NLG. <i>ACM Computing Surveys</i>.",
            ),
        ],
    ),
]
refs_html = (
    '<div class="refs">'
    + "".join(
        f'<div class="grp rise r{k + 1}"><h3>{name}</h3><ul>'
        + "".join(f'<li><span class="rn">[{n}]</span>{t}</li>' for n, t in items)
        + "</ul></div>"
        for k, (name, items) in enumerate(REFS_SHORT)
    )
    + "</div>"
)
r = IDX["refs"]
S[r] = re.sub(
    r'<div class="refs">.*?</ul></div></div>', lambda _m: refs_html, S[r], count=1, flags=re.S
)
assert "Cohen-Wang" in S[r], "refs block not replaced"

# ---------------------------------------------------------------------------------------------
# 4. Figure labels and step captions (the drawing code after the last slide)
# ---------------------------------------------------------------------------------------------
JS_SUBS = [
    # 02 · two hallucination types
    (
        "'Có dựa vào câu 2 và câu 3 — nhưng nói sai'",
        "'Dựa vào câu 2 và câu 3 nhưng mâu thuẫn với ngữ cảnh'",
    ),
    ("'Không câu nào trong tài liệu nói vậy'", "'Không có căn cứ trong tài liệu'"),
    ('data-t="Tài liệu nói <b>triều Lý</b>"', 'data-t="Tài liệu ghi <b>triều Lý</b>"'),
    (
        'data-t="Tài liệu nói <b>khoảng tám triệu</b>"',
        'data-t="Tài liệu ghi <b>khoảng tám triệu</b>"',
    ),
    (
        'data-t="Không câu nào trong tài liệu nói điều này"',
        'data-t="Không câu nào trong tài liệu đề cập nội dung này"',
        2,
    ),
    (
        "Tài liệu nói Hà Nội từng mang tên Thăng Long",
        "Tài liệu ghi Hà Nội từng mang tên Thăng Long",
    ),
    (
        "cũng dựa vào câu 2 và câu 3 — nhưng nói sai:",
        "cũng dựa vào câu 2 và câu 3 nhưng mâu thuẫn với ngữ cảnh:",
    ),
    (
        "nói về tháp Eiffel và tàu điện ngầm — <b>không câu nào</b> trong tài liệu nói vậy.",
        "đề cập tháp Eiffel và tàu điện ngầm — thông tin <b>không có</b> trong tài liệu.",
    ),
    ("Hệ thống của đề tài chấm rủi ro cho ba câu:", "Điểm rủi ro hệ thống gán cho ba câu:"),
    (
        "Bài toán là tách được cả ba loại, không chỉ đúng hay sai.",
        "Bài toán là phân loại ba lớp, không chỉ phân biệt đúng và sai.",
    ),
    # 04 · motivation
    ("'Hỏi một LLM khác làm giám khảo'", "'Dùng một LLM khác làm giám khảo'"),
    (
        "<b>Hỏi một LLM khác làm giám khảo</b>: mỗi câu trả lời phải gửi lên máy chủ bên ngoài và chờ "
        "hơn 8 giây.",
        "<b>Dùng một LLM khác làm giám khảo</b>: mỗi câu trả lời phải gửi lên máy chủ bên ngoài, độ "
        "trễ hơn 8 giây.",
    ),
    ("'macro-F1 0,656 — yếu'", "'macro-F1 0,656 — thấp nhất'"),
    ("'Không đọc được ý nghĩa'", "'Không nắm được ngữ nghĩa'"),
    ("'Chỉ 9 tham số, chạy tức thì'", "'Chỉ 9 tham số, xử lý gần như tức thời'"),
    (
        "dùng chú ý — thứ đã có sẵn khi mô hình đọc. Không giám khảo, không tinh chỉnh mô hình lớn, dữ "
        "liệu không rời máy.",
        "dùng trọng số chú ý, vốn có sẵn khi mô hình đọc. Không dùng giám khảo, không tinh chỉnh mô "
        "hình lớn, dữ liệu không rời khỏi hệ thống.",
    ),
    (
        "<b>Đặc trưng bề mặt</b>: rẻ, nhưng chỉ đếm độ dài và số từ trùng — không biết câu trả lời có "
        "nói đúng không.",
        "<b>Đặc trưng bề mặt</b>: chi phí thấp, nhưng chỉ đếm độ dài và số từ trùng — không đánh giá "
        "được nội dung câu trả lời.",
    ),
    (
        "không tinh chỉnh mô hình lớn, dữ liệu không rời khỏi máy.",
        "không tinh chỉnh mô hình lớn, dữ liệu không rời khỏi hệ thống.",
    ),
    # 07 · Lookback Lens
    ("tỷ lệ nhìn lại", "tỷ lệ lookback", 6),
    ("'phần câu trả lời đã viết'", "'câu trả lời đứng trước'"),
    ("'trung bình mỗi token đã viết'", "'trung bình mỗi token đứng trước'"),
    (
        "Chú ý của nó chia hai phía: về <b>ngữ cảnh</b> (lam) và về <b>phần câu trả lời đã viết</b> "
        "trước đó (cam).",
        "Chú ý của token này chia thành hai phần: dành cho <b>ngữ cảnh</b> (lam) và dành cho <b>phần "
        "câu trả lời đứng trước</b> (cam).",
    ),
    ("Lấy trung bình mỗi phía rồi so:", "Lấy trung bình mỗi phần rồi so sánh:"),
    (
        "Tỷ lệ càng cao, mô hình càng bám tài liệu.",
        "Tỷ lệ càng cao, mô hình càng dựa vào ngữ cảnh.",
    ),
    (
        "'các tỷ lệ này — theo bài gốc, ngang bộ phân loại'",
        "'các tỷ lệ này — theo bài gốc, tương đương bộ phân loại'",
    ),
    ("27 lớp × 28 đầu = <b>756 con số</b>.", "27 lớp × 28 đầu = <b>756 giá trị</b>."),
    (
        "đọc 756 con số đó để đoán câu trả lời có ảo giác hay không.",
        "nhận 756 giá trị đó làm đầu vào để dự đoán câu trả lời có ảo giác hay không.",
    ),
    # 09 · chunk-aware
    ("'B · ngoại lai (bịa)'", "'B · ngoại lai'"),
    ("'Lookback Lens · tỷ lệ nhìn ngữ cảnh'", "'Lookback Lens · tỷ lệ chú ý vào ngữ cảnh'"),
    ("'rải đều — tản'", "'phân bố đều'"),
    ("'dồn một chỗ — nhọn'", "'tập trung một đoạn'"),
    ("câu B nói điều ngữ cảnh không hề có.", "câu B chứa thông tin không có trong ngữ cảnh."),
    (
        "<b>Lookback Lens</b> gộp tất cả thành một con số: phần chú ý dành cho ngữ cảnh.",
        "<b>Lookback Lens</b> tổng hợp tất cả thành một giá trị: phần chú ý dành cho ngữ cảnh.",
    ),
    (
        "một con số không phân biệt được hai cách nhìn này.",
        "một giá trị không phân biệt được hai cách phân bổ chú ý này.",
    ),
    (
        "A dồn 71 % vào câu 3 — câu chứa thông tin nó dùng. B rải đều, vì không có câu nào để dựa vào.",
        "A tập trung 71 % vào câu 3 — câu chứa thông tin được sử dụng. B phân bố đều, vì không có câu "
        "nào làm căn cứ.",
    ),
    (
        "Hình dạng được đo bằng con số: <b>entropy</b> (0 là dồn một chỗ, 1 là rải đều)",
        "Hình dạng phân bố được định lượng bằng <b>entropy</b> (0 là tập trung hoàn toàn, 1 là phân bố "
        "đều)",
    ),
    # 08 · data
    ("Bẫy đã đo trước khi dùng:", "Rò rỉ được phát hiện trước khi sử dụng:"),
    (
        "(vạch đỏ): mô hình được “xem trước đề”.",
        "(vạch đỏ): rò rỉ dữ liệu giữa tập huấn luyện và tập kiểm tra.",
    ),
    # 10 · pipeline
    ("'192 con số'", "'192 đặc trưng'"),
    ("32 đầu → 192 con số", "32 đầu → 192 đặc trưng"),
    (
        "mỗi đầu cho 6 con số: tỷ lệ lookback và 5 đặc trưng hình dạng",
        "mỗi đầu cho 6 giá trị: tỷ lệ lookback và 5 đặc trưng hình dạng",
    ),
    (
        "579 tham số đổi 192 con số thành ba xác suất. Câu về Hồ Hoàn Kiếm có cụm “trở về dinh thự” "
        "tự bịa:",
        "579 tham số chuyển 192 đặc trưng thành ba xác suất. Câu trả lời về Hồ Hoàn Kiếm có cụm “trở "
        "về dinh thự” không có căn cứ:",
    ),
    (
        "rồi bỏ ma trận; lớp cuối tràn số ở float16 nên bị bỏ.",
        "rồi giải phóng ma trận; lớp cuối tràn số ở float16 nên bị loại.",
    ),
    ("cộng theo câu ngữ cảnh rồi xóa ma trận", "cộng theo câu ngữ cảnh rồi giải phóng ma trận"),
    ("'lớp 27: bỏ'", "'lớp 27: loại'"),
    ("nên không gắn hook, bỏ khỏi đặc trưng", "nên không gắn hook, loại khỏi đặc trưng"),
    # 11 · forward hook
    ("→ <b>xóa ma trận</b>. Bộ nhớ không tăng.", "→ <b>giải phóng ma trận</b>. Bộ nhớ không tăng."),
    ("'xóa ngay khi tính xong'", "'giải phóng ngay khi tính xong'"),
    ("đã vượt 16 GB của card T4;", "đã vượt 16 GB của GPU T4;"),
    (
        "— chỉ còn vài chục con số — rồi xóa ngay ma trận. Lúc nào cũng chỉ có một ma trận trong bộ nhớ.",
        "— chỉ còn vài chục giá trị — rồi giải phóng ma trận ngay. Tại mỗi thời điểm, bộ nhớ chỉ chứa "
        "một ma trận.",
    ),
    (
        "— mô hình 7B chạy trọn trong một card 16 GB miễn phí của Kaggle.",
        "— mô hình 7B vận hành trọn vẹn trên một GPU 16 GB miễn phí của Kaggle.",
    ),
    # 14 · main result
    (
        "khoảng 0,66. Đoán bừa ba lớp được khoảng 0,33.",
        "khoảng 0,66. Mức ngẫu nhiên với ba lớp là khoảng 0,33.",
    ),
    (
        "nên kết luận là <b>ngang</b>, không phải hơn.",
        "nên kết luận là <b>tương đương</b>, không khẳng định cao hơn.",
    ),
    # 15 · localisation
    ("'Chọn bừa một đoạn'", "'Chọn ngẫu nhiên một đoạn'"),
    ("'chọn bừa'", "'ngẫu nhiên'"),
    ("'Tỷ lệ trúng đoạn bằng chứng'", "'Tỷ lệ xác định đúng đoạn bằng chứng'"),
    ("'trúng ✓' : 'trượt ✗'", "'đúng ✓' : 'sai ✗'"),
    (
        "Với mỗi mẫu, xem đầu chú ý mạnh nhất nhìn đoạn nào nhiều nhất. Trùng đoạn bằng chứng là "
        "<b>trúng</b>, lệch là <b>trượt</b>.",
        "Với mỗi mẫu, xác định đoạn mà đầu chú ý mạnh nhất phân bổ chú ý nhiều nhất. Trùng đoạn bằng "
        "chứng là <b>đúng</b>, khác là <b>sai</b>.",
    ),
    (
        "Trên 2.376 mẫu, đầu mạnh nhất trúng <b>87,8 %</b>. Chọn bừa một đoạn chỉ trúng 6,1 % — kém "
        "<b>14,3 lần</b>.",
        "Trên 2.376 mẫu, đầu mạnh nhất xác định đúng <b>87,8 %</b>; chọn ngẫu nhiên một đoạn chỉ đạt "
        "6,1 % — thấp hơn <b>14,3 lần</b>.",
    ),
    (
        "Khả năng nhìn đúng chỗ thuộc về mô hình, không phụ thuộc bộ dữ liệu.",
        "Khả năng định vị thuộc về mô hình, không phụ thuộc bộ dữ liệu.",
    ),
    # 16 · intervention
    ("'tản ra'", "'phân tán hơn'"),
    ("'bớt dồn'", "'giảm tập trung'"),
    (
        "Chú ý của mô hình dồn vào đó: một đỉnh rõ, entropy thấp.",
        "Chú ý của mô hình tập trung vào câu đó: một đỉnh rõ, entropy thấp.",
    ),
    ("Đỉnh biến mất, chú ý rải đều hơn.", "Đỉnh biến mất, chú ý phân bố đều hơn."),
    ("cao hơn hẳn mức ngẫu nhiên 50 %.", "cao hơn rõ rệt mức ngẫu nhiên 50 %."),
    (
        "nên đây không phải giải thích sau khi đã thấy số.",
        "nên đây không phải giải thích sau khi đã biết kết quả.",
    ),
    # 17 · shape features
    (
        "Nhóm báo cáo thẳng kết quả âm này thay vì chọn con số đẹp.",
        "Nhóm trình bày đầy đủ kết quả không ủng hộ giả thuyết này.",
    ),
    (
        "Đo lại năm lần nữa — thêm đặc trưng, đổi mô hình, đổi cỡ, đổi bộ dữ liệu.",
        "Đo lại thêm năm lần — thêm đặc trưng, đổi mô hình, đổi kích thước, đổi bộ dữ liệu.",
    ),
    (
        "chunk-aware hơn Lookback Lens <b>+0,012</b>. Nhưng điểm số tự dao động",
        "chunk-aware cao hơn Lookback Lens <b>+0,012</b>. Tuy nhiên, điểm số dao động",
    ),
    (
        "Nằm trong vùng nhiễu — không kết luận hơn kém.",
        "Nằm trong vùng nhiễu — không kết luận được chênh lệch.",
    ),
    ("'đổi cỡ mô hình'", "'đổi kích thước mô hình'"),
    ("'đổi cỡ mô hình, chạy bfloat16'", "'đổi kích thước mô hình, chạy bfloat16'"),
    ("'E14 · thu xuống 3B'", "'E14 · thu nhỏ xuống 3B'"),
    ("'E14 · thu xuống 1.5B'", "'E14 · thu nhỏ xuống 1.5B'"),
    # 18 · cost
    (
        "Bốn mốc so sánh. Bề mặt rẻ nhưng kém;",
        "Bốn mốc so sánh. Đặc trưng bề mặt có chi phí thấp nhưng độ chính xác thấp;",
    ),
    ("độ chính xác ngang PhoBERT — chậm hơn,", "độ chính xác tương đương PhoBERT — chậm hơn,"),
    (
        "Thu xuống <b>3B</b>: nhanh gấp đôi, chỉ mất 0,01 điểm — điểm cân bằng.",
        "Thu nhỏ xuống <b>3B</b>: nhanh gấp đôi, macro-F1 chỉ giảm 0,01 — điểm cân bằng.",
    ),
    (
        "'cỡ chấm ∝ log số tham số phải huấn luyện'",
        "'kích thước chấm ∝ log số tham số phải huấn luyện'",
    ),
    ("T4 không hỗ trợ sẵn, chậm", "T4 không hỗ trợ ở mức phần cứng, chậm"),
    # 19 · transfer
    ("'mô hình đoán'", "'nhãn dự đoán'"),
    ("'đoán bừa 3 lớp'", "'mức ngẫu nhiên 3 lớp'"),
    ("'đoán bừa 2 lớp'", "'mức ngẫu nhiên 2 lớp'"),
    ("</b> bị đoán là <b>", "</b> được dự đoán là <b>"),
    (
        "chỉ <b>66</b> câu được đoán đúng; <b>988 câu</b> bị gọi thành nội tại.",
        "chỉ <b>66</b> câu được phân loại đúng; <b>988 câu</b> bị phân loại thành nội tại.",
    ),
    (
        "Điểm ba lớp rơi về gần mức đoán bừa (<b>0,358</b>). Nhưng chỉ hỏi “có ảo giác hay không” thì "
        "vẫn được <b>0,664</b>, trên mức ngẫu nhiên 0,5.",
        "Macro-F1 ba lớp giảm còn <b>0,358</b>, gần mức ngẫu nhiên. Với câu hỏi nhị phân “có ảo giác "
        "hay không”, kết quả vẫn đạt <b>0,664</b>, trên mức ngẫu nhiên 0,5.",
    ),
    ("136 câu bị gọi thành ngoại lai.", "136 câu bị phân loại thành ngoại lai."),
    (
        "nội dung GPT-4o <b>tự thêm vào</b> câu trả lời.",
        "nội dung GPT-4o <b>bổ sung</b> vào câu trả lời.",
    ),
    # 12 · system
    ("hoặc chạy cả gói bằng <b>Docker</b>", "hoặc triển khai toàn bộ bằng <b>Docker</b>"),
    # 13 · demo
    ("Câu hỏi thật: hệ thống tìm ba tài liệu", "Câu hỏi thực tế: hệ thống truy xuất ba tài liệu"),
    (
        "chú ý dồn nhiều nhất vào câu về Hồ Hoàn Kiếm — đúng câu có thông tin.",
        "chú ý tập trung nhiều nhất vào câu về Hồ Hoàn Kiếm — đúng câu chứa thông tin.",
    ),
    (
        "nhưng tự thêm “<b>sau đó anh ta đã trở về dinh thự</b>” — tài liệu không hề có.",
        "nhưng bổ sung “<b>sau đó anh ta đã trở về dinh thự</b>” — thông tin không có trong tài liệu.",
    ),
    (
        "Bộ phát hiện tự chấm: <b>ngoại lai</b>, rủi ro <b>0,997</b>. Không ai viết sẵn câu trả lời — "
        "mô hình tự bịa, hệ thống tự bắt.",
        "Bộ phát hiện gán nhãn <b>ngoại lai</b>, rủi ro <b>0,997</b>. Câu trả lời không được soạn sẵn: "
        "mệnh đề không có căn cứ do mô hình tự sinh và được phát hiện tự động.",
    ),
    # 03 · problem statement
    ("'có dựa vào ngữ cảnh nhưng nói sai'", "'dựa vào ngữ cảnh nhưng mâu thuẫn'"),
    ("'thêm điều ngữ cảnh không có'", "'thông tin không có trong ngữ cảnh'"),
    ("'Vừa một GPU T4 16 GB'", "'Chạy trên một GPU T4 16 GB'"),
    ("Đầu vào gồm ba thứ:", "Đầu vào gồm ba thành phần:"),
    (
        "chạy vừa một card 16 GB, làm cho tiếng Việt với ba lớp nhãn.",
        "chạy trên một GPU 16 GB, xử lý tiếng Việt với ba lớp nhãn.",
    ),
    (
        "— cho biết câu trả lời dựa vào đâu.",
        "— cho biết câu trả lời dựa vào phần nào của ngữ cảnh.",
    ),
    # 06 · map of approaches
    (
        "'Chỉ nắm được mẫu hình thô, dễ bị lừa khi câu sai chép nhiều từ'",
        "'Chỉ nắm được mẫu hình thô, sai lệch khi câu trả lời sai lặp lại nhiều từ của ngữ cảnh'",
    ),
    (
        "'Tốn nhiều lượt sinh; nhắm tới tính xác thực hơn là bám ngữ cảnh'",
        "'Cần nhiều lượt sinh; nhắm tới tính xác thực hơn là mức độ dựa trên ngữ cảnh'",
    ),
    ("đặc trưng bề mặt rất rẻ nhưng thô;", "đặc trưng bề mặt có chi phí rất thấp nhưng thô;"),
    # 20 · hypotheses
    (
        "'Lookback gộp vượt đặc trưng bề mặt, ngang bộ mã hóa tinh chỉnh'",
        "'Lookback gộp vượt đặc trưng bề mặt, tương đương bộ mã hóa tinh chỉnh'",
    ),
    ("; ngang PhoBERT 0,749;", "; tương đương PhoBERT 0,749;"),
    (
        "'Đầu chú ý mạnh nhất nhìn đúng đoạn chứa bằng chứng'",
        "'Đầu chú ý mạnh nhất xác định đúng đoạn chứa bằng chứng'",
    ),
    (
        "'Trúng 87,8 %, gấp 14,3 lần mức ngẫu nhiên; lặp lại trên ViWikiFC'",
        "'Đúng 87,8 %, gấp 14,3 lần mức ngẫu nhiên; lặp lại trên ViWikiFC; hơn cắt bỏ ngữ cảnh (E19)'",
    ),
    (
        "'Bỏ câu bằng chứng làm chú ý tản ra theo hướng dự đoán trước'",
        "'Thay câu bằng chứng làm chú ý phân tán theo hướng dự đoán trước'",
    ),
    (
        "vượt đặc trưng bề mặt và ngang PhoBERT tinh chỉnh.",
        "vượt đặc trưng bề mặt và tương đương PhoBERT tinh chỉnh.",
    ),
    ("Nhóm trình bày thẳng kết quả này.", "Nhóm trình bày đầy đủ kết quả này."),
    (
        "chú ý theo đoạn chỉ đúng chỗ chứa bằng chứng",
        "chú ý theo đoạn xác định đúng vị trí bằng chứng",
    ),
]

# E19: a fifth step on the localisation slide. The left illustration fades out and a three-bar
# comparison with context ablation (Table 6.17) takes its place; the right panel stays.
E19_SETUP = r"""
  /* E19 (Bảng 6.17): chú ý so với cắt bỏ từng đoạn ngữ cảnh, 300 mẫu ViWikiFC */
  let e19On = false;
  const leftAll = [...cells, ...bars, ev, evTag, pin, verdict, locTtl, d1, d22];
  const e19 = hidden(svg), EX = 360, EW = 540;
  tx(e19, 0, 30, 'Đối chiếu với cắt bỏ từng đoạn ngữ cảnh (E19 · 300 mẫu ViWikiFC)', { 'font-size': 22, fill: C.muted });
  const eb = [['Đầu chú ý mạnh nhất', .850, '1 lượt đọc', C.ctx], ['Đầu chọn trên ISE-DSC01', .797, '1 lượt đọc', C.ctx],
              ['Cắt bỏ từng đoạn (ARC-JSD)', .733, '10,9 lượt đọc', C.res]].map((r, i) => {
    const y = 96 + i * 108;
    tx(e19, 0, y + 31, r[0], { 'font-size': 23, 'font-weight': i === 0 ? 700 : 400 });
    el('rect', { x: EX, y, width: EW, height: 44, rx: 4, fill: C.paper2 }, e19);
    const b = el('rect', { x: EX, y, width: 0, height: 44, rx: 4, fill: r[3] }, e19);
    const l = tx(e19, EX + 12, y + 31, fmt(r[1] * 100) + ' %', { 'font-size': 24, 'font-weight': 700, fill: '#fff', opacity: 0 });
    tx(e19, EX + EW + 16, y + 30, r[2], { 'font-size': 21, fill: C.muted });
    return { b, l, v: r[1] };
  });
  tx(e19, 0, 452, 'Tỷ lệ mẫu có đoạn xếp hạng đầu trùng đoạn bằng chứng · mức ngẫu nhiên 10,2 %', { 'font-size': 20, fill: C.muted });
"""
E19_STEP = r"""
    { cap: 'Thí nghiệm E19 đối chiếu với <b>cắt bỏ từng đoạn ngữ cảnh</b>: đầu chú ý mạnh nhất xác định đúng <b>85,0&nbsp;%</b> so với 73,3&nbsp;%, với 1 lượt đọc thay vì trung bình 10,9 lượt.', hold: .8,
      play: tl => { tl.call(() => { e19On = true; }); tl.to(leftAll, { opacity: 0, duration: .3 }); tl.to(e19, { opacity: 1, duration: .3 });
        eb.forEach((r, i) => { tl.to(r.b, { attr: { width: EW * r.v }, duration: .6, ease: 'power2.out' }, i ? '<.12' : '>'); tl.to(r.l, { opacity: 1, duration: .2 }, '<.4'); }); } },"""

js_start = tail_part.index("<script")
js = tail_part[js_start:]
for item in JS_SUBS:
    old, new, *n = item
    js = sub(js, old, new, n[0] if n else 1, where="js")

js = sub(
    js,
    "  tx(svg, 0, by + 84, 'đoạn 1', { 'font-size': 20, fill: C.muted }); tx(svg, (N - 1)",
    "  const d1 = tx(svg, 0, by + 84, 'đoạn 1', { 'font-size': 20, fill: C.muted }); const d22 = tx(svg, (N - 1)",
    where="loc",
)
js = sub(
    js,
    "  tx(svg, 0, 30, 'Minh họa một mẫu ISE-DSC01",
    "  const locTtl = tx(svg, 0, 30, 'Minh họa một mẫu ISE-DSC01",
    where="loc",
)
js = sub(
    js,
    "  let k = 3;\n  buttons(api, [['Mẫu khác ↻', () => { k = (k + 1) % S.length;",
    E19_SETUP
    + "  let k = 0;\n  buttons(api, [['Mẫu khác ↻', () => { if (e19On) return; k = (k + 1) % S.length;",
    where="loc",
)
# step 2 used to play four samples back to back (6,4 s); it now shows one, and "Mẫu khác" the rest
js = sub(
    js,
    "play: tl => { S.slice(0, 4).forEach((s, j) => { sample(tl, s, j === 0 ? 1.4 : .8); "
    "tl.to({}, { duration: .45 }); }); } },",
    "play: tl => { sample(tl, S[0], 1.4); } },",
    where="loc",
)
js = sub(
    js,
    "      play: tl => { tl.to(cells, { opacity: 1, duration: .2, stagger: .02 });",
    "      play: tl => { tl.call(() => { e19On = false; }); tl.to(cells, { opacity: 1, duration: .2, stagger: .02 });",
    where="loc",
)
LOC_LAST = "tl.to(r.lb, { opacity: 1, duration: .2 }, '<.3'); }); } },"
js = sub(js, LOC_LAST, LOC_LAST + E19_STEP, where="loc")


# Slide 5: the four constraints become icon chips with three or four words each
CHIP_OLD = (
    "  ['Không gọi LLM giám khảo', 'Không tinh chỉnh mô hình ngôn ngữ', 'Chạy trên một GPU T4 16 GB', "
    "'Tiếng Việt, ba lớp nhãn'].forEach((t, i) => {\n"
    "    el('rect', { x: i * 425, y: 504, width: 405, height: 50, rx: 25, fill: C.ink }, K);\n"
    "    tx(K, i * 425 + 202, 536, t, { 'text-anchor': 'middle', 'font-size': 19, 'font-weight': 600, fill: '#fff' }); });"
)
CHIP_NEW = (
    "  [['Không gọi LLM giám khảo', CHIP_ICONS[0]], ['Không tinh chỉnh mô hình', CHIP_ICONS[1]], "
    "['GPU Tesla T4 16 GB', CHIP_ICONS[2]], ['Tiếng Việt, ba lớp nhãn', CHIP_ICONS[3]]].forEach(([t, ic], i) => {\n"
    "    el('rect', { x: i * 425, y: 504, width: 405, height: 50, rx: 25, fill: C.ink }, K);\n"
    "    const g = el('g', { transform: `translate(${i * 425 + 24},514) scale(1.25)`, fill: 'none', stroke: '#9FE0D9', "
    "'stroke-width': 1.8, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, K); g.innerHTML = ic;\n"
    "    tx(K, i * 425 + 222, 536, t, { 'text-anchor': 'middle', 'font-size': 20, 'font-weight': 600, fill: '#fff' }); });"
)
js = sub(js, CHIP_OLD, CHIP_NEW, where="task")
CHIP_ICONS = [ICONS[n] for n in ("noapi", "frozen", "gpu", "lang")]
js = sub(
    js,
    "FIGS.task = ",
    "const CHIP_ICONS = " + json.dumps(CHIP_ICONS, ensure_ascii=False) + ";\nFIGS.task = ",
    where="task",
)

# Shorter step captions on the four slides that keep presenter-driven steps
CAP_SUBS = [
    (
        "Ba bộ dữ liệu tiếng Việt công khai. ViHallu là bộ chính; ISE-DSC01 có ngữ cảnh dài và đánh dấu sẵn câu bằng chứng; ViWikiFC dùng để đối chứng.",
        "Ba bộ chính: <b>ViHallu</b> (chính), <b>ISE-DSC01</b> (ngữ cảnh dài, có bằng chứng), <b>ViWikiFC</b> (đối chứng).",
    ),
    (
        "Nếu chia <b>ngẫu nhiên từng câu trả lời</b>, các câu trả lời của cùng một tài liệu rơi vào cả tập huấn luyện lẫn tập kiểm tra (vạch đỏ): rò rỉ dữ liệu giữa tập huấn luyện và tập kiểm tra.",
        "Chia <b>ngẫu nhiên</b>: cùng một tài liệu nằm ở cả tập huấn luyện lẫn kiểm tra (vạch đỏ) — rò rỉ dữ liệu.",
    ),
    (
        "Đề tài <b>chia theo ngữ cảnh</b>: mọi câu trả lời của một tài liệu đi chung một tập, tỷ lệ 80/10/10, hạt giống 42. Rò rỉ bằng 0.",
        "Chia <b>theo ngữ cảnh</b>: mỗi tài liệu nằm trọn một tập, 80/10/10, hạt giống 42 — rò rỉ bằng 0.",
    ),
    (
        "Kiểm tra cả các bộ có sẵn cách chia: tập kiểm tra gốc của ViWikiFC dùng lại <b>100 %</b> ngữ cảnh huấn luyện — nên điểm trên tập đó chỉ đo việc phân loại trên ngữ cảnh đã thấy.",
        "Tập kiểm tra gốc của ViWikiFC dùng lại <b>100 %</b> ngữ cảnh huấn luyện.",
    ),
    (
        "Mỗi lớp của mô hình tạo ra một <b>ma trận chú ý</b> cho 28 đầu, mỗi cạnh dài bằng độ dài văn bản. Với 4.096 token, một lớp đã chiếm khoảng <b>0,94 GB</b>.",
        "Mỗi lớp tạo một <b>ma trận chú ý</b> cho 28 đầu: ở 4.096 token chiếm khoảng <b>0,94 GB</b>.",
    ),
    (
        "Cách thông thường giữ lại ma trận của mọi lớp tới cuối lượt đọc. Mới tới <b>lớp 12</b>, tổng bộ nhớ đã vượt 16 GB của GPU T4; giữ đủ 28 lớp cần khoảng <b>26 GB</b> chỉ riêng cho ma trận.",
        "Giữ ma trận của mọi lớp: tới <b>lớp 12</b> đã vượt 16 GB; đủ 28 lớp cần khoảng <b>26 GB</b>.",
    ),
    (
        "Với <b>forward hook</b>: lớp nào tính xong, hook cộng chú ý theo từng đoạn — chỉ còn vài chục giá trị — rồi giải phóng ma trận ngay. Tại mỗi thời điểm, bộ nhớ chỉ chứa một ma trận.",
        "<b>Forward hook</b>: tính xong lớp nào thì cộng chú ý theo đoạn rồi giải phóng ma trận lớp đó.",
    ),
    (
        "Bộ nhớ đỉnh đo thực tế trên Tesla T4 ở ngưỡng 4.096 token là <b>8,4 GB</b> — mô hình 7B vận hành trọn vẹn trên một GPU 16 GB miễn phí của Kaggle.",
        "Đỉnh đo thực tế <b>8,4 GB</b> ở 4.096 token — mô hình 7B vừa một GPU 16 GB.",
    ),
    (
        "Mỗi ngữ cảnh ISE-DSC01 có trung bình <b>22,6 đoạn</b>. Người gán nhãn đã đánh dấu sẵn đoạn chứa bằng chứng (viền đậm).",
        "Ngữ cảnh ISE-DSC01 trung bình <b>22,6 đoạn</b>; đoạn bằng chứng được đánh dấu sẵn (viền đậm).",
    ),
    (
        "Với mỗi mẫu, xác định đoạn mà đầu chú ý mạnh nhất phân bổ chú ý nhiều nhất. Trùng đoạn bằng chứng là <b>đúng</b>, khác là <b>sai</b>.",
        "Đoạn nhận nhiều chú ý nhất của đầu mạnh nhất trùng đoạn bằng chứng là <b>đúng</b>.",
    ),
    (
        "Trên 2.376 mẫu, đầu mạnh nhất xác định đúng <b>87,8 %</b>; chọn ngẫu nhiên một đoạn chỉ đạt 6,1 % — thấp hơn <b>14,3 lần</b>.",
        "2.376 mẫu: đúng <b>87,8 %</b>, gấp <b>14,3 lần</b> chọn ngẫu nhiên (6,1 %).",
    ),
    (
        "Lặp lại trên bộ thứ hai (ViWikiFC): trung bình mọi đầu <b>32,9 %</b> so với 33,2 %. Khả năng định vị thuộc về mô hình, không phụ thuộc bộ dữ liệu.",
        "Lặp lại trên ViWikiFC: trung bình mọi đầu <b>32,9 %</b> so với 33,2 % — thuộc tính của mô hình.",
    ),
    (
        "Thí nghiệm E19 đối chiếu với <b>cắt bỏ từng đoạn ngữ cảnh</b>: đầu chú ý mạnh nhất xác định đúng <b>85,0&nbsp;%</b> so với 73,3&nbsp;%, với 1 lượt đọc thay vì trung bình 10,9 lượt.",
        "E19: chú ý đúng <b>85,0&nbsp;%</b>, cắt bỏ ngữ cảnh 73,3&nbsp;% — <b>1</b> lượt đọc so với 10,9.",
    ),
    (
        "Huấn luyện trên ViHallu rồi chấm ISE-DSC01: trong 1.286 câu thật sự <b>ngoại lai</b>, chỉ <b>66</b> câu được phân loại đúng; <b>988 câu</b> bị phân loại thành nội tại.",
        "ViHallu → ISE-DSC01: 1.286 câu <b>ngoại lai</b>, chỉ <b>66</b> đúng; <b>988</b> bị gọi là nội tại.",
    ),
    (
        "Macro-F1 ba lớp giảm còn <b>0,358</b>, gần mức ngẫu nhiên. Với câu hỏi nhị phân “có ảo giác hay không”, kết quả vẫn đạt <b>0,664</b>, trên mức ngẫu nhiên 0,5.",
        "Ba lớp còn <b>0,358</b>, gần ngẫu nhiên; nhị phân vẫn <b>0,664</b> (ngẫu nhiên 0,5).",
    ),
    (
        "Chiều ngược lại mất lớp còn lại: trong 234 câu <b>nội tại</b> của ViHallu, 136 câu bị phân loại thành ngoại lai. Nhị phân vẫn đạt <b>0,776</b>.",
        "Chiều ngược lại: 136/234 câu <b>nội tại</b> bị gọi là ngoại lai; nhị phân vẫn <b>0,776</b>.",
    ),
    (
        "Nguyên nhân khả dĩ nằm ở <b>định nghĩa nhãn</b> của hai bộ: cùng tên lớp nhưng tạo ra theo hai cách khác nhau.",
        "Nguyên nhân khả dĩ: hai bộ có <b>định nghĩa nhãn</b> khác nhau.",
    ),
]
for old, new in CAP_SUBS:
    js = sub(js, old, new, where="cap")

# ?qa also reports slides whose title block pushes the figure into the step caption
js = sub(
    js,
    "slides.forEach((s, j) => { try { show(j); } catch (e) {",
    "slides.forEach((s, j) => { try { show(j); const h = s.querySelector('.fig') && s.querySelector('.head'); "
    "if (h && h.offsetTop + h.offsetHeight > 312) out.push(`slide ${j + 1}: khối tiêu đề cao ${h.offsetTop + h.offsetHeight}px > 312`); "
    "if (cur && cur.goStep) cur.steps.forEach((_, k) => cur.goStep(k, false)); } catch (e) {",
    where="qa",
)

# Presenter-driven steps. The deck used to play every step of a diagram back to back in 6–15 s
# while the spoken notes for a slide run 50–85 s, so the picture ran ahead of the speaker. Now the
# first step plays on arrival and stops; each "next" plays one more step; ?auto restores the old
# behaviour (for screen recording). ?all, ?at and ?qa behave as before.
# Only four diagrams replace earlier content with later content (measured: elements visible at the
# end of a step are changed or removed by the end of the slide), so only they keep presenter-driven
# steps. The other fourteen only add content: they play through once, with one short summary.
STEP_FIGS = ["data", "hook", "loc", "xfer"]
FIG_SUMMARY = {
    "types": "Cùng một ngữ cảnh, ba câu trả lời: điểm rủi ro <b>0,001</b> (trung thực) · <b>0,998</b> (nội tại) · <b>1,000</b> (ngoại lai).",
    "task": "Mô hình mở đọc ngữ cảnh, câu hỏi, câu trả lời trong <b>một lượt</b>; chỉ bộ phân loại tuyến tính phải huấn luyện.",
    "costs": "Mỗi hướng hiện có trả một chi phí: <b>thời gian và dữ liệu ra ngoài</b>, <b>tham số huấn luyện</b>, hoặc <b>độ chính xác</b>.",
    "map": "Khóa luận thuộc nhánh <b>trọng số chú ý</b>: một lượt đọc, bộ phân loại nhỏ, chưa có cho tiếng Việt.",
    "lb": "Mỗi đầu cho một <b>tỷ lệ lookback</b>; <b>756</b> giá trị đưa vào hồi quy logistic.",
    "chunk": "Cùng <b>62 %</b> chú ý vào ngữ cảnh: A tập trung một đoạn (entropy 0,65), B phân bố đều (entropy 1,00).",
    "pipe": "Ghép prompt → một lượt đọc, hook lấy chú ý theo đoạn → <b>192</b> đặc trưng → hồi quy logistic <b>579</b> tham số.",
    "sys": "Bốn tầng, tầng trên chỉ gọi tầng dưới; bộ phát hiện <b>11,5 KB</b>, nạp lại trùng <b>700/700</b>.",
    "demo": "Mô hình 3B tự sinh mệnh đề không có căn cứ; bộ phát hiện gán <b>ngoại lai</b>, rủi ro <b>0,997</b>.",
    "res": "Chunk-aware <b>0,757</b>, lookback gộp <b>0,745</b> — tương đương PhoBERT 0,749, với 579 so với 369 triệu tham số.",
    "iv": "Thay câu bằng chứng: cả <b>bốn</b> đặc trưng đổi đúng hướng dự đoán ở <b>71–75 %</b> trên 1.836 cặp.",
    "null": "Sáu phép đo đều trong <b>vùng nhiễu ±0,03</b>; <b>99,9 %</b> tín hiệu hình dạng đã có trong tỷ lệ gộp.",
    "cost": "XLM-R nhanh nhất; chú ý ít tham số nhất; mô hình đọc <b>3B</b> nhanh gấp đôi, chỉ giảm 0,01 macro-F1.",
    "hyp": "<b>H1, H3, H4</b> được ủng hộ; <b>H2</b> không; <b>H5</b> bác bỏ ở ba lớp, ủng hộ một phần ở nhị phân.",
}
ENGINE_START = "  function mount(s) {\n"
ENGINE_END = "  function start() {\n"
a, b = js.index(ENGINE_START), js.index(ENGINE_END)
assert js.count(ENGINE_START) == 1 and js.count(ENGINE_END) == 1 and a < b
NEW_ENGINE = r"""  // dựng sơ đồ của slide s; atEnd: hiện sẵn trạng thái cuối (khi lùi về slide trước)
  function mount(s, atEnd) {
    if (pending) { pending.kill(); pending = null; }
    if (cur) { if (cur.run) cur.run.kill(); cur.tl.kill(); cur = null; }
    TIP_HIDE();
    const name = s.dataset.fig; if (!name || !FIGS[name]) return;
    const fig = s.querySelector('.fig'), head = s.querySelector('.head');
    const headB = head.offsetTop + head.offsetHeight;
    fig.style.top = Math.max(headB + 26, headB + (898 - headB - 560) / 2) + 'px';
    const svg = fig.querySelector('svg'); svg.innerHTML = '';
    const t0 = s.querySelector('.terms'); if (t0) t0.style.maxWidth = '';
    fig.querySelectorAll('.ctl').forEach(c => c.remove());
    const tl = gsap.timeline({ paused: true });
    const stepMode = !AUTO && STEP_FIGS.includes(name);   // chỉ bốn sơ đồ có bước sau thay nội dung bước trước
    const sum = !AUTO && !stepMode ? FIG_SUMMARY[name] : null;
    // nút trong hình: chế độ bấm chỉ cho bước đang chạy chạy xong; chế độ tự chạy thì tới cuối như cũ
    const api = { fig, svg, tl, finish: () => { if (!stepMode) { if (tl.progress() < 1) { tl.progress(1); setStep(steps.length - 1); } }
      else if (c.run) goStep(c.k, false); } };
    const steps = FIGS[name](svg, api);
    const ctl = fig.querySelector('.ctl'), terms = s.querySelector('.terms');
    if (ctl && terms) terms.style.maxWidth = (1680 - ctl.offsetWidth - 40) + 'px';   // chừa chỗ cho nút điều khiển
    const hb = head.offsetTop + head.offsetHeight;
    fig.style.top = Math.max(hb + 26, hb + (898 - hb - 560) / 2) + 'px';
    const dots = s.querySelector('.dots'), cap = s.querySelector('.stepcap .txt');
    dots.innerHTML = steps.map((_, k) => `<span title="Bước ${k + 1}">${k + 1}</span>`).join('');
    dots.style.display = sum ? 'none' : '';
    function setStep(k) { cap.innerHTML = sum || steps[k].cap; [...dots.children].forEach((d, j) => d.classList.toggle('on', j <= k)); }
    // chế độ bấm: chú thích do goStep đặt, và mỗi bước cách bước sau 0,01 s để điểm cuối bước j
    // không trùng điểm đầu bước j + 1 (nếu trùng, các lệnh mở đầu bước sau sẽ chạy sớm)
    steps.forEach((st, k) => { tl.addLabel('s' + k); if (!stepMode) tl.call(() => setStep(k)); st.play(tl); tl.addLabel('e' + k);
      tl.to({}, { duration: stepMode ? .01 : (st.hold ?? 1.4) }); });
    tl.timeScale(SPEED);
    const c = { tl, steps, setStep, k: 0, run: null, stepMode };
    function goStep(j, animate) {                       // tới cuối bước j; animate: chạy hoạt ảnh của riêng bước j
      if (c.run) { c.run.kill(); c.run = null; }
      c.k = j; tl.pause();
      tl.seek(0, true);                                  // về đầu rồi tua tới để các lệnh đổi trạng thái chạy đúng thứ tự
      tl.seek(animate ? 's' + j : 'e' + j, false); setStep(j);
      if (animate) c.run = tl.tweenTo('e' + j, { onComplete: () => { c.run = null; } });
    }
    c.goStep = goStep;
    [...dots.children].forEach((d, j) => d.addEventListener('click', e => { e.stopPropagation(); goStep(j, true); }));
    cur = c;
    if (ALL) { tl.progress(1); setStep(steps.length - 1); c.k = steps.length - 1; }
    else if (AT !== null) { tl.seek(AT, false); let k = 0; steps.forEach((_, j) => { if (tl.labels['s' + j] <= AT) k = j; }); setStep(k); c.k = k; }
    else if (!stepMode && atEnd) { tl.progress(1); setStep(steps.length - 1); c.k = steps.length - 1; }
    else if (!stepMode) { setStep(0); pending = gsap.delayedCall(.35, () => { pending = null; if (cur === c) tl.play(); }); }
    else if (atEnd) goStep(steps.length - 1, false);
    else { setStep(0); pending = gsap.delayedCall(.35, () => { pending = null; if (cur === c) goStep(0, true); }); }
  }

  function show(n, atEnd) {
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((s, j) => s.classList.toggle('active', j === i));
    document.getElementById('progress').style.width = (100 * (i + 1) / slides.length) + '%';
    document.getElementById('notes-body').innerHTML = `<b>Slide ${i + 1}/${slides.length}</b><br><br>` + (slides[i].dataset.notes || '');
    history.replaceState(null, '', location.search + '#' + (i + 1));
    mount(slides[i], atEnd);
  }

  // tới: bước 1 chưa bắt đầu thì chạy ngay; đang chạy thì cho xong; còn bước thì chạy bước kế; hết thì sang slide
  function next() {
    const c = cur;
    if (c && c.stepMode && !ALL) {
      if (pending) { pending.kill(); pending = null; c.goStep(0, true); return; }
      if (c.run) { c.goStep(c.k, false); return; }
      if (c.k < c.steps.length - 1) { c.goStep(c.k + 1, true); return; }
    }
    show(i + 1);
  }
  // lùi: lùi một bước; đang ở bước đầu thì về slide trước, hiện sẵn trạng thái cuối
  function prev() {
    const c = cur;
    if (c && c.stepMode && !ALL && c.k > 0 && !pending) { c.goStep(c.k - 1, false); return; }
    show(i - 1, true);
  }

  const black = document.createElement('div'); black.id = 'black'; document.body.appendChild(black);
  let typed = '', typedAt = 0;                           // gõ số rồi Enter để nhảy tới slide
  addEventListener('keydown', e => {
    if (/^[0-9]$/.test(e.key)) { if (Date.now() - typedAt > 2000) typed = ''; typed += e.key; typedAt = Date.now(); return; }
    if (e.key === 'Enter' && typed && Date.now() - typedAt < 2000) { e.preventDefault(); show(parseInt(typed, 10) - 1); typed = ''; return; }
    typed = '';
    if (e.shiftKey && e.key === 'ArrowRight') { e.preventDefault(); show(i + 1); }
    else if (e.shiftKey && e.key === 'ArrowLeft') { e.preventDefault(); show(i - 1, true); }
    else if (['ArrowRight', 'ArrowDown', ' ', 'PageDown', 'Enter'].includes(e.key)) { e.preventDefault(); next(); }
    else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(e.key)) { e.preventDefault(); prev(); }
    else if (e.key === 'r' || e.key === 'R') { if (cur) { if (!cur.stepMode) cur.tl.restart(); else cur.goStep(cur.k, true); } }
    else if (e.key === 'b' || e.key === 'B' || e.key === '.') { black.classList.toggle('on'); }
    else if (e.key === 'n' || e.key === 'N') { document.getElementById('notes').classList.toggle('on'); }
    else if (e.key === 'f' || e.key === 'F') { document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); }
    else if (e.key === 'Home') show(0); else if (e.key === 'End') show(slides.length - 1, true);
  });
  addEventListener('click', e => {
    if (black.classList.contains('on')) { black.classList.remove('on'); return; }
    if (e.target.closest('.fig, .ctl, #notes, button, .grid16, .dots')) return;   // bấm trong sơ đồ: để dành cho tương tác
    if (e.clientX > innerWidth * .2) next(); else prev();
  });
"""
NEW_ENGINE = NEW_ENGINE.replace(
    "  // dựng sơ đồ của slide s;",
    "  const STEP_FIGS = " + json.dumps(STEP_FIGS) + ";\n"
    "  const FIG_SUMMARY = " + json.dumps(FIG_SUMMARY, ensure_ascii=False) + ";\n"
    "  // dựng sơ đồ của slide s;",
    1,
)
js = js[:a] + NEW_ENGINE + js[b:]
js = sub(
    js,
    "  let i = 0, cur = null;\n",
    "  let i = 0, cur = null, pending = null;\n  const AUTO = Q.has('auto');\n",
    where="engine",
)
js = sub(
    js,
    "   ← → / Space: đổi slide · R: chạy lại sơ đồ · N: ghi chú · F: toàn màn hình\n",
    "   → Space PageDown: bước kế (chỉ 4 sơ đồ chia bước), hết bước thì sang slide · ← PageUp: lùi\n"
    "   Shift+→ / Shift+←: bỏ qua các bước · số + Enter: nhảy tới slide · B: màn hình đen\n"
    "   R: chạy lại bước hiện tại · N: ghi chú · F: toàn màn hình\n"
    "   ?auto — sơ đồ tự chạy hết các bước như bản cũ (để quay màn hình)\n",
    where="engine",
)
tail_part = tail_part[:js_start] + js

for k in range(len(S)):
    S[k] = S[k].replace("Chương 6 · Thực nghiệm</span>", "Chương 6 · Thực nghiệm và kết quả</span>")
    S[k] = S[k].replace(
        "Chương 7–8 · Tự đánh giá</span>", "Chương 7–8 · Thảo luận và kết luận</span>"
    )

# ---------------------------------------------------------------------------------------------
# 5. Agenda and part dividers
# ---------------------------------------------------------------------------------------------
run_tpl = re.search(r'(<div class="run">.*?<span class="sec">)(.*?)(</span></div>)', S[1], re.S)
assert run_tpl and "Chương 1" in run_tpl.group(2)

# (name, description, chapter label, slide keys of the part)
PARTS = [
    (
        "Giới thiệu",
        "Phân loại ảo giác, phát biểu bài toán, động lực và câu hỏi nghiên cứu",
        "Chương 1",
        ["types", "task", "costs", "gaps"],
    ),
    (
        "Cơ sở lý thuyết",
        "Các hướng phát hiện ảo giác và phương pháp nền Lookback Lens",
        "Chương 2",
        ["map", "lb"],
    ),
    (
        "Dữ liệu",
        "Bốn bộ dữ liệu tiếng Việt và phương pháp chia tập theo ngữ cảnh",
        "Chương 3",
        ["data"],
    ),
    (
        "Phương pháp đề xuất",
        "Chunk-aware lookback ratio, quy trình một lượt đọc, forward hook",
        "Chương 4",
        ["chunk", "pipe", "hook"],
    ),
    (
        "Hệ thống",
        "Kiến trúc ViHalluLens và minh họa vận hành trên hệ RAG",
        "Chương 5",
        ["sys", "demo"],
    ),
    (
        "Thực nghiệm và kết quả",
        "Phân loại, định vị bằng chứng, can thiệp, chi phí và khái quát hóa chéo bộ dữ liệu",
        "Chương 6",
        ["res", "loc", "iv", "null", "cost", "xfer"],
    ),
    (
        "Kết luận",
        "Kiểm định giả thuyết, kết quả đạt được, hạn chế và hướng phát triển",
        "Chương 7–8",
        ["hyp", "done"],
    ),
]
PART_NOTES = [
    "Phần thứ nhất giới thiệu bài toán: hai loại ảo giác, phát biểu bài toán, động lực và ba câu "
    "hỏi nghiên cứu.",
    "Phần thứ hai trình bày các hướng phát hiện ảo giác hiện có và phương pháp nền Lookback Lens.",
    "Phần thứ ba trình bày dữ liệu và phương pháp chia tập theo ngữ cảnh.",
    "Phần thứ tư trình bày phương pháp đề xuất: chunk-aware lookback ratio, quy trình một lượt đọc "
    "và kỹ thuật trích trọng số chú ý bằng forward hook.",
    "Phần thứ năm trình bày kiến trúc hệ thống ViHalluLens và một lượt minh họa trên hệ RAG.",
    "Phần thứ sáu trình bày kết quả thực nghiệm: phân loại, kiểm chứng cơ chế, chi phí và khả năng "
    "khái quát hóa.",
    "Phần cuối kiểm định năm giả thuyết nghiên cứu, tổng kết kết quả đạt được, hạn chế và hướng "
    "phát triển.",
]

# final order: cover, agenda, then each part preceded by its divider, then references, thanks
order: list[tuple[str, object]] = [("slide", IDX["cover"]), ("agenda", None)]
for p in range(len(PARTS)):
    order.append(("part", p))
    order += [("slide", IDX[key]) for key in PARTS[p][3]]
order += [("slide", IDX["refs"]), ("slide", IDX["thanks"])]
assert sorted(v for t, v in order if t == "slide") == list(range(23))
pos = {}
for n, (t, v) in enumerate(order, 1):
    pos[(t, v)] = n


def span(p: int) -> str:
    keys = PARTS[p][3]
    a, b = pos[("slide", IDX[keys[0]])], pos[("slide", IDX[keys[-1]])]
    return f"Slide {a}" if a == b else f"Slide {a}–{b}"


AGENDA_NOTES = (
    "Bài trình bày gồm bảy phần, theo bố cục của quyển khóa luận: giới thiệu bài toán, cơ sở lý "
    "thuyết, dữ liệu, phương pháp đề xuất, hệ thống, thực nghiệm và kết quả, và cuối cùng là kết "
    "luận. Phần thực nghiệm và kết quả chiếm nhiều thời gian nhất vì chứa các kết quả chính."
)
PART_ICONS = ["intro", "theory", "data", "method", "system", "results", "conclusion"]
rows = "\n".join(
    f'    <li class="rise r{min(p + 1, 7)}"><span class="no">{p + 1:02d}</span>{icon(PART_ICONS[p])}'
    f'<span class="nm">{name}</span><span class="pg">{span(p)}</span></li>'
    for p, (name, _desc, _ch, _k) in enumerate(PARTS)
)
AGENDA = f'''<section class="slide agenda" data-notes="{html.escape(AGENDA_NOTES)}">
  {run_tpl.group(1)}Nội dung trình bày{run_tpl.group(3)}
  <div class="head"><h2>Nội dung trình bày</h2></div>
  <ol class="toc">
{rows}
  </ol>
  <div class="foot"><span>Bố cục theo tám chương của quyển khóa luận</span><span>00</span></div>
</section>'''


def divider(p: int) -> str:
    name, desc, chap, _keys = PARTS[p]
    items = "".join(
        f'<li class="{"on" if q == p else ("past" if q < p else "")}"><span class="n">{q + 1:02d}</span>{PARTS[q][0]}</li>'
        for q in range(len(PARTS))
    )
    return f'''<section class="slide part" data-notes="{html.escape(PART_NOTES[p])}">
  <div class="pic rise r1">{icon(PART_ICONS[p])}</div>
  <div class="pk rise r1">Phần {p + 1} / {len(PARTS)} · {chap}</div>
  <div class="pt rise r2">{name}</div>
  <div class="pd rise r3">{desc}</div>
  <ol class="plist rise r4">{items}</ol>
  <div class="foot"><span>Phát hiện ảo giác cho RAG tiếng Việt dựa trên tín hiệu chú ý nội tại</span><span>00</span></div>
</section>'''


CSS = """
/* === HOÀN THIỆN 14/11: câu tóm tắt dưới tiêu đề, mục lục, slide chuyển phần === */
.lede { margin-top: 12px; padding-left: 16px; border-left: 4px solid var(--ctx); font: 400 27px/1.38 var(--sans); color: var(--ink); max-width: 1640px; }
.r6 { transition-delay: .78s; } .r7 { transition-delay: .92s; }
.dots span { cursor: pointer; }
#black { position: fixed; inset: 0; background: #000; z-index: 90; display: none; }
#black.on { display: block; }
.toc { position: absolute; left: 120px; right: 120px; top: 222px; list-style: none; border-top: 2px solid var(--ink); }
.toc li { display: grid; grid-template-columns: 100px 76px 1fr 180px; align-items: center; padding: 18px 0 16px; border-bottom: 1.5px solid var(--rule); }
.toc .ic { width: 46px; height: 46px; color: var(--ctx); }
.toc .no { font: 500 42px/1 var(--serif); color: var(--ctx); }
.toc .nm { font: 500 38px/1.15 var(--serif); }
.toc .pg { font: 600 19px/1 var(--sans); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); text-align: right; }
.part { background: var(--ink); color: var(--paper); }
.part::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 18px; background: var(--ctx); }
.part .pk { position: absolute; left: 120px; top: 330px; font: 600 22px/1 var(--sans); letter-spacing: .16em; text-transform: uppercase; color: #9FE0D9; }
.part .pt { position: absolute; left: 120px; top: 382px; width: 900px; font: 500 88px/1.08 var(--serif); letter-spacing: -.015em; }
.part .pd { position: absolute; left: 120px; top: 610px; width: 860px; font: 400 29px/1.5 var(--sans); color: #B9C0CC; }
.part .plist { position: absolute; left: 1180px; right: 120px; top: 270px; list-style: none; border-left: 2px solid #3A4456; }
.part .plist li { position: relative; display: flex; gap: 22px; align-items: baseline; padding: 15px 0 15px 34px; font: 500 30px/1.2 var(--serif); color: #6E7788; }
.part .plist li .n { font: 600 18px/1 var(--sans); letter-spacing: .1em; }
.part .plist li.past { color: #98A1B1; }
.part .plist li.on { color: var(--paper); }
.part .plist li.on .n { color: #9FE0D9; }
.part .plist li.on::before { content: ""; position: absolute; left: -5px; top: 10px; bottom: 10px; width: 8px; border-radius: 4px; background: #9FE0D9; }
.part .foot { color: #8B94A5; }
.part .pic { position: absolute; left: 120px; top: 200px; color: #9FE0D9; }
.part .pic .ic { width: 96px; height: 96px; }
.gq3 { position: absolute; left: 120px; right: 120px; top: 250px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; }
.gcol .gtop { background: #fff; border: 2px solid var(--rule); border-top: 8px solid var(--c); border-radius: 14px; padding: 30px 34px 32px; min-height: 320px; }
.gcol .ic { width: 72px; height: 72px; color: var(--c); }
.gcol .k { margin-top: 16px; font: 700 18px/1 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--c); }
.gcol .s { margin-top: 14px; font: 500 35px/1.26 var(--serif); }
.gcol .s em { font-style: italic; color: var(--c); }
.gcol .gar { text-align: center; font: 700 30px/1 var(--sans); color: var(--c); padding: 12px 0; }
.gcol .qc { background: #fff; border: 2px solid var(--c); border-radius: 14px; padding: 26px 34px 28px; }
.gcol .qc .q { margin-top: 12px; font: 400 28px/1.4 var(--sans); }
.gcol .qc .a { margin-top: 16px; font: 600 20px/1 var(--sans); color: var(--muted); }
.res3 { position: absolute; left: 120px; right: 120px; top: 222px; display: grid; grid-template-columns: 1.15fr 1fr 1fr; gap: 36px; }
.rcol { background: #fff; border: 2px solid var(--rule); border-top: 8px solid var(--c); border-radius: 14px; padding: 24px 30px 18px; }
.rcol h3 { display: flex; align-items: center; gap: 14px; font: 600 30px/1.2 var(--serif); color: var(--c); margin-bottom: 10px; }
.rcol h3 .ic { width: 40px; height: 40px; }
.rcol ul { list-style: none; }
.rcol li { display: grid; gap: 16px; align-items: baseline; padding: 14px 0; border-top: 1px solid var(--rule); font: 400 23px/1.38 var(--sans); }
.rcol li.num { grid-template-columns: 118px 1fr; }
.rcol li.line { grid-template-columns: 1fr; padding-left: 26px; position: relative; }
.rcol li.line::before { content: ""; position: absolute; left: 2px; top: 25px; width: 12px; height: 3px; border-radius: 2px; background: var(--c); }
.rcol li .v { font: 600 36px/1 var(--serif); color: var(--c); }
"""  # noqa: E501 — CSS rules kept one per line
i = head_part.rindex("</style>")
head_part = head_part[:i] + CSS + head_part[i:]

blocks = []
for t, v in order:
    if t == "slide":
        blocks.append(S[v])
    elif t == "agenda":
        blocks.append(AGENDA)
    else:
        blocks.append(divider(v))

FOOT = re.compile(r'(<div class="foot"><span>.*?</span><span>)[^<]*(</span></div>)', re.S)
deck = "\n".join(
    FOOT.sub(lambda m, n=n: f"{m.group(1)}{n:02d}{m.group(2)}", b) for n, b in enumerate(blocks, 1)
)

# ---------------------------------------------------------------------------------------------
# 6. Leftover colloquial wording anywhere visible: fail rather than ship it
# ---------------------------------------------------------------------------------------------
out = head_part + deck + tail_part
# Academic wording agreed for the thesis on 15/11 ("chấm" → đánh giá / kiểm tra / phát hiện,
# "chuyển được" → "chuyển giao được", "đổi đúng hướng" → "thay đổi đúng hướng"), applied to the
# finished deck so every earlier step keeps its own strings. "chấm" as a chart dot stays.
VAN_PHONG = [
    ('khi nạp lại và chấm 700 mẫu kiểm tra, kết quả trùng',
     'khi nạp lại và đánh giá 700 mẫu test, kết quả trùng'),
    ('lưu ý Gemini chỉ được chấm trên 300 mẫu',
     'lưu ý Gemini chỉ được đánh giá trên 300 mẫu'),
    ('chấm theo từng câu của phản hồi (E18)',
     'gộp đặc trưng theo từng câu của phản hồi (E18)'),
    ('Nhóm đã thử chấm theo từng câu (E18)',
     'Nhóm đã thử gộp đặc trưng theo từng câu (E18)'),
    ('hướng phát triển tiếp theo là chấm theo từng đoạn',
     'hướng phát triển tiếp theo là phát hiện theo từng đoạn'),
    ('<span>Chấm theo từng đoạn câu trả lời',
     '<span>Phát hiện theo từng đoạn câu trả lời'),
    ('Giám khảo Gemini (bản miễn phí) chấm 300 mẫu;',
     'Giám khảo Gemini (bản miễn phí) đánh giá 300 mẫu;'),
    ("'VÙNG PHẢN HỒI · câu cần chấm'",
     "'VÙNG PHẢN HỒI · câu cần kiểm tra'"),
    ('và câu trả lời cần chấm được ghép vào',
     'và câu trả lời cần kiểm tra được ghép vào'),
    ("'Gọi Gemini chấm từng mẫu — 8,2 giây/mẫu, không huấn luyện · chấm trên 300/700 mẫu test'",
     "'Gemini đánh giá từng mẫu — 8,2 giây/mẫu, không huấn luyện · đánh giá trên 300/700 mẫu test'"),
    ("'† Gemini chấm trên 300/700 mẫu test",
     "'† Gemini được đánh giá trên 300/700 mẫu test"),
    ("'Bộ nhớ GPU đỉnh khi chấm ViHallu (MB)'",
     "'Bộ nhớ GPU đỉnh khi trích đặc trưng ViHallu (MB)'"),
    ("'Huấn luyện ViHallu → chấm ISE-DSC01'",
     "'Huấn luyện ViHallu → đánh giá ISE-DSC01'"),
    ("'Huấn luyện ISE-DSC01 → chấm ViHallu'",
     "'Huấn luyện ISE-DSC01 → đánh giá ViHallu'"),
    ("'macro-F1 khi chấm chéo bộ'",
     "'macro-F1 khi đánh giá chéo bộ'"),
    ('Điều <b>chuyển được</b> là “có bám ngữ cảnh hay không”; điều không chuyển được là “ảo giác loại nào”.',
     'Phần <b>chuyển giao được</b> là “có dựa trên ngữ cảnh hay không”; phần không chuyển giao được là “ảo giác loại nào”.'),
    ('nạp lại chấm 700 mẫu kiểm tra trùng',
     'nạp lại và đánh giá 700 mẫu test, trùng'),
    ('Qwen2.5-7B chỉ đọc lại để chấm.',
     'Qwen2.5-7B chỉ đọc lại để phát hiện ảo giác.'),
    ("'CÂU TRẢ LỜI r CẦN CHẤM · của bất kỳ hệ RAG nào'",
     "'CÂU TRẢ LỜI r CẦN KIỂM TRA · của bất kỳ hệ RAG nào'"),
    ('nên chấm được câu trả lời của hệ RAG khác.',
     'nên kiểm tra được câu trả lời của hệ RAG khác.'),
    ('và <b>câu trả lời</b> cần chấm.',
     'và <b>câu trả lời</b> cần kiểm tra.'),
    ("'Chi phí mỗi lần chấm một câu trả lời →'",
     "'Chi phí mỗi lần kiểm tra một câu trả lời →'"),
    ('nhưng mỗi lần chấm là một lượt gọi mô hình khác',
     'nhưng mỗi lần kiểm tra là một lượt gọi mô hình khác'),
    ('Cả bốn đặc trưng đổi đúng hướng ở 71–75 %',
     'Cả bốn đặc trưng thay đổi đúng hướng ở 71–75 %'),
    ('thì chuyển được sang bộ dữ liệu khác.',
     'thì chuyển giao được sang bộ dữ liệu khác.'),
    ('đặc trưng đổi đúng hướng dự đoán',
     'đặc trưng thay đổi đúng hướng dự đoán'),
    ("'Tỷ lệ cặp đổi đúng hướng dự đoán'",
     "'Tỷ lệ cặp thay đổi đúng hướng dự đoán'"),
    ("số cặp đổi đúng hướng đã ghi trước",
     "số cặp thay đổi đúng hướng đã ghi trước"),
    ("đại lượng hình dạng đổi đúng hướng ở 71–75 %",
     "đại lượng hình dạng thay đổi đúng hướng ở 71–75 %"),
    ("chi phí mỗi lần chấm ---",
     "chi phí mỗi lần kiểm tra ---"),
]
for old, new in VAN_PHONG:
    if out.count(old) != 1:
        problems.append(f"van phong: «{old[:60]}» khớp {out.count(old)} lần")
    out = out.replace(old, new)
visible = re.sub(r"data:[^\"')]+", "", out)
BANNED = [
    "bịa",
    "nói sai",
    "tự thêm",
    "bắt được",
    "chạy thật",
    "card T4",
    "card 16",
    "học thuộc",
    "đoán bừa",
    "chọn bừa",
    "trúng",
    "tản ra",
    "rải đều",
    "tỷ lệ nhìn lại",
    "cái giá",
    "dồn ",
    "cần chấm", "CẦN CHẤM", "chấm theo", "Chấm theo", "chấm trên", "được chấm", "chấm từng",
    "chấm chéo", "lần chấm", "để chấm", "chấm được", "→ chấm", "chấm 300", "chấm 700",
    "chuyển được", "cặp đổi đúng", "trưng đổi đúng", "dạng đổi đúng", "dàn trải", "bám ngữ cảnh", "bám vào", "hạ xung",
    "chỉ đúng đoạn", "bảo chứng",
]
for w in BANNED:
    for m in re.finditer(re.escape(w), visible):
        ctx = visible[max(0, m.start() - 60) : m.end() + 40].replace("\n", " ")
        if "/*" in ctx or "//" in ctx.split(w)[0][-40:]:
            continue  # inside a code comment, never rendered
        problems.append(f"banned '{w}': …{ctx}…")

if problems:
    print("\n".join(problems))
    sys.exit(1)
OUT.write_text(out, encoding="utf-8")
print(OUT, len(blocks), "slide")
