"""Parche sobre el HTML YA DESPLEGADO de Playbooks Tácticos (no parte del archivo original).

  1) Validación y saneado del .json al importar (y al restaurar del navegador).
  2) Recordatorio de copia de seguridad (fecha de la última copia + botón resaltado).
  3) Hash de integridad (SRI) para html2canvas cargado desde el CDN.

Uso:  python3 -I 2026-11-copias-y-seguridad.py <entrada.html> <salida.html>
Cada reemplazo exige EXACTAMENTE una coincidencia: si la app cambia, el script se detiene.
"""
import json
import re
import sys

SRI = "sha384-ZZ1pncU3bQe8y31yfZdMFdSpttDoPmOZg2wguVK9almUodir1PghgT0eY7Mrty8H"  # html2canvas 1.4.1


def rep(t, old, new, label):
    n = t.count(old)
    if n != 1:
        raise SystemExit("[%s] esperaba 1 coincidencia y hay %d" % (label, n))
    return t.replace(old, new)


NEW_METHODS = r'''  normalizeData(raw) {
    const fail = m => { throw new Error(m); };
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) fail("el archivo no parece un playbook.");
    if (!raw.meta || typeof raw.meta !== "object" || Array.isArray(raw.meta)) fail("falta la sección «meta» (datos del partido).");
    if (!Array.isArray(raw.blocks)) fail("falta la lista de bloques («blocks»).");
    let badImages = 0;
    const IMG_OK = /^data:image\/(png|jpe?g|gif|webp|svg\+xml)[;,][^\s"'()<>\\]*$/;
    const img = v => { if (typeof v !== "string" || v === "") return ""; if (IMG_OK.test(v)) return v; badImages++; return ""; };
    const merge = (def, val) => {
      if (Array.isArray(def)) return Array.isArray(val) ? val : def;
      if (def && typeof def === "object") {
        const v = val && typeof val === "object" && !Array.isArray(val) ? val : {};
        const o = {};
        Object.keys(def).forEach(k => { o[k] = merge(def[k], v[k]); });
        Object.keys(v).forEach(k => { if (!(k in o)) o[k] = v[k]; });
        return o;
      }
      if (typeof def === "string") return typeof val === "string" ? val : (typeof val === "number" ? String(val) : def);
      if (typeof def === "boolean") return typeof val === "boolean" ? val : def;
      return val === undefined ? def : val;
    };
    const meta = merge(BLANK.meta, raw.meta);
    ["coverBg", "contactBg", "brandLogo"].forEach(k => { meta[k] = img(meta[k]); });
    ["home", "away"].forEach(s => { meta[s].logo = img(meta[s].logo); meta[s].pitchImg = img(meta[s].pitchImg); });
    let dropped = 0;
    const seen = new Set();
    const blocks = [];
    raw.blocks.forEach(b => {
      if (!b || typeof b !== "object" || !Object.prototype.hasOwnProperty.call(NEW_BLOCK, b.type)) { dropped++; return; }
      const base = NEW_BLOCK[b.type]();
      const m = merge(base, b);
      if ("image" in m) m.image = img(m.image);
      if (b.type === "secuencia") {
        m.items = (Array.isArray(b.items) ? b.items : base.items).slice(0, 4).map(it => { const x = merge({ image: "", caption: "" }, it); x.image = img(x.image); return x; });
        if (!m.items.length) m.items = base.items;
      }
      if (b.type === "datos") {
        m.cards = (Array.isArray(b.cards) ? b.cards : base.cards).slice(0, 3).map(c => merge({ label: "", text: "", accent: false }, c));
        if (!m.cards.length) m.cards = base.cards;
      }
      let id = typeof b.id === "string" && b.id ? b.id : uid();
      while (seen.has(id)) id = uid();
      seen.add(id);
      m.id = id;
      blocks.push(m);
    });
    return { data: { meta, blocks }, dropped, badImages };
  }
  backupStale() { const lb = this.state.lastBackup; return !lb || (Date.now() - lb) > 7 * 86400000; }
  backupNote() {
    const lb = this.state.lastBackup, stale = this.backupStale();
    let txt;
    if (!lb) txt = "Aún no has descargado ninguna copia .json: tu trabajo solo existe en este navegador.";
    else { const days = Math.floor((Date.now() - lb) / 86400000); txt = "Última copia .json: " + (days === 0 ? "hoy" : days === 1 ? "ayer" : "hace " + days + " días") + (stale ? ". Conviene hacer otra." : "."); }
    return h("div", { style: { fontSize: 11.5, lineHeight: 1.45, marginBottom: 10, padding: "9px 11px", borderRadius: 8, color: stale ? "#8a5a00" : "#6B6B6B", background: stale ? "#fbf1d6" : "transparent", border: stale ? "1px solid #ecd9a3" : "1px solid #e4e0d6" } }, txt);
  }
  importJSON() {
    const inp = document.createElement("input"); inp.type = "file"; inp.accept = "application/json,.json";
    inp.onchange = () => {
      const f = inp.files[0]; if (!f) return;
      if (f.size > 30 * 1048576) { this.ask("El archivo pesa más de 30 MB: no parece un playbook.", null); return; }
      const r = new FileReader();
      r.onload = () => {
        let res;
        try { res = this.normalizeData(JSON.parse(r.result)); }
        catch (e) { this.ask("No se pudo cargar el archivo: " + (e instanceof SyntaxError ? "no es un JSON válido." : e.message), null); return; }
        this.save(res.data);
        this.setState({ activeLabel: "" });
        const notes = [];
        if (res.dropped) notes.push(res.dropped + " bloque(s) de tipo desconocido omitido(s)");
        if (res.badImages) notes.push(res.badImages + " imagen(es) no válida(s) retirada(s)");
        if (notes.length) this.ask("Playbook cargado, con avisos: " + notes.join("; ") + ".", null);
      };
      r.readAsText(f);
    };
    inp.click();
  }
'''


