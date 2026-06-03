# gui.py
import os
import sys
import threading
import time
import json

import gradio as gr

# Add current directory to path so absolute imports like src.* work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.processing.batch_processing import batch_process_files
from src.api import provider_manager
from src.metadata.exif_writer import check_exiftool_exists

# Check Exiftool at startup
check_exiftool_exists()
from src.utils.logging import set_log_handler
from src.utils.file_utils import ALL_SUPPORTED_EXTENSIONS

# Global variable to store streaming logs
log_messages = []

def gradio_log_handler(message, tag=None):
    global log_messages
    log_messages.append(message)
    if len(log_messages) > 100:
        log_messages.pop(0)

# Hook our log handler
set_log_handler(gradio_log_handler)

# --- Config Management ---
CONFIG_FILE = "config.json"

def load_config_data():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config_data(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_api_key(provider):
    config = load_config_data()
    return config.get("api_keys", {}).get(provider, "")

def get_base_url(provider):
    config = load_config_data()
    return config.get("base_urls", {}).get(provider, "")

def get_directories(base_path="/app"):
    if not os.path.exists(base_path):
        base_path = os.getcwd()
    dirs = [base_path]
    try:
        for entry in os.listdir(base_path):
            full_path = os.path.join(base_path, entry)
            if os.path.isdir(full_path) and not entry.startswith('.'):
                dirs.append(full_path)
    except Exception:
        pass
    return sorted(dirs)

def save_api_key_and_url(provider, api_key, base_url):
    config = load_config_data()
    if "api_keys" not in config:
        config["api_keys"] = {}
    if "base_urls" not in config:
        config["base_urls"] = {}
        
    config["api_keys"][provider] = api_key
    
    if provider in ["Custom", "Ollama"]:
        config["base_urls"][provider] = base_url
        
    save_config_data(config)

# --- Templates Management ---
TEMPLATES_FILE = "templates.json"

def load_templates():
    try:
        with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_templates(data):
    try:
        with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving templates: {e}")
        return False

def get_template_names():
    templates = load_templates()
    return list(templates.keys())

# --- App State Management ---
def get_last_state():
    config = load_config_data()
    return config.get("last_state", {})

def save_last_state(input_d, output_d, prov, mod, qual, kw, rename):
    config = load_config_data()
    config["last_state"] = {
        "input_dir": input_d,
        "output_dir": output_d,
        "provider": prov,
        "model": mod,
        "quality": qual,
        "keywords_count": kw,
        "rename_files": rename
    }
    save_config_data(config)

# --- Validations & Updates ---

def get_providers():
    providers = provider_manager.list_providers()
    if provider_manager.PROVIDER_CUSTOM not in providers:
        providers.append(provider_manager.PROVIDER_CUSTOM)
    return providers

def update_models(provider):
    if not provider:
        return gr.update(choices=["Seleccionar modelo..."], value=None)
        
    api_key = get_api_key(provider)
    base_url = get_base_url(provider)
    
    # We attempt to fetch live models if api key exists
    if api_key:
        models = provider_manager.fetch_models(provider, api_key, base_url=base_url)
    else:
        models = []
        
    if not models:
        # Fallback to local cache
        config = load_config_data()
        cached = config.get("models_by_provider", {}).get(provider, [])
        models = cached if cached else ["Seleccionar modelo..."]
        
    return gr.update(choices=models, value=models[0] if models else None)

def update_api_key_visibility(provider):
    # Retrieve saved api key and base url to show in settings
    key = get_api_key(provider)
    url = get_base_url(provider)
    
    if provider == "Ollama" and not key:
        key = "ollama"  # Default dummy key
    
    needs_url = provider in ["Custom", "Ollama"]
    
    return (
        gr.update(value=key),
        gr.update(visible=needs_url, value=url if url else provider_manager.PROVIDER_BASE_URLS.get(provider, ""))
    )

def validate_and_save_api_key(provider, api_key, base_url):
    if not provider or not api_key:
        return "❌ Debes seleccionar un proveedor e introducir una Clave API."
    
    # Check status
    status_dict = provider_manager.check_api_keys_status(provider, [api_key], base_url_override=base_url)
    status_code, msg = status_dict.get(api_key, (-1, "Unknown error"))
    
    if status_code == 200 or status_code == 1:
        save_api_key_and_url(provider, api_key, base_url)
        return f"✅ ¡Clave válida! Se ha guardado correctamente para {provider}."
    else:
        return f"❌ Clave Inválida o Error ({status_code}): {msg}\nNo se ha guardado."

def check_provider_readiness(provider):
    key = get_api_key(provider)
    if not key:
        return gr.update(visible=True, value=f"⚠️ No tienes configurada la Clave API para **{provider}**. Por favor, ve a la pestaña Configuración.")
    return gr.update(visible=False, value="")

def toggle_environment(env):
    is_docker = (env == "Docker (Contenedor)")
    return (
        gr.update(visible=is_docker), # docker_row
        gr.update(visible=not is_docker), # native_row
    )

def check_files(folder_path):
    if not folder_path or not folder_path.strip():
        return "⚠️ Introduce una ruta para contar los archivos."
    folder_path = folder_path.strip()
    if not os.path.isdir(folder_path):
        return f"❌ El directorio '{folder_path}' no existe o no es válido."
    
    try:
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(ALL_SUPPORTED_EXTENSIONS) and not f.startswith('.')]
        count = len(files)
        return f"✅ Encontrados {count} archivo(s) compatibles listos para procesar."
    except Exception as e:
        return f"❌ Error al leer la carpeta: {e}"

