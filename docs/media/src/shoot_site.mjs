#!/usr/bin/env node
// Re-shoot the report's landing-page figures in the light theme, over the DevTools
// protocol (Node 22+, no dependencies). Each shot may run a snippet in the page first —
// the demo figures need a preset or a RAG question clicked — then scroll and capture.
//
//   node docs/media/src/shoot_site.mjs --out docs/media [--only name,name] [--probe]
//
// The replay service has to be running first — see docs/report/README.md.
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const argv = process.argv.slice(2);
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const out = opt("--out", "shots");
const only = (opt("--only", "") || "").split(",").filter(Boolean);
const probe = argv.includes("--probe");
const BASE = "http://127.0.0.1:8000/?theme=light&noboot";
const urlFor = (s) => (s.url ? "http://127.0.0.1:8000" + s.url : BASE + (s.q || ""));

// The page keeps its content in a ~1.070 px column, so a 1.100 px viewport loses only the
// side margins: printed 15,5 cm wide, a CSS px is then 0,39 pt instead of the 0,27 pt a
// 1.568 px shot gave (text went from ~4 pt to ~6 pt). Shot at twice the pixel density so
// the smaller viewport still prints sharp.
const W = Number(opt("--width", "780"));
const SCALE = Number(opt("--scale", "2"));
const clickRag = (i) => `document.querySelectorAll('#rag-examples button')[${i}].click(); await sleep(2200);`;
const preset = (i) => `document.querySelectorAll('#examples button')[${i}].click(); await sleep(900);`;

// the hero is a sticky scroll story; ?p=1 pins its last beat — the title card and the
// whole owl — so the shot does not depend on where a scroll animation happened to land

const top = (id) => `document.getElementById('${id}').getBoundingClientRect().top + window.scrollY`;

const topOf = (sel) => `document.querySelector('${sel}').getBoundingClientRect().top + window.scrollY`;

// Printed 15,5 cm wide, a CSS px of a 780 px viewport is 0,56 pt: the page's 16 px body
// text prints at 9 pt (it was 6,4 pt from the 1.100 px viewport). Below 900 px the demo
// falls to one column and below 860 px the three "cách dùng" cards stack, so every shot is
// cut (clip) to the block its caption talks about instead of to a fixed window height.
// h only has to be tall enough to hold that block under the sticky nav bar.
const span = (first, last, pad = 14, maxH = 0) => `(() => {
  const a = document.querySelector('${first}').getBoundingClientRect();
  const b = document.querySelector('${last}').getBoundingClientRect();
  const y = a.top - ${pad} + window.scrollY;
  let height = b.bottom - a.top + 2 * ${pad};
  if (${maxH} && height > ${maxH}) height = ${maxH};
  return { x: 0, y, width: document.documentElement.clientWidth, height }; })()`;
// at 780 px the nav links wrap onto a second line, so the sticky bar is ~70 px tall
const under = (sel, gap = 104) => `${topOf(sel)} - ${gap}`;

const SHOTS = [
  // The hero keeps the desktop layout (card beside the owl): narrower than ~1.000 px the
  // card runs off the left edge, and under 860 px it drops below the owl and the frame is
  // mostly black stage. So it is shot at 1.100 px and cut to the card and the owl.
  { name: "anh_trang_chu_hero", w: 1100, h: 746, q: "&p=1", scroll: "0",
    clip: `(() => { const r = document.getElementById('intro').getBoundingClientRect();
      const x = Math.max(0, r.left - 26);
      return { x, y: 92, width: 940 - x, height: 746 - 92 }; })()` },
  { name: "anh_trang_chu_chunk_aware", h: 700, scroll: under("#chunk .compare"),
    clip: span("#chunk .compare", "#chunk .compare") },
  { name: "anh_ba_cach_dung", h: 1500, scroll: under("#system .eyebrow"),
    clip: span("#system .eyebrow", "#system .grid3") },
  { name: "anh_demo_rag", h: 1300, act: clickRag(1), scroll: under("#demo .eyebrow"),
    clip: span("#demo .eyebrow", "#rag-out") },
  // the question and answer are in the figure just before, so this one is the result card
  // down to the colour legend
  { name: "anh_giao_dien_quan_sat", h: 1100, act: clickRag(1), scroll: under("#result"),
    clip: span("#result", "#result .legend", 12) },
  // the question, the answer being scored, and the verdict with the ranked chunks
  { name: "anh_phat_hien_ngoai_lai", h: 1400, act: preset(2), scroll: under('label[for="question"]'),
    clip: span('label[for="question"]', "#chunks", 14) },
  // FastAPI's own OpenAPI page (Swagger UI) of the same service
  { name: "anh_tai_lieu_rest_api", h: 545, url: "/docs", scroll: "0" },
];

const CANDIDATES = [process.env.CHROME_PATH, "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"];
const browser = CANDIDATES.find((p) => p && existsSync(p));
if (!browser) { console.error("no Chrome found"); process.exit(2); }

