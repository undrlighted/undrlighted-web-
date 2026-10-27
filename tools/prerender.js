// Escribe en el HTML el texto que pone el JavaScript, para que Google y los buscadores
// con IA lean la página sin ejecutarlo. Se ejecuta después de tools/build.py:
//   node tools/prerender.js
// Abre cada página en Chromium (Playwright) sin GSAP ni fuentes externas, espera a que el
// script pinte los textos y guarda el resultado. Al cargar la web, el script vuelve a pintar
// lo mismo, así que el aspecto y las animaciones no cambian.
const http = require("http");
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const PAGES = JSON.parse(fs.readFileSync(path.join(ROOT, "tools/pages.json"), "utf8"));
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".jpg": "image/jpeg", ".png": "image/png", ".xml": "application/xml" };

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0].split("#")[0]);
  if (p.endsWith("/")) p += "index.html";
  const f = path.join(ROOT, p);
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "Content-Type": TYPES[path.extname(f)] || "application/octet-stream" });
  fs.createReadStream(f).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ reducedMotion: "reduce", viewport: { width: 1280, height: 900 } });
  await ctx.route("**/*", route => {
    const u = route.request().url();
    if (!u.startsWith(base) || /gsap|Flip/.test(u) || route.request().resourceType() === "image") return route.abort();
    return route.continue();
  });
  for (const url of PAGES) {
    const page = await ctx.newPage();
    await page.goto(base + url, { waitUntil: "load" });
    const out = await page.evaluate(() => {
      const H = document.documentElement;
      H.classList.remove("pre");
      if (!H.getAttribute("class")) H.removeAttribute("class");
      document.querySelector("#top").classList.remove("solid");
      return "<!doctype html>\n" + H.outerHTML + "\n";
    });
    const file = url === "/" ? path.join(ROOT, "index.html") : path.join(ROOT, url, "index.html");
    fs.writeFileSync(file, out);
    const text = await page.evaluate(() => document.body.innerText.length);
    console.log(url, "texto visible:", text);
    await page.close();
  }
  await browser.close();
  server.close();
})().catch(e => { console.error(e); process.exit(1); });
