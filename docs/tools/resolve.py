"""Assemble the chapter drafts into docs/BaoCao_KLTN.md.

Drafts use labels instead of numbers:
  headings   ## [[sec:key]] Title          -> ## 3.4 Title
  captions   *[[fig:key]] Caption*         -> *Hình 3.2 Caption*   (Bảng for tab)
  equations  \\tag{[[eq:key]]}              -> \\tag{3.5}
  references [[fig:key]] [[tab:key]] [[eq:key]] [[sec:key]]
  citations  [@key] or [@a; @b]             -> [n] / [n1], [n2]
Numbers follow order of appearance inside each chapter (appendix letters A, B, ...).
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1]
SRC = DOCS / "report"
OUT = DOCS / "BaoCao_KLTN.md"
MEDIA = DOCS / "media"
PAGEBREAK = '<div style="page-break-after: always"></div>'

BIB = {
    "azaria2023": ('Azaria, A., Mitchell, T. (2023), "The Internal State of an LLM Knows When '
                   'It\'s Lying", *Findings of the Association for Computational Linguistics: '
                   'EMNLP 2023*, pp. 967–976.'),
    "cohenwang2024": ('Cohen-Wang, B., Shah, H., Georgiev, K., Madry, A. (2024), "ContextCite: '
                      'Attributing Model Generation to Context", *Advances in Neural Information '
                      'Processing Systems* 37, arXiv:2409.00729.'),
    "chi2021": ('Chi, Z., Dong, L., Wei, F., Yang, N., Singhal, S., Wang, W., Song, X., Mao, '
                'X.-L., Huang, H., Zhou, M. (2021), "InfoXLM: An Information-Theoretic Framework '
                'for Cross-Lingual Language Model Pre-Training", *Proceedings of NAACL-HLT '
                '2021*, pp. 3576–3588.'),
    "chuang2024": ('Chuang, Y.-S., Qiu, L., Hsieh, C.-Y., Krishna, R., Kim, Y., Glass, J. '
                   '(2024), "Lookback Lens: Detecting and Mitigating Contextual Hallucinations '
                   'in Large Language Models Using Only Attention Maps", *Proceedings of EMNLP '
                   '2024*, pp. 1419–1436.'),
    "conneau2020": ('Conneau, A., Khandelwal, K., Goyal, N., Chaudhary, V., Wenzek, G., Guzmán, '
                    'F., Grave, E., Ott, M., Zettlemoyer, L., Stoyanov, V. (2020), "Unsupervised '
                    'Cross-lingual Representation Learning at Scale", *Proceedings of ACL 2020*, '
                    'pp. 8440–8451.'),
    "dao2022": ('Dao, T., Fu, D. Y., Ermon, S., Rudra, A., Ré, C. (2022), "FlashAttention: Fast '
                'and Memory-Efficient Exact Attention with IO-Awareness", *Advances in Neural '
                'Information Processing Systems* 35, pp. 16344–16359.'),
    "dettmers2023": ('Dettmers, T., Pagnoni, A., Holtzman, A., Zettlemoyer, L. (2023), "QLoRA: '
                     'Efficient Finetuning of Quantized LLMs", *Advances in Neural Information '
                     'Processing Systems* 36, arXiv:2305.14314.'),
    "dou2025": ('Dou, L., et al. (2025), "Sailor2: Sailing in South-East Asia with Inclusive '
                'Multilingual LLMs", arXiv:2502.12982.'),
    "gao2023rag": ('Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., '
                   'Wang, M., Wang, H. (2023), "Retrieval-Augmented Generation for Large '
                   'Language Models: A Survey", arXiv:2312.10997.'),
    "guo2017": ('Guo, C., Pleiss, G., Sun, Y., Weinberger, K. Q. (2017), "On Calibration of '
                'Modern Neural Networks", *Proceedings of ICML 2017*, pp. 1321–1330.'),
    "huang2025": ('Huang, L., Yu, W., Ma, W., Zhong, W., Feng, Z., Wang, H., Chen, Q., Peng, W., '
                  'Feng, X., Qin, B., Liu, T. (2025), "A Survey on Hallucination in Large '
                  'Language Models: Principles, Taxonomy, Challenges, and Open Questions", *ACM '
                  'Transactions on Information Systems* 43 (2), pp. 1–55.'),
    "jain2019": ('Jain, S., Wallace, B. C. (2019), "Attention is not Explanation", *Proceedings '
                 'of NAACL-HLT 2019*, pp. 3543–3556.'),
    "ji2023": ('Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y. J., '
               'Madotto, A., Fung, P. (2023), "Survey of Hallucination in Natural Language '
               'Generation", *ACM Computing Surveys* 55 (12), pp. 1–38.'),
    "kerby2014": ('Kerby, D. S. (2014), "The Simple Difference Formula: An Approach to Teaching '
                  'Nonparametric Correlation", *Comprehensive Psychology* 3, 11.IT.3.1.'),
    "landis1977": ('Landis, J. R., Koch, G. G. (1977), "The Measurement of Observer Agreement '
                   'for Categorical Data", *Biometrics* 33 (1), pp. 159–174.'),
    "le2024": ('Le, H. T., To, L. T., Nguyen, M. T., Nguyen, K. V. (2024), "ViWikiFC: '
               'Fact-Checking for Vietnamese Wikipedia-Based Textual Knowledge Source", '
               'arXiv:2405.07615.'),
    "li2026arcjsd": ('Li, R., Chen, C., Hu, Y., Gao, Y., Wang, X., Yilmaz, E. (2026), '
                     '"Attributing Response to Context: A Jensen–Shannon Divergence Driven '
                     'Mechanistic Study of Context Attribution in Retrieval-Augmented '
                     'Generation", *Proceedings of ICLR 2026*, arXiv:2505.16415.'),
    "lewis2020": ('Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., '
                  'Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., Kiela, D. '
                  '(2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", '
                  '*Advances in Neural Information Processing Systems* 33, pp. 9459–9474.'),
    "manakul2023": ('Manakul, P., Liusie, A., Gales, M. J. F. (2023), "SelfCheckGPT: '
                    'Zero-Resource Black-Box Hallucination Detection for Generative Large '
                    'Language Models", *Proceedings of EMNLP 2023*, pp. 9004–9017.'),
    "maynez2020": ('Maynez, J., Narayan, S., Bohnet, B., McDonald, R. (2020), "On Faithfulness '
                   'and Factuality in Abstractive Summarization", *Proceedings of ACL 2020*, pp. '
                   '1906–1919.'),
    "naeini2015": ('Naeini, M. P., Cooper, G. F., Hauskrecht, M. (2015), "Obtaining Well '
                   'Calibrated Probabilities Using Bayesian Binning", *Proceedings of AAAI '
                   '2015*, pp. 2901–2907.'),
    "nguyen2020phobert": ('Nguyen, D. Q., Nguyen, A. T. (2020), "PhoBERT: Pre-trained Language '
                          'Models for Vietnamese", *Findings of EMNLP 2020*, pp. 1037–1042.'),
    "nguyen2026vihallu": ('Nguyen, A. T.-H., Tran, K. Q., Huynh, T. V., Nguyen, P. T.-H., '
                          'Nguyen, C. T., Nguyen, K. V. (2026), "DSC2025 – ViHallu Challenge: '
                          'Detecting Hallucination in Vietnamese LLMs", arXiv:2601.04711.'),
    "ogasa2025": ('Ogasa, Y., Arase, Y. (2025), "Hallucinated Span Detection with Multi-View '
                  'Attention Features", arXiv:2504.04335.'),
    "qwen2025": 'Qwen Team (2024), *Qwen2.5 Technical Report*, arXiv:2412.15115.',
    "robertson2009": ('Robertson, S., Zaragoza, H. (2009), "The Probabilistic Relevance '
                      'Framework: BM25 and Beyond", *Foundations and Trends in Information '
                      'Retrieval* 3 (4), pp. 333–389.'),
    "sun2025redeep": ('Sun, Z., Zang, X., Zheng, K., Song, Y., Xu, J., Zhang, X., Yu, W., Song, '
                      'Y., Li, H. (2025), "ReDeEP: Detecting Hallucination in '
                      'Retrieval-Augmented Generation via Mechanistic Interpretability", '
                      '*Proceedings of ICLR 2025*, arXiv:2410.11414.'),
    "thorne2018": ('Thorne, J., Vlachos, A., Christodoulopoulos, C., Mittal, A. (2018), "FEVER: '
                   'a Large-scale Dataset for Fact Extraction and VERification", *Proceedings of '
                   'NAACL-HLT 2018*, pp. 809–819.'),
    "tran2025semviqa": ('Tran, D. X., Nguyen, N. V., Tran, T. T., Hoang, A. T., Duong, T. V., '
                        'Le, D. T., Le, P.-L. (2025), "SemViQA: A Semantic Question Answering '
                        'System for Vietnamese Information Fact-Checking", arXiv:2503.00955.'),
    "tran2025vifactcheck": ('Tran, T.-H., Tran, Q.-D., Tran, K. Q., Nguyen, K. V. (2025), '
                            '"ViFactCheck: A New Benchmark Dataset and Methods for Multi-domain '
                            'News Fact-Checking in Vietnamese", *Proceedings of the AAAI '
                            'Conference on Artificial Intelligence* 39 (1), pp. 308–316.'),
    "uitdsc2023": ('UIT Data Science Challenge 2023, Group B – UIT Data Science Challenge 2023 '
                   '(10-2023), https://codalab.lisn.upsaclay.fr/competitions/15497'),
    "vaswani2017": ('Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. '
                    'N., Kaiser, Ł., Polosukhin, I. (2017), "Attention Is All You Need", '
                    '*Advances in Neural Information Processing Systems* 30, pp. 5998–6008.'),
    "vazquez2025": ('Vázquez, R., et al. (2025), "SemEval-2025 Task 3: Mu-SHROOM, the '
                    'Multilingual Shared-task on Hallucinations and Related Observable '
                    'Overgeneration Mistakes", *Proceedings of SemEval-2025*, pp. 2472–2497.'),
    "wiegreffe2019": ('Wiegreffe, S., Pinter, Y. (2019), "Attention is not not Explanation", '
                      '*Proceedings of EMNLP-IJCNLP 2019*, pp. 11–20.'),
    "yeh2026lumina": ('Yeh, S., Li, S., Mallick, T. (2026), "LUMINA: Detecting Hallucinations in '
                      'RAG System with Context-Knowledge Signals", *Proceedings of ICLR 2026*, '
                      'arXiv:2509.21875.'),
    "zheng2023judge": ('Zheng, L., et al. (2023), "Judging LLM-as-a-Judge with MT-Bench and '
                       'Chatbot Arena", *Advances in Neural Information Processing Systems* 36.'),
}

LABEL_RX = re.compile(r"\[\[(fig|tab|eq|sec):([\w-]+)\]\]")
CAPTION_RX = re.compile(r"^\*\[\[(fig|tab):([\w-]+)\]\] (.+)\*\s*$")
TAG_RX = re.compile(r"\\tag\{\[\[eq:([\w-]+)\]\]\}")
CITE_RX = re.compile(r"\[(@[\w-]+(?:;\s*@[\w-]+)*)\]")


def fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


def main() -> None:
    files = sorted(SRC.glob("0*.md"))
    chunks = []
    for k, f in enumerate(files):
        body = f.read_text(encoding="utf-8").rstrip()
        if k > 0 and not body.endswith(PAGEBREAK) and f.name != files[-1].name:
            body += "\n\n" + PAGEBREAK
        chunks.append(body)
    text = "\n\n".join(chunks) + "\n"
    lines = text.split("\n")

    # ---------------------------------------------------------- pass 1: numbers
    numbers: dict[tuple[str, str], str] = {}
    captions: list[tuple[str, str, str]] = []      # kind, number, caption text
    headings: list[tuple[int, str]] = []           # level, rendered text
    chapter: str | None = None
    n2 = n3 = 0
    counters: dict[tuple[str, str], int] = {}
    first_seen: dict[tuple[str, str], int] = {}
    in_appendix = False
    sub_counts: dict[str, int] = {}
    for idx, line in enumerate(lines):
        m = re.match(r"^# (.+?)(?: \{[^}]*\})?\s*$", line)
        if m:
            title = m.group(1)
            cm = re.match(r"CHƯƠNG (\d+) ", title)
            if cm:
                chapter, n2, n3, in_appendix = cm.group(1), 0, 0, False
            elif title.startswith("PHỤ LỤC"):
                chapter, in_appendix = None, True
            else:
                chapter, in_appendix = None, False
            headings.append((1, title))
            continue
        m = re.match(r"^## (.+)$", line)
        if m:
            am = re.match(r"Phụ lục ([A-Z]) ", m.group(1))
            if in_appendix and am:
                chapter = am.group(1)
                headings.append((2, m.group(1)))
                continue
            sm = re.match(r"\[\[sec:([\w-]+)\]\] (.+)$", m.group(1))
            if sm:
                n2 += 1
                n3 = 0
                num = f"{chapter}.{n2}"
                numbers[("sec", sm.group(1))] = num
                headings.append((2, f"{num} {sm.group(2)}"))
                sub_counts[num] = 0
            continue
        m = re.match(r"^### \[\[sec:([\w-]+)\]\] (.+)$", line)
        if m:
            n3 += 1
            num = f"{chapter}.{n2}.{n3}"
            numbers[("sec", m.group(1))] = num
            headings.append((3, f"{num} {m.group(2)}"))
            sub_counts[f"{chapter}.{n2}"] += 1
            continue
        m = CAPTION_RX.match(line)
        if m:
            kind, key, cap = m.groups()
            if chapter is None:
                sys.exit(f"chú thích ngoài chương: {line}")
            counters[(kind, chapter)] = counters.get((kind, chapter), 0) + 1
            num = f"{chapter}.{counters[(kind, chapter)]}"
            if (kind, key) in numbers:
                sys.exit(f"nhãn trùng: {kind}:{key}")
            numbers[(kind, key)] = num
            captions.append((kind, num, cap))
            first_seen[(kind, key)] = idx
            continue
        for tm in TAG_RX.finditer(line):
            counters[("eq", chapter)] = counters.get(("eq", chapter), 0) + 1
            numbers[("eq", tm.group(1))] = f"{chapter}.{counters[('eq', chapter)]}"
            first_seen[("eq", tm.group(1))] = idx

    # template rule: a section that has sub-sections has at least two
    for sec, n in sub_counts.items():
        if n == 1:
            print(f"CẢNH BÁO: mục {sec} chỉ có 1 tiểu mục")

    # ---------------------------------------------------------- checks on refs
    refs: dict[tuple[str, str], list[int]] = {}
    for idx, line in enumerate(lines):
        if CAPTION_RX.match(line) or TAG_RX.search(line) or re.match(r"^#{2,3} \[\[sec:", line):
            continue
        for m in LABEL_RX.finditer(line):
            refs.setdefault((m.group(1), m.group(2)), []).append(idx)
    missing = [f"{k}:{v}" for (k, v) in refs if (k, v) not in numbers]
    if missing:
        sys.exit("tham chiếu tới nhãn không tồn tại: " + ", ".join(sorted(set(missing))))
    for (kind, key), num in numbers.items():
        if kind in ("fig", "tab"):
            where = refs.get((kind, key))
            if not where:
                print(f"CẢNH BÁO: {kind}:{key} ({num}) không được nhắc trong văn bản")
            elif min(where) > first_seen[(kind, key)]:
                print(f"LƯU Ý: {kind}:{key} ({num}) được nhắc lần đầu sau khi xuất hiện")

    # ---------------------------------------------------------- citations
    cited: list[str] = []
    for m in CITE_RX.finditer(text):
        for key in re.findall(r"@([\w-]+)", m.group(1)):
            if key not in BIB:
                sys.exit(f"trích dẫn không có trong danh mục: {key}")
            if key not in cited:
                cited.append(key)
    unused = sorted(set(BIB) - set(cited))
    if unused:
        print("không được trích dẫn (bỏ khỏi danh mục):", ", ".join(unused))
    order = sorted(cited, key=lambda k: (fold(BIB[k]), k))
    cite_no = {k: i + 1 for i, k in enumerate(order)}

    def cite_sub(m: re.Match) -> str:
        keys = re.findall(r"@([\w-]+)", m.group(1))
        return ", ".join(f"[{cite_no[k]}]" for k in keys)

    # ---------------------------------------------------------- pass 2: render
    def label_sub(m: re.Match) -> str:
        kind, key = m.groups()
        num = numbers[(kind, key)]
        return {"fig": f"Hình {num}", "tab": f"Bảng {num}"}.get(kind, num)

    out = LABEL_RX.sub(label_sub, text)
    out = CITE_RX.sub(cite_sub, out)

    toc = []
    for level, title in headings:
        if (title in ("ABSTRACT", "TÓM TẮT", "LỜI CẢM ƠN", "MỤC LỤC")
                or title.startswith("NHẬN XÉT")):
            continue
        toc.append(f"**{title}**" if level == 1 and title.startswith("CHƯƠNG") else title)
    out = out.replace("@@GEN_TOC@@", "\n\n".join(toc))
    lof = [f"Hình {num} {cap}" for kind, num, cap in captions if kind == "fig"]
    lot = [f"Bảng {num} {cap}" for kind, num, cap in captions if kind == "tab"]
    out = out.replace("@@GEN_LOF@@", "\n\n".join(lof))
    out = out.replace("@@GEN_LOT@@", "\n\n".join(lot))
    refs_md = ["**Tiếng Anh**", ""] + [f"[{cite_no[k]}]. {BIB[k]}\n" for k in order]
    out = out.replace("@@GEN_REFS@@", "\n".join(refs_md).rstrip())

    leftover = re.findall(r"\[\[[^\]]+\]\]|@@GEN_\w+@@|\[@[\w-]+", out)
    if leftover:
        sys.exit(f"còn nhãn chưa thay: {leftover[:10]}")

    # images that do not exist yet
    for img in re.findall(r"!\[[^\]]*\]\((media/[^)]+)\)", out):
        if not (OUT.parent / img).exists():
            print("thiếu ảnh:", img)

    OUT.write_text(out, encoding="utf-8")
    n_fig = sum(1 for c in captions if c[0] == "fig")
    n_tab = sum(1 for c in captions if c[0] == "tab")
    n_eq = sum(1 for k in numbers if k[0] == "eq")
    print(f"OK -> {OUT}  |  {n_fig} hình, {n_tab} bảng, {n_eq} công thức, {len(order)} tài liệu, "
          f"{len(out.splitlines())} dòng")


if __name__ == "__main__":
    main()
