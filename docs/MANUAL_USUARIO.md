<div style="background-color: #F9F4EF; color: #141313; padding: 30px; font-family: sans-serif; border-radius: 8px;">

<h1 style="color: #97A788; border-bottom: 2px solid #D6B972; padding-bottom: 10px;">📖 RJ Auto Metadata - Manual de Usuario</h1>

<p>Bienvenido al manual completo de <b>Auto Metadata</b>. Esta herramienta automatiza la generación de metadatos profesionales para archivos multimedia (imágenes y vídeos) utilizando Inteligencia Artificial, preparando tu contenido para las agencias de stock más exigentes.</p>

<h2 style="color: #D6B972; margin-top: 30px;">🎯 Niveles de Detalle (Prompts de IA)</h2>
<p>El parámetro <i>Nivel Detalle</i> ajusta directamente las instrucciones (prompts) que se envían al motor de IA, controlando la longitud y profundidad de los títulos generados. Las opciones disponibles son:</p>

<table style="width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #F9F4EF;">
  <tr style="background-color: #97A788; color: #F9F4EF;">
    <th style="padding: 10px; text-align: left; border: 1px solid #D6B972;">Nivel</th>
    <th style="padding: 10px; text-align: left; border: 1px solid #D6B972;">Longitud del Título</th>
    <th style="padding: 10px; text-align: left; border: 1px solid #D6B972;">Descripción y Uso Ideal</th>
  </tr>
  <tr style="background-color: #F9F4EF; color: #141313; border-bottom: 1px solid #D6B972;">
    <td style="padding: 10px; border: 1px solid #D6B972;"><b>Detailed</b></td>
    <td style="padding: 10px; border: 1px solid #D6B972;">Mínimo 6 palabras<br>Máximo 180 caracteres</td>
    <td style="padding: 10px; border: 1px solid #D6B972;">La opción por defecto. Obliga a la IA a ser muy observadora y generar descripciones ricas y largas. Ideal para agencias de stock que premian el detalle descriptivo.</td>
  </tr>
  <tr style="background-color: #F9F4EF; color: #141313; border-bottom: 1px solid #D6B972;">
    <td style="padding: 10px; border: 1px solid #D6B972;"><b>Balanced</b></td>
    <td style="padding: 10px; border: 1px solid #D6B972;">Mínimo 5 palabras<br>Máximo 165 caracteres</td>
    <td style="padding: 10px; border: 1px solid #D6B972;">Un punto intermedio perfecto. Genera títulos equilibrados que no resultan ni demasiado pesados ni demasiado escuetos.</td>
  </tr>
  <tr style="background-color: #F9F4EF; color: #141313; border-bottom: 1px solid #D6B972;">
    <td style="padding: 10px; border: 1px solid #D6B972;"><b>Less (Rápido)</b></td>
    <td style="padding: 10px; border: 1px solid #D6B972;">Mínimo 4 palabras<br>Máximo 150 caracteres</td>
    <td style="padding: 10px; border: 1px solid #D6B972;">Títulos directos, cortos y al grano. Utilízalo si tus imágenes son sencillas o prefieres metadatos muy limpios.</td>
  </tr>
  <tr style="background-color: #F9F4EF; color: #141313;">
    <td style="padding: 10px; border: 1px solid #D6B972;"><b>Custom</b></td>
    <td style="padding: 10px; border: 1px solid #D6B972;">Adaptable</td>
    <td style="padding: 10px; border: 1px solid #D6B972;">Permite al sistema flexibilizar los límites basándose fuertemente en lo que escribas en las <i>Instrucciones Adicionales</i>.</td>
  </tr>
</table>

<h2 style="color: #D6B972; margin-top: 40px;">⚙️ Funcionalidades y Secciones Principales</h2>

<h3 style="color: #97A788;">📂 1. Gestión de Directorios</h3>
<ul>
  <li><b>Origen (Directorio de Entrada):</b> La carpeta donde tienes tus fotos (.jpg, .png) o vídeos listos para procesar.</li>
  <li><b>Salida (Directorio de Salida):</b> La carpeta donde se guardarán los archivos una vez inyectados con los nuevos metadatos.</li>
  <li><i>Nota:</i> Si usas Docker, seleccionarás rutas internas (ej: <code>/app/src</code>). Si lo usas en local, podrás navegar por tu disco duro de forma natural.</li>
