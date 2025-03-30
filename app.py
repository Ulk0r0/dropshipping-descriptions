import streamlit as st
from transformers import pipeline

# Cargar modelo
generador = pipeline("text-generation", model="distilgpt2")

# Función para generar descripción base con mejor prompt
def generar_descripcion_base(producto, tono, keywords):
    prompt = f"Eres un experto en marketing para dropshipping. Escribe una descripción breve y atractiva para este producto: {producto}. " \
             f"Usa un tono {tono} y optimiza para SEO con estas palabras clave: {', '.join(keywords)}. " \
             f"Hazlo persuasivo, con 3-4 oraciones, y termina con una llamada a la acción."
    resultado = generador(prompt, max_length=120, num_return_sequences=1, temperature=0.7, top_k=50)[0]["generated_text"]
    # Limpiar el prompt y cortar en la última oración completa
    texto = resultado.replace(prompt, "").strip()
    ultimo_punto = texto.rfind(".")
    if ultimo_punto != -1:
        texto = texto[:ultimo_punto + 1]
    return texto

# Función para insertar frases en posiciones específicas
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
    # Asegurar que termine con punto
    if not descripcion.endswith("."):
        descripcion += "."
    return descripcion

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
            # Generar descripción base
            descripcion_base = generar_descripcion_base(producto, tono, keywords)
            # Insertar frases
            descripcion_final = insertar_frases(descripcion_base, frases_posiciones)
        st.subheader("Descripción generada:")
        st.write(descripcion_final)
    else:
        st.error("Por favor, ingresa el producto y al menos una frase.")
            descripcion_con_frases = insertar_frases(descripcion_base, frases_posiciones)
            descripcion_final = validar_descripcion(descripcion_con_frases)
        st.subheader("Descripción generada:")
        st.write(descripcion_final)
    else:
        st.error("Por favor, ingresa el producto y al menos una frase.")
