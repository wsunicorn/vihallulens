
/* ---------- Bài toán: (ngữ cảnh, câu hỏi, câu trả lời) → nhãn, rủi ro, tỷ trọng theo đoạn ---------- */
FIGS.task = (svg, api) => {
  const E = DATA.demo[3], ch = E.chunks.slice(0, 4).map(c => c.t.trim());
  const box = (x, y, w, h, col, soft, lab) => { const gg = hidden(svg);
    el('rect', { x, y, width: w, height: h, rx: 10, fill: soft, stroke: col, 'stroke-width': 2 }, gg);
    tx(gg, x + 14, y + 26, lab, { 'font-size': 18, 'font-weight': 700, fill: col }); return gg; };
  // đầu vào
  const CB = box(0, 0, 520, 236, C.ctx, C.ctxSoft, 'NGỮ CẢNH ĐÃ TRUY XUẤT · các đoạn c₁ … cₖ');
  ch.forEach((t, i) => { el('rect', { x: 14, y: 40 + i * 46, width: 492, height: 38, rx: 6, fill: '#fff', stroke: C.ctx, 'stroke-width': 1 }, CB);
    tx(CB, 24, 65 + i * 46, `c${'₁₂₃₄'[i]}  ` + (t.length > 52 ? t.slice(0, t.lastIndexOf(' ', 50)) + '…' : t), { 'font-size': 16 }); });
  const Q = box(0, 252, 520, 74, C.ink, C.paper2, 'CÂU HỎI q');
  tx(Q, 14, 308, E.q, { 'font-size': 18 });
  const R = box(0, 342, 520, 140, C.res, C.resSoft, 'CÂU TRẢ LỜI r CẦN CHẤM · của bất kỳ hệ RAG nào');
  html(R, 14, 376, 492, 104, E.ans.replace('sau đó anh ta đã trở về dinh thự', `<b style="color:${C.bad}">sau đó anh ta đã trở về dinh thự</b>`), 'font-size:16px;line-height:1.35');
  // bộ phát hiện
  const D = hidden(svg), DX = 640;
  el('rect', { x: DX, y: 120, width: 400, height: 260, rx: 16, fill: '#fff', stroke: C.ink, 'stroke-width': 3 }, D);
  tx(D, DX + 200, 158, 'BỘ PHÁT HIỆN', { 'text-anchor': 'middle', 'font-size': 22, 'font-weight': 700 });
  el('rect', { x: DX + 24, y: 178, width: 352, height: 82, rx: 10, fill: C.ctxSoft }, D);
  tx(D, DX + 200, 212, 'Mô hình ngôn ngữ mở, chỉ đọc', { 'text-anchor': 'middle', 'font-size': 19, 'font-weight': 600 });
  tx(D, DX + 200, 240, 'đọc chú ý của r lên từng đoạn của C', { 'text-anchor': 'middle', 'font-size': 17, fill: C.muted });
  el('rect', { x: DX + 24, y: 276, width: 352, height: 82, rx: 10, fill: C.resSoft }, D);
  tx(D, DX + 200, 310, 'Bộ phân loại tuyến tính', { 'text-anchor': 'middle', 'font-size': 19, 'font-weight': 600 });
  tx(D, DX + 200, 338, 'phần duy nhất phải huấn luyện', { 'text-anchor': 'middle', 'font-size': 17, fill: C.muted });
  hov(D, 'Không sinh thêm chữ nào: mô hình đọc lại đúng câu trả lời đã có (teacher forcing), nên chấm được câu trả lời của hệ RAG khác.');
  const arrows = [118, 289, 412].map(y => el('path', { d: `M524 ${y} C 580 ${y}, 590 250, ${DX - 6} 250`, stroke: C.muted, 'stroke-width': 3, fill: 'none' }, svg));
  const aOut = el('path', { d: `M${DX + 404} 250 H 1150`, stroke: C.muted, 'stroke-width': 3, fill: 'none' }, svg);
  // đầu ra
  const O = hidden(svg), OX = 1160;
  tx(O, OX, 26, 'ĐẦU RA', { 'font-size': 18, 'font-weight': 700, fill: C.muted });
  [['trung thực', 'mọi ý đều có trong ngữ cảnh', C.ok], ['nội tại', 'có dựa vào ngữ cảnh nhưng nói sai', C.warn], ['ngoại lai', 'thêm điều ngữ cảnh không có', C.bad]].forEach(([n, d, col], i) => {
    const y = 44 + i * 70, on = i === 2;
    el('rect', { x: OX, y, width: 520, height: 58, rx: 10, fill: on ? col : '#fff', stroke: col, 'stroke-width': 2 }, O);
    tx(O, OX + 18, y + 37, n, { 'font-size': 22, 'font-weight': 700, fill: on ? '#fff' : col });
    tx(O, OX + 150, y + 36, d, { 'font-size': 17, fill: on ? '#fff' : C.muted }); });
  el('rect', { x: OX, y: 268, width: 520, height: 74, rx: 10, fill: '#fff', stroke: C.rule, 'stroke-width': 2 }, O);
  tx(O, OX + 18, 300, 'Điểm rủi ro ∈ [0, 1]', { 'font-size': 19, 'font-weight': 600 });
  tx(O, OX + 18, 328, '= 1 − P(trung thực)', { 'font-size': 16, fill: C.muted });
  tx(O, OX + 500, 322, fmt(E.risk, 3), { 'text-anchor': 'end', 'font-size': 40, 'font-weight': 600, 'font-family': 'var(--serif)', fill: C.bad });
  el('rect', { x: OX, y: 356, width: 520, height: 126, rx: 10, fill: '#fff', stroke: C.rule, 'stroke-width': 2 }, O);
  tx(O, OX + 18, 386, 'Tỷ trọng chú ý trên từng đoạn', { 'font-size': 19, 'font-weight': 600 });
  E.chunks.forEach((c, i) => { const h = c.s / .16 * 70;
    el('rect', { x: OX + 18 + i * 40, y: 470 - h, width: 30, height: h, rx: 3, fill: C.ctx, 'fill-opacity': .3 + .7 * c.s / .16 }, O); });
  // ràng buộc
  const K = hidden(svg);
  ['Không gọi LLM giám khảo', 'Không tinh chỉnh mô hình ngôn ngữ', 'Vừa một GPU T4 16 GB', 'Tiếng Việt, ba lớp nhãn'].forEach((t, i) => {
    el('rect', { x: i * 425, y: 504, width: 405, height: 50, rx: 25, fill: C.ink }, K);
    tx(K, i * 425 + 202, 536, t, { 'text-anchor': 'middle', 'font-size': 19, 'font-weight': 600, fill: '#fff' }); });
  return [
    { cap: 'Đầu vào gồm ba thứ: <b>ngữ cảnh</b> hệ RAG đã truy xuất (chia thành các đoạn), <b>câu hỏi</b>, và <b>câu trả lời</b> cần chấm.', hold: 1.3,
      play: tl => { tl.to([CB, Q, R], { opacity: 1, duration: .35, stagger: .15 }); } },
    { cap: 'Một <b>mô hình ngôn ngữ mở</b> đọc lại cả ba trong một lượt; chỉ có <b>bộ phân loại tuyến tính</b> phía sau là phải huấn luyện.', hold: 1.3,
      play: tl => { arrows.forEach((a, i) => draw(tl, a, .4, i ? '<.08' : '>')); tl.to(D, { opacity: 1, duration: .35 }); } },
    { cap: 'Đầu ra: <b>nhãn ba lớp</b>, <b>điểm rủi ro</b>, và tỷ trọng chú ý trên từng đoạn — cho biết câu trả lời dựa vào đâu.', hold: 1.4,
      play: tl => { draw(tl, aOut, .35); tl.to(O, { opacity: 1, duration: .4 }); } },
    { cap: 'Bốn ràng buộc của đề tài: không gọi mô hình giám khảo, không tinh chỉnh mô hình ngôn ngữ, chạy vừa một card 16 GB, làm cho tiếng Việt với ba lớp nhãn.', hold: .8,
      play: tl => { tl.to(K, { opacity: 1, duration: .4 }); } },
  ];
};