</ul>

<h3 style="color: #97A788;">🤖 2. Modelo IA y Ajustes Avanzados</h3>
<ul>
  <li><b>Proveedor y Modelo:</b> Te permite seleccionar qué "cerebro" usar (OpenRouter, Gemini, Groq, etc).</li>
  <li><b>Cantidad Keywords:</b> Ajusta exactamente cuántas palabras clave (tags) quieres que genere la IA para cada archivo (entre 10 y 100).</li>
  <li><b>Instrucciones Adicionales:</b> Un campo de texto libre crucial. Aquí puedes guiar a la IA. <i>Ejemplo: "Ignora las personas del fondo y céntrate solo en el coche rojo deportivo. Usa un tono cinematográfico."</i></li>
</ul>

<h3 style="color: #97A788;">📝 3. Metadatos Fijos y Plantillas</h3>
<p>Además de la información generada por IA, puedes inyectar datos legales estáticos a todos tus archivos de golpe:</p>
<ul>
  <li><b>Información Base:</b> Autor, Copyright y Términos de Uso.</li>
  <li><b>Contacto y Licencias:</b> Información de email, teléfono, ciudad, y códigos de autorización (Model Release).</li>
  <li><b>Gestor de Plantillas (¡Nuevo!):</b> En lugar de rellenar tus datos cada vez, escribe tu Copyright y Contacto, ponle un "Nombre" (ej. <i>Mi Estudio 2026</i>) y pulsa <b>Guardar</b>. La próxima vez, solo tendrás que elegirlo en el desplegable <b>Plantilla</b> y pulsar <b>Cargar</b> para rellenar toda la columna mágicamente.</li>
</ul>

<h3 style="color: #97A788;">📄 4. Consola de Registro (Logs)</h3>
<p>El panel derecho es tu monitor del sistema. Aquí verás en tiempo real qué archivo se está procesando, qué palabras clave ha generado la IA, y si ha habido algún error durante la inyección de los datos.</p>

<h2 style="color: #D6B972; margin-top: 40px;">🧠 El "Prompt" Maestro: ¿Qué le decimos a la IA?</h2>
<p>Aunque la aplicación no imprime el texto completo en la Consola para no sobrecargar la pantalla, el sistema envía internamente unas instrucciones muy estrictas en inglés (ya que los modelos razonan mejor en este idioma) que se construyen dinámicamente con tus ajustes. El esquema base es el siguiente:</p>

<blockquote style="background-color: #f1ebd8; border-left: 4px solid #97A788; padding: 15px; margin: 20px 0; font-family: monospace; font-size: 0.9em; color: #141313;">
"You are a stock photography metadata generator. Analyze the entire image and produce production-ready metadata.<br>
<br>
<i>[Aquí se inyectan tus Instrucciones Adicionales si has escrito algo]</i><br>
<br>
Output requirements:<br>
- Title: Minimum <b>[X]</b> words, maximum <b>[Y]</b> characters, descriptive, unique, no special characters.<br>
- Description: Minimum <b>[X]</b> words, maximum <b>[Y]</b> characters, detailed, unique, no special characters.<br>
- Keywords: Provide up to <b>[Z]</b> unique keywords. Optimize for stock SEO. CRITICAL: Do NOT repeat the same base word in multiple keywords. Deduplicate concepts to maximize coverage. No multi-word phrases (e.g., instead of 'minimalist design', use 'minimalist, design').<br>
- Adobe Stock category: choose the number and name from: <i>[Lista de Adobe]</i>.<br>
- Shutterstock category: choose one from: <i>[Lista de Shutterstock]</i>.<br>
<br>
Return ONLY valid JSON matching this schema exactly..."
</blockquote>
<p>Las variables <b>[X]</b> e <b>[Y]</b> cambian según el <i>Nivel de Detalle</i> que hayas elegido (ej: Detailed envía 6 y 180), y la <b>[Z]</b> es la cantidad exacta del deslizador de <i>Cantidad Keywords</i>.</p>

<hr style="border: 0; height: 1px; background-color: #D6B972; margin-top: 40px; margin-bottom: 20px;">
<p style="text-align: center; font-size: 0.9em;"><i>La aplicación recordará automáticamente tu última configuración para que tu flujo de trabajo sea lo más rápido posible.</i></p>

</div>