const profile = mkdtempSync(join(tmpdir(), "vhl-shoot-"));
const proc = spawn(browser, ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
  "--no-default-browser-check", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
const cleanup = () => { try { proc.kill(); } catch { } setTimeout(() => { try { rmSync(profile, { recursive: true, force: true }); } catch { } }, 300); };

try {
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = "";
    const t = setTimeout(() => reject(new Error("no DevTools URL in 20 s")), 20000);
    proc.stderr.on("data", (d) => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) { clearTimeout(t); resolve(m[1]); } });
    proc.on("exit", (c) => reject(new Error(`browser exited early (${c})`)));
  });
  const ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let nextId = 0; const pending = new Map(); const listeners = new Set();
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const { resolve, reject } = pending.get(m.id); pending.delete(m.id); m.error ? reject(new Error(m.error.message)) : resolve(m.result); }
    else listeners.forEach((fn) => fn(m));
  };
  const send = (method, params = {}, sessionId) => new Promise((resolve, reject) => {
    const id = ++nextId; pending.set(id, { resolve, reject }); ws.send(JSON.stringify({ id, method, params, sessionId }));
  });
  const nextEv = (method, sessionId, ms = 30000) => new Promise((resolve, reject) => {
    const t = setTimeout(() => { listeners.delete(fn); reject(new Error(`timeout ${method}`)); }, ms); t.unref?.();
    const fn = (m) => { if (m.method === method && m.sessionId === sessionId) { clearTimeout(t); listeners.delete(fn); resolve(m.params); } };
    listeners.add(fn);
  });
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  await send("Page.enable", {}, sessionId);
  await send("Runtime.enable", {}, sessionId);
  const evalIn = async (expression, awaitPromise = true) => {
    const r = await send("Runtime.evaluate", { expression, awaitPromise, returnByValue: true }, sessionId);
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
    return r.result.value;
  };

  mkdirSync(out, { recursive: true });
  for (const s of SHOTS) {
    if (only.length && !only.includes(s.name)) continue;
    const w = s.w || W;
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: s.h, deviceScaleFactor: SCALE, mobile: false }, sessionId);
    const loaded = nextEv("Page.loadEventFired", sessionId).catch((e) => e);
    await send("Page.navigate", { url: urlFor(s) }, sessionId);
    await loaded;
    await sleep(2500);                                  // health probe + replay.json + examples
    // the first load of a cold service can still read "đang kiểm dịch vụ…": wait it out
    await evalIn(`(async () => { const el = document.getElementById('health-text');
      for (let k = 0; el && k < 40 && el.textContent.includes('đang kiểm'); k++)
        await new Promise(r => setTimeout(r, 150)); })()`);
    // the mascot's speech bubble drifts over the text, and the corner companion (the small
    // owl and its "ẩn cú" button) sits on top of whatever is bottom right
    await evalIn(`(() => { const st = document.createElement('style');
      // The page writes its attention colour as hsla(var(--attn), a) with --attn holding a
      // space-separated "h s l": that mixes the two colour syntaxes, the browser drops the
      // declaration, and the per-chunk bars and the "ít … nhiều" legend come out empty. The
      // shot restates the two gradients in valid syntax; the page source is left alone.
      st.textContent = '#bubble, #buddy, #buddy-off { display: none !important; }'
        + ' .bars:not(.one) .b { background: linear-gradient(180deg, hsl(var(--attn) / .85), hsl(var(--attn) / .35)) !important; }'
        + ' .legend .grad { background: linear-gradient(90deg, hsl(var(--attn) / .05), hsl(var(--attn) / .85)) !important; }';
      document.head.appendChild(st); })()`, false);
    if (s.act) await evalIn(`(async () => { const sleep = (ms) => new Promise(r => setTimeout(r, ms)); ${s.act} })()`);
    const y = await evalIn(`(async () => {
      const sleep = (ms) => new Promise(r => setTimeout(r, ms));
      const y = Math.max(0, Math.round(${s.scroll}));
      window.scrollTo(0, y); await sleep(1400); window.scrollTo(0, y); await sleep(900);
      return Math.round(window.scrollY);
    })()`);
    if (probe) {
      const geo = await evalIn(`JSON.stringify(Object.fromEntries(['hero','problem','how','chunk','numbers','honest','demo','system','result']
        .map(id => [id, (document.getElementById(id) || {offsetTop: -1}).offsetTop])))`);
      console.log("  geometry:", geo);
    }
    const shot = { format: "png" };
    if (s.clip) {                  // CDP clips in page coordinates, not viewport ones
      const c = await evalIn(s.clip, false);
      shot.clip = { x: c.x, y: c.y, width: c.width, height: c.height, scale: 1 };
    }
    const { data } = await send("Page.captureScreenshot", shot, sessionId);
    writeFileSync(join(out, `${s.name}.png`), Buffer.from(data, "base64"));
    console.log(`${s.name.padEnd(28)} ${w}×${s.h} @${SCALE}x  scrollY=${y}`);
  }
} finally { cleanup(); }