/* ---------- Các hướng phát hiện ảo giác hiện có: bản đồ tham số huấn luyện × chi phí mỗi lần chấm ---------- */
FIGS.map = (svg, api) => {
  const XL = ['gần như 0', 'một lượt bộ mã hóa', 'một lượt đọc mô hình mở', 'một lượt gọi LLM qua API', 'nhiều lượt sinh'];
  const YL = ['không huấn luyện', 'vài tham số đến khoảng một triệu', 'hàng trăm triệu tham số'];
  const X0 = 190, X1 = 1660, Y0 = 470, sx = i => X0 + 152 + i * (X1 - X0 - 304) / 4, sy = j => [414, 262, 100][j];
  const ax = g(svg);
  el('line', { x1: X0, x2: X1, y1: Y0, y2: Y0, stroke: C.ink, 'stroke-width': 2 }, ax);
  el('line', { x1: X0, x2: X0, y1: Y0, y2: 30, stroke: C.ink, 'stroke-width': 2 }, ax);
  XL.forEach((t, i) => tx(ax, sx(i), Y0 + 30, t, { 'text-anchor': 'middle', 'font-size': 17, fill: C.muted }));
  tx(ax, (X0 + X1) / 2, Y0 + 62, 'Chi phí mỗi lần chấm một câu trả lời →', { 'text-anchor': 'middle', 'font-size': 19, 'font-weight': 600 });
  YL.forEach((t, j) => html(ax, 0, sy(j) - 26, X0 - 16, 60, t, 'font-size:17px;line-height:1.25;text-align:right;color:#5E6675'));
  tx(ax, X0 + 10, 22, '↑ Tham số phải huấn luyện', { 'font-size': 19, 'font-weight': 600 });
  const G = [
    { n: 'Đặc trưng bề mặt', w: 'độ dài, trùng lặp từ', i: 0, j: 1, dy: 0, col: C.muted, s: 'Độ dài, tỷ lệ từ trùng ngữ cảnh', l: 'Chỉ nắm được mẫu hình thô, dễ bị lừa khi câu sai chép nhiều từ' },
    { n: 'Bộ mã hóa, NLI', w: 'PhoBERT (2020) · XLM-R (2020)', i: 1, j: 2, dy: 0, col: C.res, s: 'Văn bản ngữ cảnh và câu trả lời', l: 'Cần dữ liệu có nhãn, tinh chỉnh lại khi đổi miền' },
    { n: 'LLM giám khảo', w: 'Zheng và cộng sự (2023)', i: 3, j: 0, dy: 0, col: C.warn, s: 'Văn bản, qua một LLM khác', l: 'Chi phí theo từng lượt, độ trễ mạng, dữ liệu phải rời hệ thống' },
    { n: 'Nhất quán khi lấy mẫu', w: 'SelfCheckGPT (2023)', i: 4, j: 0, dy: 0, col: C.warn, s: 'Nhiều câu trả lời của cùng một mô hình', l: 'Tốn nhiều lượt sinh; nhắm tới tính xác thực hơn là bám ngữ cảnh' },
    { n: 'Trạng thái ẩn', w: 'Azaria và Mitchell (2023)', i: 2, j: 1, dy: -66, col: C.violet, s: 'Biểu diễn ẩn bên trong mô hình', l: 'Cần mô hình mở; khó diễn giải' },
    { n: 'Trọng số chú ý', w: 'Lookback Lens (2024) · ReDeEP (2025)', i: 2, j: 1, dy: 44, col: C.ctx, s: 'Chú ý của câu trả lời lên ngữ cảnh', l: 'Cần mô hình mở và cài đặt chú ý không tối ưu hóa (eager)' },
  ];
  const cards = G.map(o => { const gg = hidden(svg), cx = sx(o.i), cy = sy(o.j) + o.dy, w = 284, h = 92;
    el('rect', { x: cx - w / 2, y: cy - h / 2, width: w, height: h, rx: 12, fill: '#fff', stroke: o.col, 'stroke-width': 3 }, gg);
    tx(gg, cx, cy - 16, o.n, { 'text-anchor': 'middle', 'font-size': 21, 'font-weight': 700, fill: o.col === C.muted ? C.ink : o.col });
    html(gg, cx - w / 2 + 8, cy - 4, w - 16, 44, o.w, 'font-size:15px;line-height:1.3;text-align:center;color:#5E6675');
    hov(gg, `<b>${o.n}</b><br>Tín hiệu: ${o.s}<br>Hạn chế: ${o.l}`); gg.c = [cx, cy]; return gg; });
  const ring = hidden(svg), [cx, cy] = cards[5].c;
  el('rect', { x: cx - 166, y: cy - 54, width: 332, height: 108, rx: 18, fill: 'none', stroke: C.ctx, 'stroke-width': 3, 'stroke-dasharray': '9 7' }, ring);
  html(ring, cx + 180, cy - 96, 300, 120, `<b style="color:${C.ctx}">Vị trí của khóa luận</b><br>không tinh chỉnh, không gọi API — nhưng còn ít được nghiên cứu, và <b>chưa có cho tiếng Việt</b>`, 'font-size:17px;line-height:1.35');
  return [
    { cap: 'Hướng <b>dựa trên văn bản</b>: đặc trưng bề mặt rất rẻ nhưng thô; bộ mã hóa tinh chỉnh chính xác nhưng phải huấn luyện hàng trăm triệu tham số.', hold: 1.4,
      play: tl => { tl.to([cards[0], cards[1]], { opacity: 1, duration: .35, stagger: .2 }); } },
    { cap: 'Hướng <b>dựa trên LLM</b>: không phải huấn luyện, nhưng mỗi lần chấm là một lượt gọi mô hình khác, hoặc nhiều lượt sinh.', hold: 1.4,
      play: tl => { tl.to([cards[2], cards[3]], { opacity: 1, duration: .35, stagger: .2 }); } },
    { cap: 'Hướng <b>dựa trên trạng thái nội tại</b>: chỉ một lượt đọc và một bộ phân loại nhỏ. Lookback Lens đọc trọng số chú ý; Azaria và Mitchell đọc trạng thái ẩn.', hold: 1.4,
      play: tl => { tl.to([cards[4], cards[5]], { opacity: 1, duration: .35, stagger: .2 }); } },
    { cap: 'Khóa luận thuộc nhóm <b>trọng số chú ý</b>: tách tỷ lệ chú ý theo từng đoạn và áp dụng lần đầu cho tiếng Việt.', hold: .8,
      play: tl => { tl.to(ring, { opacity: 1, duration: .4 }); } },
  ];
};