def open_native_folder_picker(current_path):
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        folder_path = filedialog.askdirectory(parent=root, title="Seleccionar Carpeta", initialdir=current_path if os.path.exists(current_path) else "/")
        root.destroy()
        return folder_path if folder_path else current_path
    except Exception as e:
        print(f"Native picker failed: {e}")
        return current_path

# --- Template Callbacks ---
def auto_fill_template_name(author):
    return author if author else ""

def save_current_template(name, author, copyright_val, usage, email, web, phone, city, country, address, licensor, m_release, p_release):
    if not name or not name.strip():
        return gr.update(), "⚠️ Por favor, introduce un nombre para la plantilla."
    
    data = {
        "author_name": author,
        "copyright_info": copyright_val,
        "usage_terms": usage,
        "contact_email": email,
        "contact_web": web,
        "contact_phone": phone,
        "contact_city": city,
        "contact_country": country,
        "contact_address": address,
        "licensor": licensor,
        "model_release": m_release,
        "property_release": p_release
    }
    templates = load_templates()
    templates[name.strip()] = data
    save_templates(templates)
    
    new_choices = get_template_names()
    return gr.update(choices=new_choices, value=name.strip()), f"✅ Plantilla '{name}' guardada."

def load_selected_template(name):
    if not name:
        return [gr.update()] * 12 + ["⚠️ Ninguna plantilla seleccionada."]
    
    templates = load_templates()
    data = templates.get(name, {})
    if not data:
        return [gr.update()] * 12 + [f"❌ Plantilla '{name}' no encontrada."]
        
    return [
        data.get("author_name", ""),
        data.get("copyright_info", ""),
        data.get("usage_terms", ""),
        data.get("contact_email", ""),
        data.get("contact_web", ""),
        data.get("contact_phone", ""),
        data.get("contact_city", ""),
        data.get("contact_country", ""),
        data.get("contact_address", ""),
        data.get("licensor", ""),
        data.get("model_release", ""),
        data.get("property_release", ""),
        f"✅ Plantilla '{name}' cargada."
    ]

def clear_base_fields():
    return "", "", ""

def clear_contact_fields():
    return "", "", "", "", "", ""

def clear_license_fields():
    return "", "", ""

