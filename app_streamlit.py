import streamlit as st
import requests

st.set_page_config(page_title="WLM Assistant", page_icon="📘")

API_URL = "http://api:8000/ask"


# -------------------------------------
# Encabezado (Paso 6.2)
# -------------------------------------
st.title("📘 Blue Yonder WLM – AI Assistant")
st.subheader("Tu experto en Warehouse Labor Management")

st.write("---")

# -------------------------------------
# Botón borrar conversación (Paso 6.1)
# -------------------------------------
if st.button("🧹 Borrar conversación"):
    st.session_state["messages"] = []
    st.success("Conversación reiniciada.")

# -------------------------------------
# Historial
# -------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).markdown(msg["content"])

# -------------------------------------
# Entrada usuario
# -------------------------------------
user_input = st.chat_input("Escribe tu pregunta sobre WLM...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    try:
        # Llamada a tu API (Paso 6.3 – mejor manejo de errores)
        response = requests.post(API_URL, json={"question": user_input}, timeout=20)

        if response.status_code == 200:
            assistant_reply = response.json().get("answer", "No se recibió una respuesta válida.")
        else:
            assistant_reply = f"⚠️ Error en la API ({response.status_code}): {response.text}"

    except requests.exceptions.ConnectionError:
        assistant_reply = "❌ No se pudo conectar con la API. ¿Está ejecutándose FastAPI?"
    except requests.exceptions.Timeout:
        assistant_reply = "⏳ La API tardó demasiado en responder."
    except Exception as e:
        assistant_reply = f"⚠️ Error inesperado: {str(e)}"

    st.session_state["messages"].append({"role": "assistant", "content": assistant_reply})
    st.chat_message("assistant").markdown(assistant_reply)
