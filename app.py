import streamlit as st
import requests
import os

# Configurar API de Hugging Face con variable de entorno
API_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")  # Obtiene el token desde las variables de entorno
if not API_TOKEN:
    st.error("Error: No se encontró el token de Hugging Face. Configúralo en Streamlit Cloud.")
    st.stop()

headers = {"Authorization": f"Bearer {API_TOKEN}"}
API_URL = "https://api-inference.huggingface.co/models/gpt2-medium"

# Función para generar descripción base
def generar_descripcion_base(producto, tono, keywords):
    prompt = f"Eres un experto en marketing para dropshipping. Escribe una descripción breve y atractiva para: {producto}. " \
             f"Usa un tono {tono}, optimiza para SEO con: {', '.join(keywords)}. 3-4 oraciones, termina con una llamada a la acción."
    payload = {"inputs": prompt, "max_length": 120, "temperature": 0.7}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()[0]["generated_text"].replace(prompt, "").strip()

# Función para insertar frases
def insertar_frases(descripcion_base, frases_posiciones):
    partes = {"inicio": "", "medio": descripcion_base, "cierre": ""}
    oraciones = partes["medio"].split(". ")
    for frase, posicion in frases_posiciones.items():
        if posicion == "inicio":
            partes["inicio"] = f"{frase} "
        elif posicion == "medio" and len(oraciones) > 1:
            oraciones.insert(len(oraciones) // 2, frase)
            partes["medio"] = ". ".join(oraciones)
        elif posicion == "cierre":
            partes["cierre"] = f" {frase}"
        else:  # Automático
            partes["medio"] += f" {frase}"
    descripcion = f"{partes['inicio']}{partes['medio']}{partes['cierre']}".strip()
    if not descripcion.endswith("."):
        descripcion += "."
    return descripcion

# Interfaz gráfica
st.title("Generador de Descripciones de Productos para Dropshipping")
producto = st.text_input("Producto (ej. 'Auriculares inalámbricos, Bluetooth 5.0, 20h batería, negros')")
tono = st.selectbox("Tono", ["informal", "profesional", "creativo"])
keywords = st.text_input("Palabras clave SEO (separadas por comas)", "auriculares inalámbricos, Bluetooth").split(", ")

st.subheader("Frases personalizadas")
num_frases = st.number_input("¿Cuántas frases quieres añadir?", min_value=0, max_value=5, value=1)
frases_posiciones = {}
for i in range(num_frases):
    frase = st.text_input(f"Frase {i+1}", key=f"frase_{i}")
    posicion = st.selectbox(f"Posición de la frase {i+1}", ["inicio", "medio", "cierre", "automático"], key=f"pos_{i}")
    if frase:
        frases_posiciones[frase] = posicion

if st.button("Generar Descripción"):
    if producto and frases_posiciones:
        with st.spinner("Generando descripción..."):
            descripcion_base = generar_descripcion_base(producto, tono, keywords)
            descripcion_final = insertar_frases(descripcion_base, frases_posiciones)
        st.subheader("Descripción generada:")
        st.write(descripcion_final)
    else:
        st.error("Por favor, ingresa el producto y al menos una frase.")
