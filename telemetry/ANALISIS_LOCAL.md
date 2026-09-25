# Analizador conversacional local

El botón **Consultar al asistente** abre un panel conversacional, pero sus respuestas son determinísticas: el servidor toma la captura vigente y arma textos predeterminados a partir de los mismos niveles `safe`, `warning` y `critical` que usa el dashboard. No llama a OpenAI, no necesita clave, no usa Internet y cada consulta cuesta cero. Al abrir muestra un saludo estable y espera una pregunta o una sugerencia rápida; no lanza una respuesta automática que pueda aparecer mientras el usuario ya escribe. Acepta Enter para enviar.

## Qué responde

- Una consulta general enumera pH, humedad, conductividad y temperatura con valor, unidad, estado, objetivo y recomendación.
- Si todo está dentro del objetivo, entrega retroalimentación positiva y recomienda mantener el monitoreo.
- Si hay varios problemas, cuenta críticos y advertencias, explica todos y refuerza cuáles parámetros permanecen adecuados.
- Reconoce consultas enfocadas por palabras como `pH`, `acidez`, `humedad`, `conductividad`, `EC`, `temperatura`, `calor` o `frío`.
- Relaciona escenarios predeterminados: temperatura alta + humedad baja, temperatura alta + humedad alta, temperatura baja + humedad alta y pH + EC fuera del objetivo.
- Si la conexión está vencida, no presenta la última captura como estado actual.

Cada respuesta vuelve a consultar el estado del servidor. Por eso una repregunta posterior puede reflejar potenciómetros que cambiaron desde el mensaje anterior. El historial sólo se usa para mostrar la conversación; no puede reemplazar las métricas del servidor.

## Límites deliberados

No es un modelo generativo ni entiende cualquier tema. Una pregunta no reconocida recibe el análisis general. Tampoco diagnostica plantas, prescribe dosis, controla bombas o modifica alertas. Los potenciómetros simulan sensores y los límites críticos son reglas conservadoras del prototipo.

El chat conserva hasta 40 mensajes visibles en la página y envía como máximo 6 anteriores al servidor. No hay persistencia al recargar. Las rutas locales conservan protección de origen y un token de sesión separado del token de telemetría:

- `GET /api/v1/ai/config`: informa `configured: true`, nombre del analizador, `external_api: false`, costo cero y token local.
- `POST /api/v1/ai/chat`: recibe `message` e `history`; toma las métricas exclusivamente del estado interno y devuelve `reply`, hora de captura y estado de conexión.

Antes de usar recomendaciones en producción hacen falta sensores calibrados, perfiles por cultivo y validación agronómica de cada texto y umbral.
