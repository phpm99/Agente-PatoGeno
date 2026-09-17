import os
import json
import feedparser
import requests
from google import genai
from google.genai import types

# ----------------- CONFIGURACIÓN DEL AGENTE -----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MEMORY_FILE = "seen_articles.json"

# Perfil del usuario (puedes ser tan descriptivo como quieras)
USER_PROFILE = """
Intereses clave:
- Avances en Inteligencia Artificial aplicada, agentes autónomos, LLMs open-source y etica aplicada a la IA.
- Avances cientificos con capacidad de alto impacto social.
- Industria argentina, producción y empleo.
- Microeconomía Argentina, endeudamiento y situacion de los hogares.
- Cooperación internacional.
- Tensiones geopolíticas globales.
- Salud pública, salud reproductiva y salud mental.
- Educación, gratuidad y laicidad universitaria.
- Políticas públicas.
- NO me interesan: rumores de celebridades, política partidaria sin impacto macro, deportes generales.
"""

RSS_FEEDS = [
    "https://www.clarin.com/rss/lo-ultimo/",
    "https://www.clarin.com/rss/politica/",
    "https://www.clarin.com/rss/mundo/",
    "https://www.clarin.com/rss/sociedad/",
    "https://www.clarin.com/rss/economia/",
    "https://www.clarin.com/rss/tecnologia/",
    "https://www.clarin.com/rss/internacional/",
    "batimes.com.ar/feed",
    "https://www.lanacion.com.ar/arc/outboundfeeds/rss",
    "perfil.com/feed",
    "https://www.cronista.com/rss/feed.xml",
    "https://www.lapoliticaonline.com/files/rss",
    "https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/el-pais/notas",
    "https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/economia/notas",
    "https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/sociedad/notas",
    "https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/ciencia/notas",
    "https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/universidad/notas",
    "https://www.pagina12.com.ar/arc/outboundfeeds/rss/suplementos/cash/notas",
    "http://rss.dw.com/rdf/rss-sp-all",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Americas.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/SmallBusiness.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/EnergyEnvironment.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Climate.xml",
    "http://www.bbc.co.uk/mundo/ultimas_noticias/index.xml",
    "http://www.bbc.co.uk/mundo/temas/internacional/index.xml",
    "http://www.bbc.co.uk/mundo/temas/america_latina/index.xml",
    "http://www.bbc.co.uk/mundo/temas/ciencia/index.xml",
    "https://actualidad.rt.com/feeds/all.rss",
    "https://mondiplo.com/?page=backend", 
    # Agrega aquí los feeds RSS de tus portales favoritos
]
# ------------------------------------------------------------

def load_seen_ids():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_ids(seen_ids):
    # Guardamos los últimos 500 IDs para evitar saturar memoria
    with open(MEMORY_FILE, "w") as f:
        json.dump(list(seen_ids)[-500:], f)

def evaluate_with_ai(client: genai.Client, title: str, summary: str):
    """El agente razona si la noticia aporta valor al usuario y genera una justificación."""
    prompt = f"""
    Eres un asistente de inteligencia curador de noticias.
    
    Perfil de intereses del usuario:
    {USER_PROFILE}
    
    Noticia a evaluar:
    - Título: {title}
    - Extracto: {summary}
    
    Determina si esta noticia amerita una interrupción en el celular del usuario.
    Responde estrictamente en formato JSON con la siguiente estructura:
    {{
      "relevant": true/false,
      "reason": "Explicación en 1 o 2 oraciones de por qué le interesa al usuario.",
      "score": número del 1 al 10 que represente el impacto/relevancia
    }}
    """
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error evaluando con IA: {e}")
        return {"relevant": False}

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def main():
    seen_ids = load_seen_ids()
    new_seen = set(seen_ids)
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:10]:  # Evalúa los últimos 10 por feed
            entry_id = entry.get("id", entry.get("link", entry.get("title")))
            
            if entry_id in seen_ids:
                continue
            
            new_seen.add(entry_id)
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            
            # Razonamiento del Agente
            decision = evaluate_with_ai(client, title, summary)
            
            # Acción
            if decision.get("relevant") and decision.get("score", 0) >= 7:
                msg = (
                    f"🎯 *Relevancia ({decision.get('score')}/10)*\n\n"
                    f"*{title}*\n\n"
                    f"💡 *Por qué te interesa:* {decision.get('reason')}\n\n"
                    f"🔗 [Leer artículo]({link})"
                )
                send_telegram(msg)
                print(f"Noticia enviada: {title}")
            else:
                print(f"Descartada: {title}")
                
    save_seen_ids(new_seen)

if __name__ == "__main__":
    main()
