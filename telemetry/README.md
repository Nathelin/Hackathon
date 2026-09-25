# HydroGuard: versión local con API REST

El dashboard principal de `dashboard/` muestra las cuatro señales del ESP32 en **Invernadero 1 / Tanque 1**. La cadena es:

`B10K → ADC del ESP32 → USB 115200 → bridge.py → POST REST → api.py → dashboard Vue`

Python no recibe señales eléctricas directamente: el ESP32 las digitaliza y envía líneas JSON. El lector usa el ADC `raw`, por lo que es compatible con el firmware anterior de cuatro canales (ignora sus campos `ph`). No hace falta recargar la placa para esta actualización. Se incluye también un sketch reproducible en `firmware/HydroGuard/HydroGuard.ino`.

## Mapeo y perfil de simulación

| Pin del cursor B10K | Métrica | Escala de simulación | Objetivo | Crítico (inclusive) |
|---|---|---|---|---|
| G34 | pH de solución nutritiva | 0–14 | 5.6–6.0 | ≤4.5 / ≥7.5 |
| G33 | Humedad relativa del aire | 0–100 % HR | 50–70 % | ≤30 / ≥90 % |
| G32 | Conductividad de solución | 0–5 mS/cm | 1.2–1.8 mS/cm | ≤0.5 / ≥3.0 mS/cm |
| G35 | Temperatura del aire | 0–45 °C | 19–24 °C | ≤10 / ≥32 °C |

Los extremos de cada B10K van a **3V3 y GND común**, nunca a 5 V. El orden en que llega el JSON no importa: se identifica cada canal por `pin`. `raw=0` es una lectura válida; una entrada flotante no se puede distinguir de un sensor físico averiado usando sólo un ADC. No se inventa un cero si el ESP32 deja de transmitir.

