import streamlit as st
from google import genai
from google.genai import types
import requests
from fpdf import FPDF

# ==============================
# Configurar API Gemini
# ==============================
api = st.secrets['auth_api']   #reemplaza con tu API de Gemini
client = genai.Client(api_key=api)

# ==============================
# Diccionario de textos bilingüe
# ==============================
texts = {
    "English": {
        "subheader": "Upload one or more medical images for analysis",
        "info": "💡 You can upload multiple images or provide multiple image URLs. Use 'Generate Analysis' for a global analysis or 'Generate Individual Analysis' for per-image results.",
        "upload_label": "📤 Upload one or multiple images",
        "urls_label": "🌐 Or enter multiple direct image URLs (one per line, ending with .jpg/.jpeg/.png)",
        "global_prompt": (
            "You are a medical image analysis expert. "
            "Analyze all the provided image(s) together and provide a single concise summary (max 200 words) "
            "highlighting patterns, common findings, and recommendations. "
            "Include disclaimer: Consult with a doctor before making any decisions."
        ),
        "individual_prompt": (
            "You are a medical image analysis expert. "
            "Analyze this image and provide a concise summary (max 200 words) with: "
            "1) Detailed Analysis, 2) Findings Report, "
            "3) Recommendations and Next Steps, 4) Treatment Suggestions. "
            "Include disclaimer: Consult with a doctor before making any decisions."
        ),
        "generate_global": "🔍 Generate Analysis",
        "generate_individual": "🧩 Generate Individual Analysis",
        "pdf_title": "Global Analysis",
        "analysis_result": "Analysis Result",
        "download_txt": "Download TXT",
        "download_pdf": "Download PDF",
        "analyzing_label": "Analyzing"
    },
    "Español": {
        "subheader": "Suba una o más imágenes médicas para análisis",
        "info": "💡 Puede subir múltiples imágenes o proporcionar varias URLs de imágenes. Use 'Generar Análisis' para un análisis global o 'Análisis Individual' para resultados por imagen.",
        "upload_label": "📤 Suba una o más imágenes",
        "urls_label": "🌐 O ingrese varias URLs directas de imágenes (una por línea, terminando en .jpg/.jpeg/.png)",
        "global_prompt": (
            "Eres un experto en análisis de imágenes médicas. "
            "Analiza todas las imágenes proporcionadas y entregue un resumen conciso (máx. 200 palabras) "
            "resaltando patrones, hallazgos comunes y recomendaciones. "
            "Incluye el aviso: Consulte con un médico antes de tomar decisiones."
        ),
        "individual_prompt": (
            "Eres un experto en análisis de imágenes médicas. "
            "Analiza esta imagen y proporciona un resumen conciso (máx. 200 palabras) con: "
            "1) Análisis Detallado, 2) Informe de Hallazgos, "
            "3) Recomendaciones y Próximos Pasos, 4) Sugerencias de Tratamiento. "
            "Incluye el aviso: Consulte con un médico antes de tomar decisiones."
        ),
        "generate_global": "🔍 Generar Análisis",
        "generate_individual": "🧩 Análisis Individual",
        "pdf_title": "Análisis Global",
        "analysis_result": "Resultado del Análisis",
        "download_txt": "Descargar TXT",
        "download_pdf": "Descargar PDF",
        "analyzing_label": "Analizando"
    }
}

# ==============================
# Configuración de la app
# ==============================
st.set_page_config(page_title="VitalImage Analysis", page_icon=":robot:")
st.title("🧑 VITAL ❤️ Image 📷 Analytics 📊 👩‍⚕️")

# Selección de idioma
language = st.selectbox("🌐 Select language / Seleccione idioma", ["English", "Español"])
t = texts[language]

st.subheader(t["subheader"])
st.info(t["info"])

# Subir imágenes locales
uploaded_files = st.file_uploader(t["upload_label"], type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Ingresar URLs de imágenes
image_urls = st.text_area(t["urls_label"])


# Función para leer imágenes de URLs
def read_images_from_urls(urls):
    images = []
    labels = []
    for url in urls:
        url = url.strip()
        if url:
            try:
                resp = requests.get(url)
                if resp.status_code == 200:
                    images.append(resp.content)
                    labels.append(url.split("/")[-1])
            except:
                pass
    return images, labels


# Función para mostrar análisis y botones
def display_analysis(response_text, image_labels):
    """
    Muestra el análisis de imágenes de forma ordenada en Streamlit.
    """
    # Título simple
    st.markdown(f"### 📝 Análisis")

    st.markdown(f"**{t['analysis_result']}**")
    st.markdown(f"Imágenes analizadas: {', '.join(image_labels)}")
    st.write(response_text)

    # Botones de descarga
    st.download_button(f"💾 {t['download_txt']}", response_text, f"analysis_{'_'.join(image_labels)}.txt", "text/plain")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 6, response_text)
    pdf_path = f"/tmp/analysis_{'_'.join(image_labels)}.pdf"
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button(f"📄 {t['download_pdf']}", f, f"analysis_{'_'.join(image_labels)}.pdf", "application/pdf")


# ==============================
# Botón de análisis global
# ==============================
if st.button(t["generate_global"]):
    all_images = []
    all_labels = []

    # Locales
    if uploaded_files:
        for f in uploaded_files:
            all_images.append(f.read())
            all_labels.append(f.name)

    # URLs
    urls_list = image_urls.splitlines()
    url_images, url_labels = read_images_from_urls(urls_list)
    all_images.extend(url_images)
    all_labels.extend(url_labels)

    if all_images:
        st.info(f"{t['analyzing_label']}: {', '.join(all_labels)}")

        # Preparar parts
        parts = [types.Part.from_bytes(data=img, mime_type="image/jpeg") for img in all_images]
        parts.append(t["global_prompt"])

        # Generar respuesta
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=parts
        )

        display_analysis(response.text, all_labels)
    else:
        st.warning("⚠️ No images provided.")

# ==============================
# Botón de análisis individual
# ==============================
if st.button(t["generate_individual"]):
    all_images = []
    all_labels = []

    # Locales
    if uploaded_files:
        for f in uploaded_files:
            all_images.append(f.read())
            all_labels.append(f.name)

    # URLs
    urls_list = image_urls.splitlines()
    url_images, url_labels = read_images_from_urls(urls_list)
    all_images.extend(url_images)
    all_labels.extend(url_labels)

    if all_images:
        for img, label in zip(all_images, all_labels):
            st.info(f"{t['analyzing_label']}: {label}")
            parts = [types.Part.from_bytes(data=img, mime_type="image/jpeg"), t["individual_prompt"]]
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=parts
            )
            display_analysis(response.text, [label])
    else:
        st.warning("⚠️ No images provided.")

