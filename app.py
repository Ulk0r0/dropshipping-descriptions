import streamlit as st
from transformers import pipeline

# Cargar modelos (se descargan al iniciar la app en la nube)
generador = pipeline("text-generation", model="distilgpt2")
validador = pipeline("text2text-generation", model="t5-small")

# Función para generar la descripción base
def generar_descripcion_base(producto, tono, keywords):
    prompt = f"Genera una descripción atractiva para: {producto}. Tono {tono}. " \
             f"Optimiza para SEO con palabras clave: {', '.join(keywords)}."
    resultado = generador(prompt, max_length=100, num_return_sequences=1)
    return resultado[0]["generated_text"].replace(prompt, "").strip()

# Función para insertar frases en posiciones específicas
def insertar_frases(descripcion_base, frases_posiciones):
    partes = {"inicio": "", "medio": descripcion_base, "cierre": ""}
    for frase, posicion in frases_posiciones.items():
        if posicion == "inicio":
            partes["inicio"] += f"{frase} "
        elif posicion == "medio":
            medio_split = partes["medio"].split(". ")
            partes["medio"] = ". ".join(medio_split[:len(medio_split)//2] + [frase] + medio_split[len(medio_split)//2:])
        elif posicion == "cierre":
            partes["cierre"] += f" {frase}"
        else:  # Automático
            partes["medio"] += f" {frase}"
    return f"{partes['inicio']}{partes['medio']}{partes['cierre']}".strip()

# Función para validar y ajustar coherencia
def validar_descripcion(texto):
    prompt = f"Reescribe este texto para que sea más coherente y natural: {texto}"
    resultado = validador(prompt, max_length=150, num_return_sequences=1)
    return resultado[0]["generated_text"]

# Interfaz gráfica con Streamlit
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
            descripcion_con_frases = insertar_frases(descripcion_base, frases_posiciones)
            descripcion_final = validar_descripcion(descripcion_con_frases)
        st.subheader("Descripción generada:")
        st.write(descripcion_final)
    else:
        st.error("Por favor, ingresa el producto y al menos una frase.")