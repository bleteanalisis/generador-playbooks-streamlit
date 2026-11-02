"""Prueba end-to-end del parche contra una URL (local con cabeceras, o produccion).
Uso: python3 -I test_parche.py <url> <carpeta_scripts_de_promo>   (necesita cdp.py y demo_data.py)
Comprueba: carga sin violaciones CSP, edicion, A4, deshacer, copia .json, importacion
(valida/invalida/saneada), restauracion de datos corruptos y exportacion PNG (html2canvas + SRI).
"""
import json
import sys
import time

url, scripts = sys.argv[1], sys.argv[2]
sys.path.insert(0, scripts)
from cdp import Chrome
from demo_data import state_json, build_state

REC = """
window.__csp = [];
document.addEventListener('securitypolicyviolation', function (e) {
  window.__csp.push(e.violatedDirective + ' | ' + e.blockedURI + ' | ' + (e.sourceFile || '') );
});
"""
results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + ((" -> " + str(extra)) if extra != "" else ""), flush=True)


def logic_call(c, expr):
    return c.js("(function(){var k=Object.keys(window.__dcRegistry)[0];var P=window.__dcRegistry[k].Logic.prototype;"
                "return JSON.stringify(%s);})()" % expr)


c = Chrome()
try:
    c.open_page()
    c.send("Page.addScriptToEvaluateOnNewDocument", {"source": REC})
    c.viewport(1800, 1125, 1)
    c.goto(url, settle=3.5)
    c.js("localStorage.clear();localStorage.setItem('madg_playbook_v1', %s);localStorage.setItem('madg_help_dismissed','1')"
         % json.dumps(state_json()))
    c.goto(url, settle=3.5)
    c.js("window.dispatchEvent(new Event('resize'))"); time.sleep(0.6)

    check("carga: 7 paginas con datos de demo", c.js("document.querySelectorAll('.madg-page').length") == 7)
    check("carga: sin violaciones CSP", c.js("window.__csp.length") == 0, c.js("window.__csp"))
    check("aviso de copia visible (nunca guardada)", "Aún no has descargado" in c.js("document.body.innerText"))
    check("intro actualizada", "descarga un .json" in c.js("document.body.innerText"))

    # edicion + A4 + deshacer
    c.js("""(function(){var l=Array.prototype.find.call(document.querySelectorAll('label'),function(x){return x.textContent.toLowerCase().indexOf('título del análisis')===0});
      var t=l.querySelector('textarea');Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(t,'Titulo editado QA');
      t.dispatchEvent(new Event('input',{bubbles:true}));})()""")
    time.sleep(0.5)
    check("edicion en vivo", "Titulo editado QA" in c.js("document.body.innerText"))
    c.js("Array.prototype.find.call(document.querySelectorAll('button'),function(b){return b.textContent.trim()==='Descarga · A4'}).click()")
    time.sleep(0.6)
    check("modo A4 sin errores", c.js("document.querySelectorAll('.madg-page').length") == 7)
    c.js("Array.prototype.find.call(document.querySelectorAll('button'),function(b){return b.textContent.trim()==='Redes · 4:3'}).click()")
    time.sleep(0.5)

    # copia .json (descarga interceptada)
    c.js("""window.__dl=[];var oc=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){
      if(this.download){window.__dl.push(this.download);return;} return oc.call(this);};""")
    c.js("Array.prototype.find.call(document.querySelectorAll('button'),function(b){return b.textContent.trim()==='Guardar .json'}).click()")
    time.sleep(0.6)
    txt = c.js("document.body.innerText")
    check("copia .json: descarga lanzada", c.js("window.__dl.length") == 1, c.js("window.__dl"))
    check("copia .json: aviso pasa a 'hoy'", "Última copia .json: hoy" in txt)
    check("copia .json: marca guardada", c.js("!!localStorage.getItem('madg_last_backup')"))

    # normalizeData (casos)
    ok = json.loads(logic_call(c, "(function(){var r=P.normalizeData.call({}, %s);return {b:r.data.blocks.length,d:r.dropped,i:r.badImages};})()" % json.dumps(build_state(), ensure_ascii=False)))
    check("import valido (estado de demo): 4 bloques, nada retirado", ok == {"b": 4, "d": 0, "i": 0}, ok)
    bad = {"meta": {"title": "T", "home": {"score": 3}}, "blocks": [
        {"type": "hackeado", "id": "x"}, {"type": "cita", "id": "dup", "text": "a"}, {"type": "cita", "id": "dup", "text": "b"},
        {"type": "analisis", "image": "javascript:alert(1)"}, {"type": "destacado", "image": "https://evil.example/x.png"},
        {"type": "secuencia", "items": "no-es-lista"}, {"type": "datos", "cards": []}, 7, None]}
    r = json.loads(logic_call(c, "(function(){var r=P.normalizeData.call({}, %s);return {b:r.data.blocks.length,d:r.dropped,i:r.badImages,"
                                 "ids:r.data.blocks.map(function(b){return b.id}),score:r.data.meta.home.score,seq:r.data.blocks.filter(function(b){return b.type==='secuencia'})[0].items.length,"
                                 "cards:r.data.blocks.filter(function(b){return b.type==='datos'})[0].cards.length,away:typeof r.data.meta.away.name,auth:typeof r.data.meta.author.name};})()" % json.dumps(bad)))
    check("import saneado: bloques/dropped/imagenes", (r["b"], r["d"], r["i"]) == (6, 3, 2), r)
    check("import saneado: ids unicos", len(set(r["ids"])) == len(r["ids"]))
    check("import saneado: score numerico -> texto, listas reparadas", r["score"] == "3" and r["seq"] == 3 and r["cards"] == 3 and r["away"] == "string" and r["auth"] == "string", r)
    errs = []
    for label, raw in [("sin blocks", {"meta": {}}), ("meta array", {"meta": [], "blocks": []}), ("array raiz", []), ("null", None)]:
        e = c.js("(function(){var k=Object.keys(window.__dcRegistry)[0];var P=window.__dcRegistry[k].Logic.prototype;try{P.normalizeData.call({}, %s);return 'NO-ERROR';}catch(e){return e.message;}})()" % json.dumps(raw))
        errs.append((label, e))
    check("import invalido: 4 casos rechazados con mensaje", all(e != "NO-ERROR" and e for _, e in errs), errs)

    # importacion real por el boton (selector de archivos simulado)
    c.js("""HTMLInputElement.prototype.click=function(){ if(this.type==='file'&&window.__next){var dt=new DataTransfer();dt.items.add(window.__next);
      Object.defineProperty(this,'files',{value:dt.files});this.onchange&&this.onchange();} }""")
    def importar(text):
        c.js("window.__next = new File([%s], 'x.json', {type:'application/json'});" % json.dumps(text))
        c.js("Array.prototype.find.call(document.querySelectorAll('button'),function(b){return b.textContent.trim()==='Cargar .json'}).click()")
        time.sleep(0.8)
        return c.js("document.body.innerText")
    t1 = importar("esto no es json {")
    check("boton Cargar: JSON roto -> aviso claro", "no es un JSON válido" in t1)
    c.js("Array.prototype.find.call(document.querySelectorAll('button'),function(b){return b.textContent.trim()==='Aceptar'}).click()"); time.sleep(0.3)
    t2 = importar(json.dumps({"meta": {"title": "Solo meta"}}))
    check("boton Cargar: sin blocks -> aviso claro", "falta la lista de bloques" in t2)
    c.js("Array.prototype.find.call(document.querySelectorAll('button'),function(b){return b.textContent.trim()==='Aceptar'}).click()"); time.sleep(0.3)
    t3 = importar(json.dumps({"meta": {"title": "Importado OK"}, "blocks": [{"type": "cita", "text": "hola"}, {"type": "zzz"}]}))
    check("boton Cargar: parcial -> carga + aviso de bloque omitido", "Importado OK" in t3 and "omitido" in t3, t3[t3.find('Playbook cargado'):][:90])
    check("la app sigue viva tras importar", c.js("document.querySelectorAll('.madg-page').length") == 4)  # portada+ficha+1 bloque+contacto
    c.js("Array.prototype.find.call(document.querySelectorAll('button'),function(b){return b.textContent.trim()==='Aceptar'}).click()"); time.sleep(0.3)

    # restauracion con datos corruptos del navegador
    for label, raw in [("meta null", '{"meta":null}'), ("no json", "{{{"), ("parcial", '{"meta":{"title":"Restaurado parcial"},"blocks":[{"type":"cita"}]}')]:
        c.js("localStorage.setItem('madg_playbook_v1', %s)" % json.dumps(raw))
        c.goto(url, settle=3.0)
        n = c.js("document.querySelectorAll('.madg-page').length")
        body = c.js("document.body.innerText")
        check("restaurar '%s': la app arranca" % label, n >= 3, n)
        if label == "parcial":
            check("restaurar parcial: usa el dato valido", "Restaurado parcial" in body)

    # exportar imagenes (html2canvas + SRI + CSP)
    c.js("localStorage.clear();localStorage.setItem('madg_playbook_v1', %s);localStorage.setItem('madg_help_dismissed','1')" % json.dumps(state_json()))
    c.goto(url, settle=3.5)
    c.js("window.dispatchEvent(new Event('resize'))"); time.sleep(0.5)
    c.js("""window.__dl=[];var oc=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){
      if(this.download){window.__dl.push(this.download);return;} return oc.call(this);};""")
    c.js("Array.prototype.find.call(document.querySelectorAll('button'),function(b){return b.textContent.indexOf('Descargar imágenes')>=0}).click()")
    t0 = time.time()
    while time.time() - t0 < 90 and c.js("window.__dl.length") < 7:
        time.sleep(1)
    n_dl = c.js("window.__dl.length")
    check("exportar imagenes: 7 PNG generados (CDN + SRI + CSP)", n_dl == 7, "%d en %.0fs" % (n_dl, time.time() - t0))
    check("html2canvas cargado con integridad", c.js("(function(){var s=Array.prototype.find.call(document.scripts,function(x){return x.src.indexOf('html2canvas')>=0});return !!s&&!!s.integrity&&s.crossOrigin==='anonymous'})()"))
    viol = c.js("window.__csp")
    check("sin violaciones CSP en toda la sesion de exportacion", not viol, viol)
finally:
    c.close()

fails = [n for n, ok in results if not ok]
print("\nRESUMEN: %d/%d pruebas OK" % (len(results) - len(fails), len(results)))
if fails:
    print("FALLAN:", fails)
    sys.exit(1)
