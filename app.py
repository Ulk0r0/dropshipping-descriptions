import streamlit as st
from transformers import pipeline

# Cargar el modelo OPT-350M con caché para optimizar recursos
@st.cache_resource
def load_generator():
    try:
        # Usar device=-1 para CPU (Streamlit Cloud no tiene GPU)
        return pipeline("text-generation", model="facebook/opt-350m", device=-1)
    except Exception as e:
        st.error(f"Error cargando el modelo: {str(e)}")
        return None

generador = load_generator()
if generador is None:
    st.stop()

# Función para generar descripción base con prompt optimizado
def generar_descripcion_base(producto, tono, keywords):
    prompt = f"Soy un experto en marketing para dropshipping. Mi tarea es escribir una descripción atractiva de 3-4 oraciones para: {producto}. " \
             f"El tono debe ser {tono}, optimizada para SEO con estas palabras clave: {', '.join(keywords)}. Termina con una llamada a la acción clara."
    try:
        resultado = generador(prompt, max_length=120, temperature=0.7, top_p=0.9, num_return_sequences=1, truncation=True)[0]["generated_text"]
        texto = resultado.replace(prompt, "").strip()
        ultimo_punto = texto.rfind(".")
        if ultimo_punto != -1:
            texto = texto[:ultimo_punto + 1]
        return texto if texto else "No se pudo generar una descripción válida."
    except Exception as e:
        st.error(f"Error generando texto: {str(e)}")
        return "Error al generar la descripción."

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
