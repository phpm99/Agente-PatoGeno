📰🤖 Agente-PatoGeno - Curaduría de Noticias con IA

📌 *Descripción del Proyecto*

Pipeline automatizado en Python que monitorea, filtra y cura noticias de múltiples feeds RSS utilizando la API de Groq (Llama 3.1) y entrega resúmenes traducidos y etiquetados a través de Telegram.

Este proyecto está diseñado bajo estrictas restricciones de cuota gratuita (Zero-Cost Architecture), priorizando la eficiencia de los *tokens* mediante filtros locales y memoria de estado persistente.

🚀 *Características Principales*

*   **Curaduría Inteligente:** Evalúa el nivel de relevancia de las noticias basándose en un perfil de usuario predefinido mediante *prompt engineering* estricto en JSON.
*   **Optimización de Tokens (Zero-Cost):** 
    *   Memoria de estado (`seen_articles.json`) que evita procesar artículos duplicados.
    *   Pre-filtro local de palabras clave (lista negra) que descarta contenido basura (farándula, deportes) antes de realizar peticiones a la API.
*   **Umbrales Dinámicos:** Asigna diferentes niveles de exigencia de puntaje según la fuente (ej. umbral de 9/10 para agencias con alto volumen como RT/Clarín; 8/10 para el resto).
*   **Traducción y Enriquecimiento:** Las noticias en inglés (ej. The New York Times) son traducidas automáticamente al español. El modelo genera *hashtags* dinámicos para facilitar la búsqueda en el historial del chat.
*   **Notificaciones Inteligentes:** Integración con la API de Telegram, incluyendo un "Modo Nocturno" que silencia las notificaciones entre las 00:00 y las 07:00 (hora Argentina) utilizando `pytz`.

🏗️ *Arquitectura y Flujo de Trabajo*

El flujo se ejecuta de manera desatendida mediante **GitHub Actions** en intervalos programados (Cron):

1. **Extracción:** `feedparser` lee +20 fuentes RSS optimizadas y depuradas.
2. **Pre-procesamiento:** Se cruza el ID del artículo con la memoria persistente y se aplica el filtro local de *banned words*.
3. **Evaluación LLM:** Si pasa los filtros locales, el título y extracto se envían a Groq (Llama-3.1-70b-versatile). El modelo devuelve un JSON estructurado con el puntaje, el resumen y las etiquetas.
4. **Entrega:** Si el puntaje supera el umbral, se formatea el mensaje en Markdown y se envía vía Telegram.
5. **Persistencia:** Se hace un *commit* automático en el repositorio actualizando `seen_articles.json`.

🛠️ *Stack Tecnológico*

*   **Lenguaje:** Python 3.11
*   **Automatización:** GitHub Actions (CI/CD Cron Jobs)
*   **Modelos de IA:** GPT OSS 20B (vía Groq Cloud API)
*   **Librerías clave:** `feedparser`, `requests`, `groq`, `pytz`
*   **Integración:** Telegram Bot API

🗺️ *Roadmap Futuro*

*   [ ] **Feedback Interactivo:** Migración de la arquitectura unidireccional a un servidor webhook continuo para agregar botones de "Me interesa / No me interesa" (Inline Keyboards de Telegram) y entrenar al agente dinámicamente.
*   [ ] **Análisis de Encuadre (Framing):** Incorporar detección de tono editorial y asignación de responsabilidad en los titulares para análisis politológico.