def patch(t):
    # 1) importar: validar + saneado (sustituye al importJSON original)
    old_import = re.search(r"  importJSON\(\) \{.*?\n    inp\.click\(\);\n  \}\n", t, re.S)
    if not old_import or t.count("  importJSON() {") != 1:
        raise SystemExit("[importJSON] no encontrado")
    t = t[:old_import.start()] + NEW_METHODS + t[old_import.end():]

    # 1b) restaurar del navegador: mismo saneado (un dato corrupto ya no tumba la app)
    t = rep(t, '''        const parsed = JSON.parse(saved);
        parsed.meta.author = Object.assign({ name: "", role: "", bio: "", newsletter: "", podcast: "", social: "", email: "" }, parsed.meta.author || {});
        this.setState({ data: parsed });''',
        '''        this.setState({ data: this.normalizeData(JSON.parse(saved)).data });''', "restore")

    # 2) copia de seguridad: marca de tiempo, estado, aviso y botón resaltado
    t = rep(t, "exportingImg: false, dirty: false",
            'exportingImg: false, lastBackup: (function () { try { return Number(localStorage.getItem("madg_last_backup")) || 0; } catch (e) { return 0; } })(), dirty: false', "state")
    t = rep(t, "    this.setState({ dirty: false });\n    this.pushHistory();",
            '    const nowTs = Date.now();\n    try { localStorage.setItem("madg_last_backup", String(nowTs)); } catch (e) {}\n    this.setState({ dirty: false, lastBackup: nowTs });\n    this.pushHistory();', "exportJSON")
    t = rep(t, '''      h("div", { style: { display: "flex", flexWrap: "wrap", gap: 7 } },
        h("button", { onClick: () => this.exportJSON(), style: this.btnStyle("#171717", "#fff") }, "Guardar .json"),''',
        '''      this.backupNote(),
      h("div", { style: { display: "flex", flexWrap: "wrap", gap: 7 } },
        h("button", { onClick: () => this.exportJSON(), style: this.backupStale() ? this.btnStyle("var(--color-verde)", "#171717") : this.btnStyle("#171717", "#fff") }, "Guardar .json"),''', "datos-ui")
    t = rep(t, "Se guarda solo en este navegador.\"",
            "Se guarda solo en este navegador: descarga un .json de vez en cuando como copia.\"", "intro")

    # 3) integridad del script externo
    t = rep(t, 's.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";',
            's.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"; s.integrity = "%s"; s.crossOrigin = "anonymous";' % SRI, "sri")
    return t


def main(src, dst):
    lines = open(src, encoding="utf-8").read().split("\n")
    idx = next(i for i, l in enumerate(lines) if l.startswith('"<!DOCTYPE html>'))
    tpl = json.loads(lines[idx])
    tpl = patch(tpl)
    dumped = json.dumps(tpl, ensure_ascii=False)
    dumped = re.sub(r"</(script|style|body|html)", lambda m: "<\\u002F" + m.group(1), dumped, flags=re.I)
    lines[idx] = dumped
    open(dst, "w", encoding="utf-8").write("\n".join(lines))
    print("ok ->", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