Elegimos lechuga por ser el cultivo principal de ejemplo del proyecto. El [manual de Cornell](https://cpb-us-e1.wpmucdn.com/blogs.cornell.edu/dist/8/8824/files/2019/06/Cornell-CEA-Lettuce-Handbook-.pdf), §3.3, propone pH 5.6–6.0, humedad 50–70 % y temperaturas de aire de 24 °C de día / 19 °C de noche. Aquí esas temperaturas se simplifican a una banda operativa. La [guía de Oklahoma State](https://extension.okstate.edu/fact-sheets/electrical-conductivity-and-ph-guide-for-hydroponics) propone EC 1.2–1.8 mS/cm para lechuga y un rango de pH diferente; se eligió el perfil de Cornell para pH, no una supuesta regla universal.

Los límites críticos son **decisiones conservadoras de diseño del prototipo**, no umbrales experimentales de muerte o daño publicados por esas universidades. Variedad, etapa, duración de exposición, luz y temperatura de agua modifican el riesgo. Fuera del objetivo pero dentro de los críticos se informa “Atención”. Las reglas están centralizadas en `domain.py`; los avisos no dependen de IA. Hay un chat local de textos predeterminados, sin servicios externos ni control automático de bombas/dosificación. El nivel de agua y el estado de la bomba no se infieren de estos cuatro canales.

## Inicio local

Requisitos: Linux, Python 3.10+, Node compatible con el proyecto Vue y acceso al puerto serial. No se agregaron dependencias npm/Python.

```bash
cd /home/matir/Hidroponia/Main/Hackathon/dashboard
npm run build
cd ../telemetry
bash run_local.sh
```

Abrir **http://127.0.0.1:8080/** en esta computadora. No abrir un HTML por `file://`. Para desarrollo: mantener la API activa y ejecutar `npm run dev` en `dashboard/`; Vite ya redirige `/api` al backend local.

En esta máquina quedó actualizado el servicio existente `hydroguard-dashboard.service`, que inicia ambos procesos y conserva el arranque automático. **No ejecutar simultáneamente el lector de `Prototipo #1`, Arduino Monitor Serie o Web Serial**. El nuevo lector abre el puerto de manera exclusiva.

```bash
systemctl --user status hydroguard-dashboard.service
systemctl --user restart hydroguard-dashboard.service
journalctl --user -u hydroguard-dashboard.service -f
curl http://127.0.0.1:8080/api/health
```

Para ejecución manual, primero detener el servicio. `run_local.py` crea `config.env` con un token aleatorio local y permisos 0600. Ese archivo está excluido de git. `config.env.example` documenta las opciones. Los secretos nunca se envían a Vue. En otra PC, ajustar `HYDRO_SERIAL` al enlace de `/dev/serial/by-id/`; no se sondean puertos ajenos a la placa elegida.

El supervisor reinicia API/lector si alguno termina. Si la PC está apagada o suspendida no puede recibir ni notificar. No se puede prometer disponibilidad absoluta frente a fallas físicas o pérdida de alimentación.

## Reconexión y datos vencidos

- Búsqueda USB cada 0.5 s cuando no hay dispositivo; reintento con espera acotada de hasta 3 s tras errores.
- Puerto de identidad estable, apertura completa 115200 8N1, sin control de flujo heredado; RTS/DTR liberados para evitar mantener EN/BOOT activados.
- Hasta 6 s para el primer JSON válido; 3 s sin **tramas válidas** cierran/reabren el puerto. El ruido no renueva el plazo.
- Buffer de línea acotado y validación de los cuatro GPIO, ADC entero 0–4095, unidades y valores. No se aceptan `NaN`, tramas incompletas ni canales duplicados.
- La API considera vencida la lectura tras 4 s. Desconexión no equivale a cero; la UI muestra “—” y deja de indicar condiciones actuales.
- HTTP funciona en un hilo separado con timeout de 2 s: una API caída no bloquea el USB. Cada trama válida se encola para envío. Cola de 32 elementos; ante caída/saturación se descartan las más viejas, nunca se hace replay indefinido de datos obsoletos. Se retoma con nuevas lecturas.
- La web consulta cada 500 ms, con timeout y reintentos, y no necesita recargarse después de una reconexión.

## API REST v1

Sólo escucha en loopback para esta prueba local. GET es lectura local; los POST de telemetría/bridge requieren `Authorization: Bearer <HYDRO_API_TOKEN>` y `Content-Type: application/json`. Máximo 16 KB por cuerpo. Valores inválidos → 400; secreto inválido → 401; ruta inexistente → 404; cuerpo excesivo → 413. El chat utiliza otro contrato y protección local, documentados en [ANALISIS_LOCAL.md](ANALISIS_LOCAL.md).

| Método | Ruta | Uso |
|---|---|---|
| POST | `/api/v1/telemetry` | Enviar una captura con las cuatro métricas |
| POST | `/api/v1/bridge/status` | Latido/estado del lector serial |
| GET | `/api/v1/telemetry/latest` | Lectura vigente, diagnóstico, perfil, gráficos y alertas |
| GET | `/api/health` | Mismo estado para diagnóstico |

Ejemplo de cuerpo (reemplazar `captured_at` por el tiempo Unix actual, en segundos):

```json
{
  "device_id": "esp32-hydro-1",
  "simulation": true,
  "greenhouse_id": 1,
  "tank_id": 1,
  "captured_at": 1790300000.1,
  "metrics": {
    "ph": {"pin": 34, "raw": 0, "value": 0},
    "humidity": {"pin": 33, "raw": 0, "value": 0},
    "ec": {"pin": 32, "raw": 0, "value": 0},
    "temperature": {"pin": 35, "raw": 0, "value": 0}
  }
}
```

Los IDs omitidos toman valor 1; otros destinos se rechazan en este prototipo. Cada `value` debe corresponder al ADC y la escala. Se rechazan capturas duplicadas, fuera de orden o mayores a 15 s. Estado, últimas 120 muestras (a ~1 Hz) y últimos 100 avisos viven **sólo en RAM**. Reiniciar API borra estos datos; no representa un histórico de producción.

## Alertas

`State.evaluate()` ejecuta el notificador en la primera lectura que entra en nivel crítico. Se requiere recuperación durante 5 s antes de cerrar la incidencia; si después vuelve a entrar en nivel crítico, crea un aviso nuevo de inmediato. No se envía un correo por cada trama mientras el evento sigue activo.

La campana del dashboard usa las alertas de esta API (ya no datos de ejemplo). Cada evento crítico nuevo y reciente abre un aviso destacado dentro de la página, sin pedir permisos del navegador. Se deduplica por ID, no por lectura; el cierre no resuelve el incidente. Si llegan varias alertas, quedan en una cola acotada y se muestran al cerrar la anterior. Los eventos viejos siguen en la campana, pero no reaparecen como avisos flotantes al recargar. El botón “Probar aviso crítico” sólo prueba la presentación: no cambia las lecturas ni manda correo.

También se pueden habilitar notificaciones del sistema con el botón de la página; requieren permiso y la página abierta. No son push móvil en segundo plano.

Para correo, completar `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM`, `SMTP_USER`, `SMTP_PASSWORD` y `ALERT_EMAIL_TO` en `config.env`, y reiniciar el servicio. Usa STARTTLS, cola limitada y estado visible: no configurado / en cola / enviado / falló. Sin credenciales **no se afirma haber enviado correos**. Los correos llevan `[SIMULACIÓN]`. No se hizo un envío real durante la instalación.

## Pruebas

```bash
cd telemetry
python3 -m unittest -v
cd ../dashboard
npm run build
```

Se cubren mapeo/extremos ADC, validación, cero válido, límites de riesgo, alerta crítica inmediata, recuperación y reentrada, API autenticada, JSON fragmentado/ruido continuo, desconexión y reconexión con cambio de dispositivo virtual, y caída/recuperación de API usando el proceso bridge real. El chat prueba condiciones favorables, varios problemas simultáneos, relaciones predeterminadas, preguntas enfocadas, datos vencidos y protección de acceso, sin Internet.

Prueba física: abrir dashboard, girar cada B10K, desenchufar USB y comprobar estado desconectado, volver a enchufar y esperar la recuperación. Los tests con pseudo-terminales reproducen el flujo del sistema, pero no sustituyen probar el cable y el adaptador físicos.

## Vercel: prueba futura, no desplegada

Consulta de documentación oficial: 24/09/2026. Hobby incluye, bajo Fluid Compute: **1 millón de invocaciones**, **1 millón de Edge Requests**, **4 horas de CPU activa**, **360 GB-h de memoria**, **100 GB de transferencia** y **10 GB de transferencia de origen**. Superar cupos puede suspender el recurso; no es capacidad ilimitada. Hobby se limita a uso personal/no comercial: una suscripción vendida a productores requiere un plan comercial. [Plan Hobby](https://vercel.com/docs/plans/hobby).

Las Functions de Hobby tienen máximo de **300 s**, **2 GB de memoria** y cuerpo de petición/respuesta máximo de **4.5 MB**. No sirven para ejecutar permanentemente el lector USB: ese proceso queda en la computadora conectada al ESP32. [Límites de Functions](https://vercel.com/docs/functions/limitations).

El servidor actual es local y mantiene estado en RAM. **No desplegarlo sin cambios en Vercel**: para esa prueba se necesitan handlers serverless del mismo contrato, almacenamiento compartido para última lectura/alertas (por ejemplo una base de datos), deduplicación atómica, autenticación por usuario/equipo, HTTPS y protección de lectura. El emisor ya admite otra URL mediante `HYDRO_API_URL`, pero la API remota debe existir y satisfacer ese contrato. No se configuró ninguna cuenta ni se publicó información.

Con el firmware actual (una trama cada 150 ms), los POST de telemetría solos serían aproximadamente **17.28 millones / 30 días**, más consultas web y latidos. Un panel abierto 24/7 a 500 ms añade **5.184 millones** de GET. Para la nube habría que reducir explícitamente la frecuencia o agrupar capturas: POST y GET cada 10 s suman ~518,400 invocaciones/30 días por un dispositivo + un visor, antes de otros pedidos. No alcanza con alojar el mismo bucle sin cambiar su frecuencia. En local se respeta un POST por cada trama válida recibida.

Para venderlo todavía faltan validación con sensores físicos, histórico persistente, multiusuario, aislamiento por cliente, reglas por cultivo y mecanismo de entrega/reintento persistente de alertas. El chat explica las lecturas simuladas con reglas transparentes; cada texto y umbral requiere validación con datos de cultivo antes de ofrecer recomendaciones productivas. Ver [alcance del analizador local](ANALISIS_LOCAL.md).
