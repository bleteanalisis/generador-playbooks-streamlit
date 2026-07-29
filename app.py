"""
Generador de Playbooks Tácticos — Más Allá del Gol
App de Streamlit para crear análisis tácticos visuales con múltiples tipos de bloques,
subida de imágenes y exportación como JSON e HTML.
"""

import streamlit as st
import json
import base64
import io
import uuid
from datetime import datetime
from PIL import Image

# ──────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Generador de Playbooks — Más Allá del Gol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color scheme
CARBON = "#171717"
BONE = "#F4F1EA"
VERDE = "#B9F148"
GRIS = "#6B6B6B"
BONE60 = "#dbd5c6"

# Block types
BLOCK_TYPES = {
    "analisis": "Análisis (imagen + 2 columnas)",
    "destacado": "Destacado (imagen grande + texto)",
    "secuencia": "Secuencia (2–4 imágenes)",
    "datos": "Datos / claves (tarjetas)",
    "grafica": "Gráfica de datos (imagen + texto)",
    "dark": "Bloque destacado (fondo oscuro)",
    "cita": "Cita / pull quote"
}

# ──────────────────────────────────────────────────────────────────────────
# INICIALIZAR SESSION STATE
# ──────────────────────────────────────────────────────────────────────────

def init_state():
    if "playbook_data" not in st.session_state:
        st.session_state.playbook_data = {
            "meta": {
                "number": "01",
                "title": "Nuevo análisis",
                "subtitle": "",
                "competition": "",
                "date": datetime.now().strftime("%d %b %Y"),
                "venue": "",
                "scorers": "",
                "home": {
                    "name": "Equipo A",
                    "abbr": "EQA",
                    "score": "0",
                    "system": "1-4-3-3",
                    "xi": "",
                    "logo": "",
                },
                "away": {
                    "name": "Equipo B",
                    "abbr": "EQB",
                    "score": "0",
                    "system": "1-4-2-3-1",
                    "xi": "",
                    "logo": "",
                }
            },
            "blocks": []
        }
    
    if "mode" not in st.session_state:
        st.session_state.mode = "carrusel"  # carrusel o a4
    
    if "images_cache" not in st.session_state:
        st.session_state.images_cache = {}  # cache para imágenes en base64

def create_new_block(block_type):
    """Crea un nuevo bloque vacío del tipo especificado."""
    bid = str(uuid.uuid4())[:8]
    
    templates = {
        "analisis": {
            "id": bid,
            "type": "analisis",
            "num": "",
            "kicker": "Nueva sección",
            "title": "Título de la sección",
            "image": "",
            "leftLabel": "Columna A",
            "leftText": "",
            "rightLabel": "Columna B",
            "rightText": ""
        },
        "destacado": {
            "id": bid,
            "type": "destacado",
            "num": "",
            "kicker": "Destacado",
            "title": "Título",
            "image": "",
            "lead": "",
            "body": ""
        },
        "secuencia": {
            "id": bid,
            "type": "secuencia",
            "num": "",
            "kicker": "Secuencia",
            "title": "La secuencia",
            "items": [
                {"image": "", "caption": "Fotograma 1"},
                {"image": "", "caption": "Fotograma 2"},
                {"image": "", "caption": "Fotograma 3"}
            ]
        },
        "datos": {
            "id": bid,
            "type": "datos",
            "num": "",
            "kicker": "Claves",
            "title": "Datos clave",
            "cards": [
                {"label": "Dato 1", "text": "", "accent": True},
                {"label": "Dato 2", "text": "", "accent": True},
                {"label": "Dato 3", "text": "", "accent": False}
            ]
        },
        "grafica": {
            "id": bid,
            "type": "grafica",
            "num": "",
            "kicker": "Datos",
            "title": "Gráfica",
            "image": "",
            "body": ""
        },
        "dark": {
            "id": bid,
            "type": "dark",
            "num": "",
            "kicker": "Sección",
            "title": "Título",
            "body": ""
        },
        "cita": {
            "id": bid,
            "type": "cita",
            "text": "Conclusión destacada",
            "attr": "Atribución"
        }
    }
    
    return templates.get(block_type, templates["destacado"])

