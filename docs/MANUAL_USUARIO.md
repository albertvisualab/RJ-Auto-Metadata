<div style="background-color: #F9F4EF; color: #141313; padding: 40px; font-family: sans-serif; border-radius: 8px; line-height: 1.6;">

<h1 style="color: #97A788; border-bottom: 3px solid #D6B972; padding-bottom: 10px;">📖 RJ Auto Metadata - Manual de Usuario Completo</h1>

<p>Bienvenido al manual definitivo de <b>Auto Metadata</b>. Esta herramienta ha sido diseñada para automatizar el tedioso proceso de generar metadatos profesionales para archivos multimedia (imágenes y vídeos) utilizando Inteligencia Artificial, y prepararlos directamente para su venta en las agencias de stock más exigentes.</p>

<h2 style="color: #D6B972; margin-top: 40px; border-bottom: 1px solid #e0d5c1; padding-bottom: 5px;">⚙️ 1. Panel de Configuración y Origen</h2>

<h3 style="color: #97A788;">📁 Gestión de Directorios</h3>
<p>El primer paso es indicarle a la aplicación dónde están tus archivos y dónde quieres que los guarde terminados:</p>
<ul>
  <li><b>Origen (Directorio de Entrada):</b> Selecciona la carpeta donde tienes tus fotos originales (<code>.jpg</code>, <code>.png</code>) o vídeos listos para procesar.</li>
  <li><b>Salida (Directorio de Salida):</b> La carpeta donde se guardarán los archivos una vez procesados y donde se generarán las hojas de cálculo CSV.</li>
</ul>

<blockquote style="background-color: #f1ebd8; border-left: 4px solid #D6B972; padding: 10px 15px; margin: 15px 0; font-size: 0.95em;">
  <b>💡 Tip de Flujo de Trabajo:</b> Mantén tus carpetas originales limpias. La aplicación <b>nunca</b> sobrescribe tus originales; copia el archivo a la carpeta de salida y le inyecta los metadatos allí.
</blockquote>

<h2 style="color: #D6B972; margin-top: 40px; border-bottom: 1px solid #e0d5c1; padding-bottom: 5px;">🤖 2. Configuración del Motor de IA</h2>

<h3 style="color: #97A788;">Niveles de Detalle (Prompts de IA)</h3>
<p>El <i>Nivel Detalle</i> es el corazón de la aplicación. Ajusta las directrices exactas que se envían al motor de IA, controlando la longitud y profundidad de los títulos y descripciones.</p>

<table style="width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #ffffff; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
  <tr style="background-color: #97A788; color: #F9F4EF;">
    <th style="padding: 12px; text-align: left; border: 1px solid #d1c8b4;">Nivel</th>
    <th style="padding: 12px; text-align: left; border: 1px solid #d1c8b4;">Longitud Objetivo</th>
    <th style="padding: 12px; text-align: left; border: 1px solid #d1c8b4;">Uso Ideal y Comportamiento</th>
  </tr>
  <tr style="color: #141313;">
    <td style="padding: 12px; border: 1px solid #e0d5c1;"><b>Detailed</b></td>
    <td style="padding: 12px; border: 1px solid #e0d5c1;">6 a 180 caracteres</td>
    <td style="padding: 12px; border: 1px solid #e0d5c1;">La IA se vuelve hiperexhaustiva. Describe colores, fondos, texturas y estados de ánimo. Ideal para Adobe Stock o Shutterstock, que premian el detalle descriptivo masivo.</td>
  </tr>
  <tr style="color: #141313; background-color: #faf7f2;">
    <td style="padding: 12px; border: 1px solid #e0d5c1;"><b>Balanced</b></td>
    <td style="padding: 12px; border: 1px solid #e0d5c1;">5 a 165 caracteres</td>
    <td style="padding: 12px; border: 1px solid #e0d5c1;">Punto intermedio perfecto. Descripciones naturales que capturan la esencia sin caer en la verborrea excesiva.</td>
  </tr>
  <tr style="color: #141313;">
    <td style="padding: 12px; border: 1px solid #e0d5c1;"><b>Less</b></td>
    <td style="padding: 12px; border: 1px solid #e0d5c1;">4 a 150 caracteres</td>
    <td style="padding: 12px; border: 1px solid #e0d5c1;">Títulos cortos y al grano. Usar para sujetos recortados (aislados en blanco) o ilustraciones muy minimalistas.</td>
  </tr>
  <tr style="color: #141313; background-color: #faf7f2;">
    <td style="padding: 12px; border: 1px solid #e0d5c1;"><b>Custom</b></td>
    <td style="padding: 12px; border: 1px solid #e0d5c1;">Adaptable</td>
    <td style="padding: 12px; border: 1px solid #e0d5c1;">Libera las restricciones. Se basará un 100% en lo que tú le pidas en las <i>Instrucciones Adicionales</i>.</td>
  </tr>
</table>

<h3 style="color: #97A788; margin-top: 25px;">Instrucciones Adicionales (Custom Prompting)</h3>
<p>Si la IA no entiende el contexto visual de tus fotos, puedes decírselo aquí. Este texto se fusiona directamente con la instrucción principal de la IA.</p>
<ul>
  <li><b>Ejemplo Malo:</b> <i>"Pon títulos guays."</i> (Demasiado vago).</li>
  <li><b>Ejemplo Bueno:</b> <i>"Estas imágenes son renders 3D arquitectónicos. Ignora a las personas desenfocadas y céntrate en describir los materiales de construcción (hormigón, madera, cristal) y la iluminación natural."</i></li>
</ul>

