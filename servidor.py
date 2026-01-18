from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# --- SEGURIDAD PARA LA NUBE ---
# Aquí le decimos: "Busca la clave en los secretos de la nube, no en el código"
API_KEY = os.environ.get("GEMINI_API_KEY") 
if not API_KEY:
    print("⚠️ ADVERTENCIA: No se encontró la API KEY")

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
    chat = model.start_chat(history=[])
except Exception as e:
    print(f"Error configurando IA: {e}")

# Cargar Precios
if os.path.exists('precios.xlsx'):
    df = pd.read_excel('precios.xlsx')
    PRECIOS_TEXTO = df.to_string(index=False)
else:
    PRECIOS_TEXTO = "No hay lista de precios disponible."

@app.route('/chat', methods=['POST'])
def responder():
    try:
        datos = request.json
        mensaje_usuario = datos.get('mensaje', '')
        
        instrucciones = f"""
        Eres el experto en ventas de "Maderas La Choca".
        Usa esta tabla de precios para responder:
        {PRECIOS_TEXTO}
        Sé breve, amable y técnico.
        """
        
        response = chat.send_message(f"{instrucciones}\nCliente dice: {mensaje_usuario}")
        return jsonify({"respuesta": response.text})
    except Exception as e:
        return jsonify({"respuesta": f"Lo siento, hubo un error técnico: {str(e)}"})

if __name__ == '__main__':
    # --- PUERTO DINÁMICO (OBLIGATORIO PARA RENDER) ---
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)