def image_to_base64(image_file):
    """Convierte un archivo subido a base64."""
    if image_file is None:
        return ""
    
    # Comprimir imagen si es grande
    img = Image.open(image_file)
    max_width = 1600
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    
    # Convertir a base64
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    img_bytes = buffered.getvalue()
    return "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode()

# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR — EDITOR DE METADATOS
# ──────────────────────────────────────────────────────────────────────────

def render_sidebar():
    st.sidebar.title("📋 Metadatos del partido")
    
    with st.sidebar.form("meta_form"):
        st.subheader("① Número y título")
        st.session_state.playbook_data["meta"]["number"] = st.text_input(
            "Nº de análisis", 
            st.session_state.playbook_data["meta"]["number"]
        )
        st.session_state.playbook_data["meta"]["title"] = st.text_input(
            "Título",
            st.session_state.playbook_data["meta"]["title"]
        )
        st.session_state.playbook_data["meta"]["subtitle"] = st.text_input(
            "Subtítulo",
            st.session_state.playbook_data["meta"]["subtitle"]
        )
        
        st.subheader("② Competición y fecha")
        st.session_state.playbook_data["meta"]["competition"] = st.text_input(
            "Competición",
            st.session_state.playbook_data["meta"]["competition"]
        )
        st.session_state.playbook_data["meta"]["date"] = st.text_input(
            "Fecha",
            st.session_state.playbook_data["meta"]["date"]
        )
        st.session_state.playbook_data["meta"]["venue"] = st.text_input(
            "Estadio",
            st.session_state.playbook_data["meta"]["venue"]
        )
        
        st.subheader("③ Equipo LOCAL")
        meta = st.session_state.playbook_data["meta"]["home"]
        c1, c2 = st.columns(2)
        meta["name"] = c1.text_input("Nombre", meta["name"], key="h_name")
        meta["abbr"] = c2.text_input("Abreviatura", meta["abbr"], key="h_abbr")
        c3, c4 = st.columns(2)
        meta["score"] = c3.text_input("Goles", meta["score"], key="h_score")
        meta["system"] = c4.text_input("Formación", meta["system"], key="h_system")
        meta["xi"] = st.text_area("Alineación (números separados por ·)", meta["xi"], key="h_xi", height=60)
        
        st.subheader("④ Equipo VISITANTE")
        meta = st.session_state.playbook_data["meta"]["away"]
        c1, c2 = st.columns(2)
        meta["name"] = c1.text_input("Nombre", meta["name"], key="a_name")
        meta["abbr"] = c2.text_input("Abreviatura", meta["abbr"], key="a_abbr")
        c3, c4 = st.columns(2)
        meta["score"] = c3.text_input("Goles", meta["score"], key="a_score")
        meta["system"] = c4.text_input("Formación", meta["system"], key="a_system")
        meta["xi"] = st.text_area("Alineación (números separados por ·)", meta["xi"], key="a_xi", height=60)
        
        st.form_submit_button("✓ Guardar metadatos", use_container_width=True)
    
    st.sidebar.divider()
    st.sidebar.subheader("🎬 Bloques de contenido")
    
    col1, col2 = st.sidebar.columns(2)
    if col1.button("+ Nuevo bloque", use_container_width=True):
        st.session_state.show_block_menu = True
    
    if st.session_state.get("show_block_menu", False):
        st.sidebar.write("**Tipo de bloque:**")
        for btype, label in BLOCK_TYPES.items():
            if st.sidebar.button(label, key=f"new_block_{btype}", use_container_width=True):
                new_block = create_new_block(btype)
                st.session_state.playbook_data["blocks"].append(new_block)
                st.session_state.show_block_menu = False
                st.rerun()
    
    st.sidebar.divider()
    st.sidebar.subheader("💾 Exportar / Importar")
    
    col1, col2 = st.sidebar.columns(2)
    if col1.button("📥 Exportar JSON", use_container_width=True):
        json_str = json.dumps(st.session_state.playbook_data, ensure_ascii=False, indent=2)
        st.sidebar.download_button(
            "⬇ Descargar",
            json_str,
            file_name=f"playbook-{st.session_state.playbook_data['meta']['number']}.json",
            mime="application/json",
            use_container_width=True
        )
    
    if col2.button("📤 Importar JSON", use_container_width=True):
        st.session_state.show_import = True
    
    if st.session_state.get("show_import", False):
        uploaded_file = st.sidebar.file_uploader("Selecciona un JSON", type=["json"])
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
                st.session_state.playbook_data = data
                st.session_state.show_import = False
                st.success("✓ Playbook importado")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    
    st.sidebar.divider()
    st.sidebar.subheader("⚙️ Herramientas")
    
    col1, col2 = st.sidebar.columns(2)
    if col1.button("🔄 Duplicar", use_container_width=True):
        new_data = json.loads(json.dumps(st.session_state.playbook_data))
        for block in new_data["blocks"]:
            block["id"] = str(uuid.uuid4())[:8]
        st.session_state.playbook_data = new_data
        st.success("✓ Playbook duplicado")
    
    if col2.button("🗑️ Reset", use_container_width=True):
        if st.session_state.get("confirm_reset", False):
            init_state()
            st.session_state.confirm_reset = False
            st.success("✓ Resetheado")
            st.rerun()
        else:
            st.session_state.confirm_reset = True
            st.sidebar.warning("¿Estás seguro? Haz click de nuevo para confirmar.")