<h2 style="color: #D6B972; margin-top: 40px; border-bottom: 1px solid #e0d5c1; padding-bottom: 5px;">🚀 3. Funciones de Automatización Clave</h2>

<h3 style="color: #97A788;">✏️ Renombrado Automático (SEO)</h3>
<p><b>Activando esta casilla</b>, la aplicación cambiará el nombre original de tu archivo (ej: <code>IMG_4922.jpg</code>) por un nombre hiper-optimizado para buscadores basado en el título generado por la IA (ej: <code>elegant-table-setting-with-candles.jpg</code>).</p>
<p><i>Nota sobre el orden:</i> El renombrado es puramente semántico. Si tenías fotos ordenadas numéricamente, al usar nombres descriptivos perderán ese orden alfabético, pero a cambio ganarás tracción orgánica en las búsquedas de las agencias.</p>

<h3 style="color: #97A788;">🏷️ Auto Categorizar para Agencias Stock</h3>
<p><b>Activando esta casilla</b>, el sistema leerá el Título y las Keywords que acaba de generar la IA y utilizará un algoritmo interno para asignar la <b>Categoría Oficial</b> correspondiente de Adobe Stock y Shutterstock.</p>
<ul>
  <li><i>Ejemplo:</i> Si la IA genera palabras como <i>"dog", "puppy", "pet"</i>, el sistema mapeará automáticamente a la categoría <b>"Animals/Wildlife"</b> en el CSV de Shutterstock, y a la categoría <b>"Animals" (número 1)</b> en Adobe Stock.</li>
  <li>Si desactivas esto, las columnas de categoría en los archivos CSV se quedarán en blanco.</li>
</ul>

<h2 style="color: #D6B972; margin-top: 40px; border-bottom: 1px solid #e0d5c1; padding-bottom: 5px;">📝 4. Metadatos Fijos y Plantillas (El Sistema Dual)</h2>

<p>Es vital entender que esta aplicación usa un <b>Sistema Dual</b>. La IA solo genera contenido comercial (Títulos y Keywords), pero tus datos personales de Autor se escriben en el archivo mediante un proceso separado para garantizar su integridad legal.</p>

<h3 style="color: #97A788;">Incrustación EXIF Pura</h3>
<p>Cuando rellenas los campos de <b>Autor, Copyright, Email, Web, etc.</b>, esta información NO se envía a la IA (para evitar que ensucie los títulos SEO). En cambio, se inyecta silenciosamente como <b>Metadatos Puros (EXIF, IPTC, XMP)</b> directamente en la estructura interna del archivo JPG/PNG/MP4. Así, si alguien descarga tu foto, tu autoría viaja con ella para siempre.</p>

<h3 style="color: #97A788;">Conexión de Permisos con Archivos CSV</h3>
<p>Dentro de la pestaña de <b>Licencias y Permisos</b>, hay campos especiales que se sincronizan con las hojas de cálculo generadas:</p>
<ul>
  <li><b>ID Permiso de Modelo & ID Permiso de Propiedad:</b> Lo que escribas aquí se rellenará automáticamente en la columna <code>Releases</code> del documento <code>adobe_stock_export.csv</code> (separados por comas si usas ambos).</li>
  <li><b>País (Contacto):</b> Lo que escribas en "País" viajará a la columna oculta de país en el archivo <code>123rf_export.csv</code>.</li>
</ul>

<h3 style="color: #97A788;">Gestor de Plantillas</h3>
<p>Si siempre usas la misma información de autor y contacto, no la escribas cada vez:</p>
<ol>
  <li>Rellena todos tus datos de Autor, Copyright y Permisos.</li>
  <li>Escribe un nombre en la casilla "Nombre" (ej: <i>"Shoot Editorial Moda"</i> o <i>"Mi Estudio Base"</i>).</li>
  <li>Pulsa <b>Guardar</b>. A partir de ahora, podrás cargarlo instantáneamente desde el desplegable.</li>
</ol>

<h2 style="color: #D6B972; margin-top: 40px; border-bottom: 1px solid #e0d5c1; padding-bottom: 5px;">📊 5. Las Hojas de Cálculo CSV Generadas</h2>

<p>En tu carpeta de <i>Salida</i>, se creará una subcarpeta llamada <code>metadata_csv</code>. Aquí encontrarás hojas Excel listas para importar directamente en el portal de subidas de cada agencia, ahorrándote horas de trabajo manual. Cada agencia tiene su formato particular:</p>

<ul>
  <li><b>adobe_stock_export.csv:</b> Incluye Nombre, Título, Keywords, Categoría Mapeada, y la columna "Releases" (si rellenaste las IDs de Modelo/Propiedad en la interfaz).</li>
  <li><b>shutterstock_export.csv:</b> Incluye Nombre, Descripción, Keywords, y la Categoría Oficial de Shutterstock calculada. (El contenido para adultos y editorial se marca como "No" por defecto).</li>
  <li><b>vecteezy_export.csv:</b> Adaptado a los requisitos de Vecteezy (Licencia Pro por defecto).</li>
  <li><b>123rf_export.csv:</b> Usa su formato propietario, capturando el país de tus datos de contacto.</li>
  <li><b>depositphotos_export.csv & miri_canvas_export.csv:</b> Plantillas estandarizadas para dichas plataformas.</li>
</ul>

<hr style="border: 0; height: 1px; background-color: #D6B972; margin-top: 40px; margin-bottom: 20px;">
<p style="text-align: center; font-size: 0.9em;"><i>La aplicación recordará automáticamente tu última configuración de directorios y modelo para que tu flujo de trabajo diario requiera apenas un par de clics.</i></p>

</div>