/* ---------- Tự đánh giá: kiểm định năm giả thuyết ---------- */
FIGS.hyp = (svg, api) => {
  const H = [
    ['H1', 'Lookback gộp vượt đặc trưng bề mặt, ngang bộ mã hóa tinh chỉnh', '0,745 so với 0,656 của đặc trưng bề mặt; ngang PhoBERT 0,749; thấp hơn XLM-R 0,776 nhưng khoảng tin cậy chồng nhau; cộng thêm +0,109 vào đặc trưng bề mặt', 'Được ủng hộ', C.ok, 'CH2, CH3 · E01, E02, E09, E12'],
    ['H2', 'Chunk-aware tăng macro-F1, tăng nhiều hơn trên ngữ cảnh dài', '+0,012 nằm trong khoảng tin cậy; chỉ +0,007 trên ngữ cảnh dài; dấu đổi chiều theo mô hình đọc; 99,9 % tín hiệu trùng tỷ lệ gộp', 'Không được ủng hộ', C.bad, 'CH1 · E03–E05, E07, E12–E15'],
    ['H3', 'Đầu chú ý mạnh nhất nhìn đúng đoạn chứa bằng chứng', 'Trúng 87,8 %, gấp 14,3 lần mức ngẫu nhiên; lặp lại trên ViWikiFC', 'Được ủng hộ', C.ok, 'CH1 · E06, E08'],
    ['H4', 'Bỏ câu bằng chứng làm chú ý tản ra theo hướng dự đoán trước', 'Cả bốn đặc trưng đổi đúng hướng ở 71–75 % số cặp; độ thay đổi nhỏ', 'Ủng hộ về hướng, độ lớn nhỏ', C.warn, 'CH1 · E08'],
    ['H5', 'Bộ phát hiện giữ hiệu năng trên bộ dữ liệu khác', 'Ba lớp sụt 0,19–0,43; nhị phân chéo bộ vẫn đạt 0,63–0,78', 'Bác bỏ ở ba lớp, ủng hộ một phần ở nhị phân', C.warn, 'CH3 · E15, E16'],
  ];
  const hd = g(svg);
  [['Giả thuyết', 80], ['Bằng chứng chính', 760], ['Kết luận', 1400]].forEach(([t, x]) => tx(hd, x, 20, t, { 'font-size': 18, 'font-weight': 700, fill: C.muted }));
  const rows = H.map(([id, st, ev, vd, col, tip], i) => { const y = 34 + i * 105, gg = hidden(svg);
    el('rect', { x: 0, y, width: 1680, height: 95, rx: 10, fill: '#fff', stroke: C.rule, 'stroke-width': 1.5 }, gg);
    el('circle', { cx: 36, cy: y + 47, r: 26, fill: C.ink }, gg);
    tx(gg, 36, y + 55, id, { 'text-anchor': 'middle', 'font-size': 20, 'font-weight': 700, fill: '#fff' });
    html(gg, 80, y + 12, 650, 76, st, 'font-size:21px;line-height:1.3;font-weight:600');
    html(gg, 760, y + 12, 610, 76, ev, 'font-size:18px;line-height:1.35;color:#5E6675');
    const stamp = g(gg);
    el('rect', { x: 1396, y: y + 14, width: 270, height: 66, rx: 10, fill: col }, stamp);
    html(stamp, 1404, y + 18, 254, 60, vd, 'font-size:17px;line-height:1.25;font-weight:700;color:#fff;text-align:center;display:flex;align-items:center;justify-content:center;height:58px');
    hov(gg, `<b>${id}</b> · ${tip}`); gg.stamp = stamp; return gg; });
  const show = (tl, list) => list.forEach((r, k) => { tl.to(r, { opacity: 1, duration: .3 }, k ? '<.15' : '>');
    tl.fromTo(r.stamp, { opacity: 0, scale: 1.2, transformOrigin: '1531px 50%' }, { opacity: 1, scale: 1, duration: .3, ease: 'back.out(2)' }); });
  return [
    { cap: '<b>H1</b> được ủng hộ: chỉ một bộ phân loại tuyến tính trên tỷ lệ chú ý đã vượt đặc trưng bề mặt và ngang PhoBERT tinh chỉnh.', hold: 1.3, play: tl => show(tl, [rows[0]]) },
    { cap: '<b>H2</b> — giả thuyết chính về chunk-aware — <b>không</b> được ủng hộ: mức tăng nằm trong vùng nhiễu. Nhóm trình bày thẳng kết quả này.', hold: 1.5, play: tl => show(tl, [rows[1]]) },
    { cap: '<b>H3, H4</b> được ủng hộ: chú ý theo đoạn chỉ đúng chỗ chứa bằng chứng và phản ứng đúng hướng khi bằng chứng bị thay.', hold: 1.4, play: tl => show(tl, [rows[2], rows[3]]) },
    { cap: '<b>H5</b> bác bỏ ở bài toán ba lớp; quyết định “có ảo giác hay không” thì chuyển được sang bộ dữ liệu khác.', hold: .8, play: tl => show(tl, [rows[4]]) },
  ];
};