def start_processing(input_dir, output_dir, provider_name, model_name, keywords_count, quality, rename_files, auto_category, custom_instruction, author_name, copyright_info, usage_terms, contact_email, contact_web, contact_phone, contact_city, contact_country, contact_address, licensor, model_release, property_release):
    global log_messages
    log_messages.clear()
    
    api_key = get_api_key(provider_name)
    base_url = get_base_url(provider_name)
    
    if not input_dir or not output_dir:
        yield "❌ Error: El Directorio de Entrada y de Salida son obligatorios."
        return
        
    if not api_key:
        yield f"❌ Error: No hay Clave API configurada para {provider_name}. Abre los Ajustes de Entorno."
        return
        
    api_keys = [api_key.strip()]
    
    ghostscript_path = "gswin64c.exe"
    if os.name == 'posix':
        ghostscript_path = "gs"
        
    final_instruction = (custom_instruction or "").strip()
    
    exif_metadata = {}
    if (author_name or "").strip(): exif_metadata["author"] = author_name.strip()
    if (copyright_info or "").strip(): exif_metadata["copyright"] = copyright_info.strip()
    if (usage_terms or "").strip(): exif_metadata["usage_terms"] = usage_terms.strip()
    if (contact_email or "").strip(): exif_metadata["contact_email"] = contact_email.strip()
    if (contact_web or "").strip(): exif_metadata["contact_web"] = contact_web.strip()
    if (contact_phone or "").strip(): exif_metadata["contact_phone"] = contact_phone.strip()
    if (contact_city or "").strip(): exif_metadata["contact_city"] = contact_city.strip()
    if (contact_country or "").strip(): exif_metadata["contact_country"] = contact_country.strip()
    if (contact_address or "").strip(): exif_metadata["contact_address"] = contact_address.strip()
    if (licensor or "").strip(): exif_metadata["licensor"] = licensor.strip()
    if (model_release or "").strip(): exif_metadata["model_release"] = model_release.strip()
    if (property_release or "").strip(): exif_metadata["property_release"] = property_release.strip()
    
    prompt_config = {
        "custom_instruction": final_instruction,
        "inject_keywords": [],
        "rename_files": rename_files,
        "exif_metadata": exif_metadata
    }
    
    # Run the batch in a separate thread
    result_container = {}
    
    def worker():
        try:
            res = batch_process_files(
                input_dir=input_dir.strip(),
                output_dir=output_dir.strip(),
                api_keys=api_keys,
                provider_name=provider_name,
                ghostscript_path=ghostscript_path,
                rename_enabled=rename_files,
                delay_seconds=2,
                num_workers=1,
                auto_kategori_enabled=auto_category,
                auto_foldering_enabled=False,
                selected_model=model_name,
                embedding_enabled=True,
                auto_retry_enabled=True,
                keyword_count=str(keywords_count),
                priority=quality,
                prompt_config=prompt_config,
                base_url_override=base_url if provider_name in ["Custom", "Ollama"] else None
            )
            result_container['result'] = res
        except Exception as e:
            result_container['error'] = str(e)

    t = threading.Thread(target=worker)
    t.start()
    
    while t.is_alive():
        yield "\n".join(log_messages)
        time.sleep(0.5)
        
    t.join()
    
    final_output = "\n".join(log_messages)
    if 'error' in result_container:
        final_output += f"\n\n❌ ERROR CRÍTICO: {result_container['error']}"
    else:
        final_output += f"\n\n✅ FINALIZADO. Resultados:\n{result_container['result']}"
        
    yield final_output

# Create the specific "Light System" Gradio Theme
light_theme = gr.themes.Soft(
    primary_hue=gr.themes.colors.Color(
        c50="#eef2eb", c100="#dce5d7", c200="#c9d8c3", c300="#b7cbae", 
        c400="#a5be9a", c500="#97a788", c600="#7a876d", c700="#5d6753", 
        c800="#404739", c900="#23271f", c950="#12140f",
        name="green_accent"
    ),
    secondary_hue=gr.themes.colors.Color(
        c50="#fbf8f0", c100="#f6f0e2", c200="#f2e9d3", c300="#ede1c5", 
        c400="#e9d9b6", c500="#d6b972", c600="#ac945b", c700="#806f44", 
        c800="#554a2d", c900="#2a2516", c950="#15120b",
        name="gold_accent"
    ),
    neutral_hue=gr.themes.colors.stone,
    font=[gr.themes.GoogleFont("Be Vietnam Pro"), "sans-serif"]
).set(
    body_background_fill="#E8E2DA",
    body_text_color="#141313",
    block_background_fill="#FFFFFF",
    block_border_width="1px",
    block_border_color="#D6B972",
    block_shadow="*shadow_drop",
    block_label_text_color="#5d6753",
    button_primary_background_fill="#97A788",
    button_secondary_background_fill="#D6B972",
    button_primary_text_color="#FFFFFF",
    button_secondary_text_color="#141313",
    button_primary_background_fill_hover="#7a876d",
    button_secondary_background_fill_hover="#ac945b",
)

def is_docker_env():
    return os.path.exists("/.dockerenv")