# ──────────────────────────────────────────────────────────────────────────
# MAIN — EDITOR DE BLOQUES
# ──────────────────────────────────────────────────────────────────────────

def render_main():
    st.title("🎬 Generador de Playbooks Tácticos")
    st.caption("Más Allá del Gol")
    
    # Modo de vista
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.mode = st.radio(
            "Modo de vista",
            ["carrusel", "a4"],
            format_func=lambda x: "📱 Carrusel (redes)" if x == "carrusel" else "📄 A4 (impresión)",
            horizontal=True
        )
    
    # Botón de imprimir
    if st.button("🖨️ Imprimir / PDF", use_container_width=False):
        st.info("Abre las DevTools (F12) → Console → `window.print()` para imprimir.")
    
    st.divider()
    
    # Editor de bloques
    if not st.session_state.playbook_data["blocks"]:
        st.info("No hay bloques todavía. Añade uno desde la barra lateral →")
    else:
        for i, block in enumerate(st.session_state.playbook_data["blocks"]):
            with st.expander(f"**{i+1}.** {BLOCK_TYPES.get(block['type'], 'Bloque')} — {block.get('title', '(sin título)')}", expanded=False):
                render_block_editor(block, i)

def render_block_editor(block, idx):
    """Editor para un bloque individual."""
    bid = block["id"]
    btype = block["type"]
    
    # Encabezado
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        block["title"] = st.text_input("Título", block.get("title", ""), key=f"{bid}_title")
    with col2:
        block["num"] = st.text_input("Nº", block.get("num", ""), key=f"{bid}_num", max_chars=2)
    with col3:
        if idx > 0 and st.button("⬆", key=f"{bid}_up"):
            st.session_state.playbook_data["blocks"][idx], st.session_state.playbook_data["blocks"][idx-1] = \
                st.session_state.playbook_data["blocks"][idx-1], st.session_state.playbook_data["blocks"][idx]
            st.rerun()
    with col4:
        if idx < len(st.session_state.playbook_data["blocks"]) - 1 and st.button("⬇", key=f"{bid}_down"):
            st.session_state.playbook_data["blocks"][idx], st.session_state.playbook_data["blocks"][idx+1] = \
                st.session_state.playbook_data["blocks"][idx+1], st.session_state.playbook_data["blocks"][idx]
            st.rerun()
    
    # Campos específicos por tipo
    if btype == "analisis":
        block["kicker"] = st.text_input("Kicker", block.get("kicker", ""), key=f"{bid}_kicker")
        col1, col2 = st.columns(2)
        with col1:
            block["leftLabel"] = st.text_input("Etiqueta columna izquierda", block.get("leftLabel", ""), key=f"{bid}_ll")
            block["leftText"] = st.text_area("Texto columna izquierda", block.get("leftText", ""), height=100, key=f"{bid}_lt")
        with col2:
            block["rightLabel"] = st.text_input("Etiqueta columna derecha", block.get("rightLabel", ""), key=f"{bid}_rl")
            block["rightText"] = st.text_area("Texto columna derecha", block.get("rightText", ""), height=100, key=f"{bid}_rt")
        img_file = st.file_uploader("Imagen", type=["jpg", "jpeg", "png"], key=f"{bid}_img")
        if img_file:
            block["image"] = image_to_base64(img_file)
    
    elif btype == "destacado":
        block["kicker"] = st.text_input("Kicker", block.get("kicker", ""), key=f"{bid}_kicker")
        block["lead"] = st.text_input("Lead (primer párrafo)", block.get("lead", ""), key=f"{bid}_lead")
        block["body"] = st.text_area("Cuerpo", block.get("body", ""), height=100, key=f"{bid}_body")
        img_file = st.file_uploader("Imagen", type=["jpg", "jpeg", "png"], key=f"{bid}_img")
        if img_file:
            block["image"] = image_to_base64(img_file)
    
    elif btype == "secuencia":
        block["kicker"] = st.text_input("Kicker", block.get("kicker", ""), key=f"{bid}_kicker")
        for j, item in enumerate(block.get("items", [])):
            st.write(f"**Fotograma {j+1}**")
            item["caption"] = st.text_input(f"Pie de foto {j+1}", item.get("caption", ""), key=f"{bid}_cap{j}")
            img_file = st.file_uploader(f"Imagen {j+1}", type=["jpg", "jpeg", "png"], key=f"{bid}_img{j}")
            if img_file:
                item["image"] = image_to_base64(img_file)
    
    elif btype == "datos":
        block["kicker"] = st.text_input("Kicker", block.get("kicker", ""), key=f"{bid}_kicker")
        for j, card in enumerate(block.get("cards", [])):
            st.write(f"**Tarjeta {j+1}**")
            c1, c2 = st.columns([3, 1])
            with c1:
                card["label"] = st.text_input(f"Etiqueta {j+1}", card.get("label", ""), key=f"{bid}_label{j}")
            with c2:
                card["accent"] = st.checkbox("Destacada", card.get("accent", False), key=f"{bid}_accent{j}")
            card["text"] = st.text_area(f"Texto {j+1}", card.get("text", ""), height=60, key=f"{bid}_text{j}")
    
    elif btype == "grafica":
        block["kicker"] = st.text_input("Kicker", block.get("kicker", ""), key=f"{bid}_kicker")
        block["body"] = st.text_area("Descripción", block.get("body", ""), height=80, key=f"{bid}_body")
        img_file = st.file_uploader("Gráfica", type=["jpg", "jpeg", "png"], key=f"{bid}_img")
        if img_file:
            block["image"] = image_to_base64(img_file)
    
    elif btype == "dark":
        block["kicker"] = st.text_input("Kicker", block.get("kicker", ""), key=f"{bid}_kicker")
        block["body"] = st.text_area("Texto", block.get("body", ""), height=100, key=f"{bid}_body")
    
    elif btype == "cita":
        block["text"] = st.text_area("Cita", block.get("text", ""), height=60, key=f"{bid}_text")
        block["attr"] = st.text_input("Atribución", block.get("attr", ""), key=f"{bid}_attr")
    
    # Eliminar bloque
    if st.button("🗑️ Eliminar bloque", key=f"{bid}_del"):
        st.session_state.playbook_data["blocks"] = [b for b in st.session_state.playbook_data["blocks"] if b["id"] != bid]
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────

init_state()

# Layout
col_sidebar, col_main = st.columns([1, 2], gap="large")

with col_sidebar:
    render_sidebar()

with col_main:
    render_main()

# Footer
st.divider()
st.caption("Generador de Playbooks Tácticos — Más Allá del Gol | 2026")
