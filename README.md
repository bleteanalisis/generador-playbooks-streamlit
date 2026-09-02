# Generador de Playbooks Tácticos — Más Allá del Gol

Herramienta web para crear análisis tácticos visuales completos: editor de metadatos del
partido, 7 tipos de bloques de contenido, subida de imágenes y exportación a PDF.

Es una única página web autocontenida (`generador-playbook-standalone.html`) — no necesita
servidor, base de datos ni instalación. Se abre en el navegador y ya está.

**Demo en vivo:** https://generador-playbook-tactico.vercel.app

## Características

✅ Editor interactivo de metadatos del partido, alineaciones y campograma
✅ 7 tipos de bloques de contenido (análisis, destacado, secuencia, datos, gráfica, dark, cita)
✅ Autor del análisis editable (nombre, bio, newsletter, podcast, redes, email)
✅ Subida de imágenes (foto del equipo, imágenes tácticas, gráficas)
✅ Dos modos de vista: carrusel (redes, 4:3) y A4 (impresión)
✅ Adaptado a móvil: en pantallas pequeñas arranca en vista previa y el editor se puede
   abrir a pantalla completa
✅ Exportación a PDF (vía el diálogo de impresión del navegador)
✅ Exportación e importación como JSON (para reutilizar o compartir datos)
✅ Autoguardado en localStorage (navegador)
✅ Duplicar playbooks existentes

## Uso

Abre `generador-playbook-standalone.html` directamente en el navegador (doble clic) o entra
en la demo en vivo. Todo pasa en el cliente: no hace falta instalar nada ni tener conexión
después de cargar la página.

### Estructura de un playbook

**Metadatos del partido:**
- Número de análisis (ej: "08")
- Título y subtítulo
- Competición, fecha, lugar
- Score, goleadores, formaciones y alineaciones
- Logos e imágenes de equipos
- Autor del análisis (nombre, rol, bio y redes/contacto)

**Bloques de contenido** (agrégalos en el orden que quieras):

1. **Análisis** — Imagen + 2 columnas de texto (antes/después, home/away, etc.)
2. **Destacado** — Imagen grande + párrafo + cuerpo
3. **Secuencia** — 2–4 imágenes con pie de foto (fotograma a fotograma)
4. **Datos/Claves** — 3 tarjetas con datos clave, puntos de éxito, fallos
5. **Gráfica** — Imagen + texto (para gráficas de datos)
6. **Dark** — Bloque de fondo oscuro para destacar un punto
7. **Cita** — Pull quote (conclusión, frase destacada)

### Workflow

1. Rellena los metadatos del partido y el autor del análisis (barra lateral)
2. Elige el modo: **Redes · 4:3** (carrusel para redes sociales) o **Descarga · A4** (impresión)
3. Añade bloques con **+ Añadir bloque**, cada uno con su propio editor
4. Sube imágenes para cada sección
5. Exporta:
   - **Exportar PDF** → abre el diálogo de impresión del navegador (activa «Gráficos de
     fondo» y márgenes «Ninguno» para que salga igual que en pantalla)
   - **Guardar .json** → para reutilizar o compartir los datos estructurados

### Atajos útiles

- **Duplicar partido** — copia un análisis completo y adapta solo lo que cambia
- **Cargar .json** — carga un análisis que guardaste antes
- **Partido nuevo** — empieza en blanco de verdad (pide confirmación antes de borrar)
- **Mover bloques** — ↑↓ para reordenar secciones, ⧉ para duplicar uno, ✕ para borrarlo
- **Pegar análisis en bruto** — pega texto separado por líneas en blanco y trocéalo en
  bloques «Destacado» automáticamente

## Desplegar cambios

El repo se sube a mano a GitHub (arrastrando los archivos en *Add file → Upload files*), y
Vercel redespliega solo al detectar el cambio — no hace falta configurar nada más porque es
un sitio estático de un único archivo.

Si quieres probarlo en tu ordenador antes de subirlo, basta con abrir
`generador-playbook-standalone.html` con doble clic.

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
    "author": { "name": "...", "role": "...", "bio": "...", "email": "..." },
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

**¿Pierdo mis datos al cerrar?**
No, se guardan en localStorage del navegador. Pero si cambias de navegador o limpias el cache, los pierdes. **Exporta siempre un JSON** para estar seguro.

**¿Puedo editar el HTML exportado?**
Sí, es HTML puro. Pero los cambios no se guardan en la app. Si editas el HTML, guarda una copia.

**¿Quieres imprimir a PDF con mejor calidad?**
Abre el HTML en Firefox (mejor que Chrome para impresión) y usa Imprimir → Guardar como PDF.

---

**Creado por:** Blete (Más Allá del Gol)
**Última actualización:** 2026