with gr.Blocks(title="Auto metadata", theme=light_theme) as demo:
    with gr.Row(elem_id="header_row"):
        with gr.Column(scale=4):
            gr.HTML("<h2 style='color: #97A788; margin-bottom: 0;'>Auto Metadata <span style='font-size:0.6em; color:gray; font-weight:normal;'>Plataforma web moderna para la generación automática de metadatos mediante IA.</span></h2>")
        with gr.Column(scale=1, min_width=150):
            settings_btn = gr.Button("⚙️ Ajustes Entorno y API", variant="secondary")
            back_btn = gr.Button("🔙 Volver al Trabajo", variant="primary", visible=False)
            
    with gr.Column(visible=False) as settings_workspace:
        with gr.Row():
            env_toggle = gr.Radio(["Docker (Contenedor)", "Local (Nativo)"], label="Modo de Entorno", value="Docker (Contenedor)" if is_docker_env() else "Local (Nativo)", info="Ajusta la forma de navegar por las carpetas.")
            
        gr.Markdown("### 🔐 Credenciales y Seguridad")
        gr.Markdown("Selecciona un proveedor, introduce su Clave API y guárdala. Esta configuración se guarda de manera segura en tu entorno local.")
        
        with gr.Row():
            with gr.Column(scale=1):
                provider_settings = gr.Dropdown(label="🌐 Proveedor a Configurar", choices=get_providers(), value=get_providers()[0] if get_providers() else None)
            with gr.Column(scale=2):
                api_key = gr.Textbox(label="🔑 Clave secreta API", type="password", placeholder="Introduce aquí tu clave API...")
            with gr.Column(scale=2):
                base_url = gr.Textbox(label="🔗 URL Base (Local/Custom)", placeholder="Ej: http://host.docker.internal:11434/v1", visible=False)
        
        with gr.Row():
            save_key_btn = gr.Button("💾 Guardar y Validar Configuración", variant="primary")
            validation_output = gr.Markdown("")

    with gr.Column(visible=True) as main_workspace:
        gr.Markdown("---")
        
        with gr.Row():
            # COLUMNA 1: GESTIÓN + MOTOR
            with gr.Column(scale=1):
                gr.Markdown("### 📂 Gestión de Directorios")
                root_path = "/app" if os.path.exists("/app") else os.path.abspath(".")
                
                with gr.Row(visible=is_docker_env()) as docker_row:
                    input_browser = gr.Dropdown(label="📁 Origen (Docker)", choices=get_directories(), value=get_directories()[0] if get_directories() else "", allow_custom_value=True)
                    output_browser = gr.Dropdown(label="📂 Salida (Docker)", choices=get_directories(), value=get_directories()[0] if get_directories() else "", allow_custom_value=True)
                
                with gr.Row(visible=not is_docker_env()) as native_row:
                    input_dir = gr.Textbox(label="📁 Origen (Local)", placeholder="Ruta a la carpeta...", scale=3)
                    native_input_btn = gr.Button("📂 Examinar", variant="secondary", scale=1)
                    output_dir = gr.Textbox(label="📂 Salida (Local)", placeholder="Ruta a la carpeta...", scale=3)
                    native_output_btn = gr.Button("📂 Examinar", variant="secondary", scale=1)
                    
                if is_docker_env():
                    input_dir = gr.Textbox(visible=False, value=get_directories()[0] if get_directories() else "")
                    native_input_btn = gr.Button(visible=False)
                    output_dir = gr.Textbox(visible=False, value=get_directories()[0] if get_directories() else "")
                    native_output_btn = gr.Button(visible=False)
                    
                with gr.Row():
                    check_files_btn = gr.Button("🔍 Verificar Directorio", variant="secondary", scale=1)
                    file_count_output = gr.Markdown("⚠️ No verificado.")
                    
                with gr.Row():
                    gr.Markdown("### 🤖 Modelo IA")
                    provider_warning = gr.Markdown("", visible=False)
                    
                with gr.Row():
                    provider_work = gr.Dropdown(label="🌐 Proveedor IA", choices=get_providers(), value=get_providers()[0] if get_providers() else None)
                    model_work = gr.Dropdown(label="🤖 Modelo", choices=[], allow_custom_value=True)
                
                gr.Markdown("#### Ajustes Avanzados")
                with gr.Row():
                    quality = gr.Dropdown(label="🎯 Nivel Detalle", choices=["Detailed", "Balanced", "Less", "Custom"], value="Detailed")
                    keywords_count = gr.Slider(label="🏷️ Cantidad Keywords", minimum=10, maximum=100, step=1, value=49)
                rename_files = gr.Checkbox(label="✏️ Renombrar archivos automáticamente (SEO)", value=False)
                auto_category = gr.Checkbox(label="🏷️ Auto Categorizar para Agencias Stock", value=True)
                custom_instruction = gr.Textbox(label="📋 Instrucciones Adicionales", lines=5, placeholder="Ej: Centrarse en el estado de ánimo cinematográfico y paletas de colores cálidas...")
            
            # COLUMNA 2: METADATOS Y PLANTILLAS
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Metadatos Fijos y Plantillas")
                with gr.Group():
                    author_name = gr.Textbox(label="👤 Autor / Creador", placeholder="Ej: Juan Pérez", lines=1)
                    copyright_info = gr.Textbox(label="©️ Derechos de Autor (Copyright)", placeholder="Ej: 2026 Studio", lines=1)
                    usage_terms = gr.Textbox(label="⚖️ Términos de Uso", placeholder="Ej: Todos los derechos reservados", lines=1)
                    clear_base_btn = gr.Button("🧹 Vaciar Base", size="sm", variant="secondary")
                
                with gr.Accordion("📞 Información de Contacto (Opcional)", open=False):
                    contact_email = gr.Textbox(label="📧 Email de Contacto", placeholder="Ej: hola@studio.com", lines=1)
                    contact_web = gr.Textbox(label="🌐 Página Web", placeholder="Ej: www.studio.com", lines=1)
                    contact_phone = gr.Textbox(label="📞 Teléfono", placeholder="Ej: +34 600 000 000", lines=1)
                    contact_city = gr.Textbox(label="🏙️ Ciudad", placeholder="Ej: Barcelona", lines=1)
                    contact_country = gr.Textbox(label="🌍 País", placeholder="Ej: España", lines=1)
                    contact_address = gr.Textbox(label="📍 Dirección", placeholder="Ej: Calle Principal 123", lines=1)
                    clear_contact_btn = gr.Button("🧹 Vaciar Contacto", size="sm", variant="secondary")
                    
                with gr.Accordion("📜 Licencias y Permisos (Opcional)", open=False):
                    licensor = gr.Textbox(label="🏢 Licenciante", placeholder="Ej: Agencia XYZ", lines=1)
                    model_release = gr.Textbox(label="🧑 ID Permiso de Modelo", placeholder="Ej: MR-2026-001", lines=1)
                    property_release = gr.Textbox(label="🏠 ID Permiso de Propiedad", placeholder="Ej: PR-2026-001", lines=1)
                    clear_license_btn = gr.Button("🧹 Vaciar Licencias", size="sm", variant="secondary")
                    
                gr.Markdown("#### 💾 Gestor de Plantillas")
                with gr.Row():
                    with gr.Column(scale=1, min_width=50):
                        template_dropdown = gr.Dropdown(label="Plantilla", choices=get_template_names(), value=None)
                        load_template_btn = gr.Button("📂 Cargar", variant="secondary", size="sm")
                    with gr.Column(scale=1, min_width=50):
                        template_name = gr.Textbox(label="Nombre", placeholder="Nuevo...", lines=1)
                        save_template_btn = gr.Button("💾 Guardar", variant="primary", size="sm")
                    
                template_status = gr.Markdown("")
                
            # COLUMNA 3: REGISTROS
            with gr.Column(scale=1):
                gr.Markdown("### 📄 Consola de Registro")
                output_logs = gr.Textbox(label="", show_label=False, lines=30, interactive=False, max_lines=40)
            
    gr.Markdown("---")
    
    with gr.Row():
        process_btn = gr.Button("▶ Iniciar Procesamiento Múltiple", variant="primary", size="lg")
        stop_btn = gr.Button("🛑 Cancelar Proceso", variant="secondary", size="lg")
                
    # --- EVENT WIRING ---
    
    env_toggle.change(
        fn=toggle_environment,
        inputs=[env_toggle],
        outputs=[docker_row, native_row]
    )
    
    # Process Tab
    provider_work.change(fn=update_models, inputs=provider_work, outputs=model_work)
    provider_work.change(fn=check_provider_readiness, inputs=provider_work, outputs=provider_warning)
    
    # Settings Tab
    provider_settings.change(fn=update_api_key_visibility, inputs=provider_settings, outputs=[api_key, base_url])
    save_key_btn.click(fn=validate_and_save_api_key, inputs=[provider_settings, api_key, base_url], outputs=validation_output)
    
    # Helper to resolve browser paths
    def resolve_browser_path(selected):
        if not selected: 
            return ""
        if isinstance(selected, (list, tuple)):
            if len(selected) == 0:
                return ""
            val = selected[0]
        else:
            val = selected
            
        val = str(val)
        if not os.path.isabs(val):
            return os.path.join(root_path, val)
        return val
        
    input_browser.change(fn=resolve_browser_path, inputs=input_browser, outputs=input_dir)
    output_browser.change(fn=resolve_browser_path, inputs=output_browser, outputs=output_dir)

    native_input_btn.click(fn=open_native_folder_picker, inputs=[input_dir], outputs=[input_dir])
    native_output_btn.click(fn=open_native_folder_picker, inputs=[output_dir], outputs=[output_dir])

    check_files_btn.click(
        fn=check_files,
        inputs=[input_dir],
        outputs=[file_count_output]
    )
    
    click_event = process_btn.click(
        fn=start_processing,
        inputs=[
            input_dir, output_dir, provider_work, model_work, keywords_count, quality, rename_files, auto_category, custom_instruction, 
            author_name, copyright_info, usage_terms, contact_email, contact_web, contact_phone, 
            contact_city, contact_country, contact_address, licensor, model_release, property_release
        ],
        outputs=output_logs
    )
    
    stop_btn.click(
        fn=lambda current_logs: gr.update(value=(current_logs or "") + "\n\n🛑 Proceso cancelado por el usuario."), 
        inputs=[output_logs], 
        outputs=output_logs, 
        cancels=[click_event]
    )
    
    # Template and Clear events
    author_name.change(fn=auto_fill_template_name, inputs=[author_name], outputs=[template_name])
    
    clear_base_btn.click(fn=clear_base_fields, inputs=[], outputs=[author_name, copyright_info, usage_terms])
    clear_contact_btn.click(fn=clear_contact_fields, inputs=[], outputs=[contact_email, contact_web, contact_phone, contact_city, contact_country, contact_address])
    clear_license_btn.click(fn=clear_license_fields, inputs=[], outputs=[licensor, model_release, property_release])
    
    save_template_btn.click(
        fn=save_current_template,
        inputs=[template_name, author_name, copyright_info, usage_terms, contact_email, contact_web, contact_phone, contact_city, contact_country, contact_address, licensor, model_release, property_release],
        outputs=[template_dropdown, template_status]
    )
    
    load_template_btn.click(
        fn=load_selected_template,
        inputs=[template_dropdown],
        outputs=[author_name, copyright_info, usage_terms, contact_email, contact_web, contact_phone, contact_city, contact_country, contact_address, licensor, model_release, property_release, template_status]
    )
    
    # View toggling events
    def show_settings():
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=True)
        
    def hide_settings():
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
        
    settings_btn.click(fn=show_settings, inputs=[], outputs=[main_workspace, settings_workspace, settings_btn, back_btn])
    back_btn.click(fn=hide_settings, inputs=[], outputs=[main_workspace, settings_workspace, settings_btn, back_btn])
    
    # --- State Persistence ---
    def on_state_change(ind, outd, prov, mod, qual, kw, rename):
        save_last_state(ind, outd, prov, mod, qual, kw, rename)
        
    for component in [input_dir, output_dir, provider_work, model_work, quality, keywords_count, rename_files]:
        component.change(
            fn=on_state_change,
            inputs=[input_dir, output_dir, provider_work, model_work, quality, keywords_count, rename_files],
            outputs=[]
        )
        
    def load_initial_state():
        state = get_last_state()
        if not state:
            return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
        return (
            gr.update(value=state.get("input_dir", "")),
            gr.update(value=state.get("output_dir", "")),
            gr.update(value=state.get("provider", get_providers()[0] if get_providers() else None)),
            gr.update(value=state.get("model", None)),
            gr.update(value=state.get("quality", "Detailed")),
            gr.update(value=state.get("keywords_count", 49)),
            gr.update(value=state.get("rename_files", False))
        )
    
    # Initialize UI state
    demo.load(fn=load_initial_state, outputs=[input_dir, output_dir, provider_work, model_work, quality, keywords_count, rename_files])
    demo.load(fn=update_models, inputs=provider_work, outputs=model_work)
    demo.load(fn=update_api_key_visibility, inputs=provider_settings, outputs=[api_key, base_url])
    demo.load(fn=check_provider_readiness, inputs=provider_work, outputs=provider_warning)
    demo.load(fn=lambda: gr.update(value="Docker (Contenedor)" if os.path.exists("/.dockerenv") else "Local (Nativo)"), outputs=env_toggle)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
