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
    // nút trong hình: chế độ bấm chỉ cho bước đang chạy chạy xong; chế độ tự chạy thì tới cuối như cũ
    const api = { fig, svg, tl, finish: () => { if (AUTO) { if (tl.progress() < 1) { tl.progress(1); setStep(steps.length - 1); } }
      else if (c.run) goStep(c.k, false); } };
    const steps = FIGS[name](svg, api);
    const ctl = fig.querySelector('.ctl'), terms = s.querySelector('.terms');
    if (ctl && terms) terms.style.maxWidth = (1680 - ctl.offsetWidth - 40) + 'px';   // chừa chỗ cho nút điều khiển
    const hb = head.offsetTop + head.offsetHeight;
    fig.style.top = Math.max(hb + 26, hb + (898 - hb - 560) / 2) + 'px';
    const dots = s.querySelector('.dots'), cap = s.querySelector('.stepcap .txt');
    dots.innerHTML = steps.map((_, k) => `<span title="Bước ${k + 1}">${k + 1}</span>`).join('');
    function setStep(k) { cap.innerHTML = steps[k].cap; [...dots.children].forEach((d, j) => d.classList.toggle('on', j <= k)); }
    // chế độ bấm: chú thích do goStep đặt, và mỗi bước cách bước sau 0,01 s để điểm cuối bước j
    // không trùng điểm đầu bước j + 1 (nếu trùng, các lệnh mở đầu bước sau sẽ chạy sớm)
    steps.forEach((st, k) => { tl.addLabel('s' + k); if (AUTO) tl.call(() => setStep(k)); st.play(tl); tl.addLabel('e' + k);
      tl.to({}, { duration: AUTO ? (st.hold ?? 1.4) : .01 }); });
    tl.timeScale(SPEED);
    const c = { tl, steps, setStep, k: 0, run: null };
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
    else if (AUTO) { setStep(0); pending = gsap.delayedCall(.35, () => { pending = null; if (cur === c) tl.play(); }); }
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
    if (c && !AUTO && !ALL) {
      if (pending) { pending.kill(); pending = null; c.goStep(0, true); return; }
      if (c.run) { c.goStep(c.k, false); return; }
      if (c.k < c.steps.length - 1) { c.goStep(c.k + 1, true); return; }
    }
    show(i + 1);
  }
  // lùi: lùi một bước; đang ở bước đầu thì về slide trước, hiện sẵn trạng thái cuối
  function prev() {
    const c = cur;
    if (c && !AUTO && !ALL && c.k > 0 && !pending) { c.goStep(c.k - 1, false); return; }
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
    else if (e.key === 'r' || e.key === 'R') { if (cur) { if (AUTO || !cur.goStep) cur.tl.restart(); else cur.goStep(cur.k, true); } }
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
    "   → Space PageDown: bước kế, hết bước thì sang slide · ← PageUp: lùi một bước\n"
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
rows = "\n".join(
    f'    <li class="rise r{min(p + 1, 7)}"><span class="no">{p + 1:02d}</span>'
    f'<span class="nm">{name}</span><span class="ds">{desc}</span><span class="pg">{span(p)}</span></li>'
    for p, (name, desc, _ch, _k) in enumerate(PARTS)
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
.toc li { display: grid; grid-template-columns: 100px 500px 1fr 150px; align-items: baseline; padding: 22px 0 20px; border-bottom: 1.5px solid var(--rule); }
.toc .no { font: 500 42px/1 var(--serif); color: var(--ctx); }
.toc .nm { font: 500 38px/1.15 var(--serif); }
.toc .ds { font: 400 23px/1.35 var(--sans); color: var(--muted); padding-right: 24px; }
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
