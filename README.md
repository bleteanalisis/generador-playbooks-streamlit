# Generador de Playbooks Tácticos — Más Allá del Gol

Streamlit app para crear análisis tácticos visuales completos, con múltiples tipos de bloques, subida de imágenes y exportación como JSON e HTML.

## Características

✅ Editor interactivo de metadatos del partido  
✅ 7 tipos de bloques de contenido (análisis, destacado, secuencia, datos, gráfica, dark, cita)  
✅ Subida de imágenes (foto del equipo, imágenes tácticas, gráficas)  
✅ Dos modos de vista: carrusel (redes) y A4 (impresión)  
✅ Exportación como JSON (para reutilizar o compartir datos)  
✅ Exportación como HTML (para imprimir a PDF)  
✅ Autoguardado en localStorage (navegador)  
✅ Duplicar playbooks existentes  
✅ Importar/exportar JSON  

## Instalación local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre `http://localhost:8501` en tu navegador.

## Uso

### Estructura de un playbook

**Metadatos del partido:**
- Número de análisis (ej: "08")
- Título y subtítulo
- Competición, fecha, lugar
- Score y resultado
- Formaciones y alineaciones
- Logos e imágenes de equipos

**Bloques de contenido** (agrégalos en el orden que quieras):

1. **Análisis** — Imagen + 2 columnas de texto (antes/después, home/away, etc.)
2. **Destacado** — Imagen grande + párrafo + cuerpo
3. **Secuencia** — 2–4 imágenes con pie de foto (fotograma a fotograma)
4. **Datos/Claves** — 3 tarjetas con datos clave, puntos de éxito, fallos
5. **Gráfica** — Imagen + texto (para gráficas de datos)
6. **Dark** — Bloque de fondo oscuro para destaca

r un punto
7. **Cita** — Pull quote (conclusión, frase destacada)

### Workflow

1. Rellena los metadatos del partido (arriba en la barra lateral)
2. Elige el modo: **Carrusel** (redes sociales 1280×960) o **A4** (impresión 794×1123)
3. Añade bloques con el botón **+ Nuevo bloque**
4. Cada bloque tiene su propio editor
5. Sube imágenes para cada sección
6. Exporta como:
   - **JSON** → para reutilizar o compartir datos estructurados
   - **HTML** → para abrir en navegador, imprimir o editar

### Atajos útiles

- **Duplicar playbook** — copia un análisis completo y adapta solo lo que cambia
- **Importar JSON** — carga un análisis que guardaste antes
- **Reset** — empieza de cero (con confirmación)
- **Mover bloques** — ↑↓ para reordenar secciones

## Desplegar en Streamlit Cloud

1. Pushea este repo a tu cuenta de GitHub:
   ```bash
   git init
   git add .
   git commit -m "Generador de playbooks — primera versión"
   git branch -M main
   git remote add origin https://github.com/tu-usuario/generador-playbooks-streamlit.git
   git push -u origin main
   ```

2. Entra en https://streamlit.io/cloud
3. **New app** → selecciona el repo, rama `main`, archivo `app.py`
4. ¡Listo! Tu app estará en línea en ~1–2 minutos

Cada `git push` redeploy automáticamente.

## Design system

**Colores:**
- Verde: `#B9F148` (acento principal)
- Carbon: `#171717` (dark)
- Bone: `#F4F1EA` (light)
- Gris: `#6B6B6B` (texto secundario)

**Tipografías:**
- Display: Newsreader (serif, headings)
- Body: Archivo (sans-serif)

## Estructura de datos (JSON)

Los playbooks se guardan en JSON con esta estructura:

```json
{
  "meta": {
    "number": "08",
    "title": "...",
    "subtitle": "...",
    "home": { "name": "Málaga", "score": "2", "system": "1-4-2-3-1", ... },
    "away": { "name": "Almería", "score": "1", "system": "1-4-4-2", ... },
    ...
  },
  "blocks": [
    { "id": "abc123", "type": "analisis", "num": "01", ... },
    { "id": "def456", "type": "destacado", ... },
    ...
  ]
}
```

Esto te permite:
- Compartir análisis en texto plano
- Importar/exportar fácilmente
- Integrar con otras herramientas
- Versionar en Git

## Troubleshooting

**¿Las imágenes son muy grandes?**  
La app comprime automáticamente a ~1600px de ancho. Si aún así la sesión es lenta, usa imágenes más pequeñas.

**¿Perdo mis datos al cerrar?**  
No, se guardan en localStorage del navegador. Pero si cambias de navegador o limpias el cache, los pierdes. **Exporta siempre un JSON** para estar seguro.

**¿Puedo editar el HTML exportado?**  
Sí, es HTML puro. Pero los cambios no se guardan en la app. Si editas el HTML, guarda una copia.

**¿Quieres imprimir a PDF con mejor calidad?**  
Abre el HTML en Firefox (mejor que Chrome para impresión) y usa Imprimir → Guardar como PDF.

---

**Creado por:** Blete (Más Allá del Gol)  
**Última actualización:** 2026
