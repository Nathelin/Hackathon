"""Contrato de simulación y perfil de lechuga; sin dependencias externas."""
import math

PROFILE = {
    "id": "lettuce-demo-v1", "name": "Lechuga hidropónica · demostración",
    "note": "Rangos orientativos. Los límites críticos son reglas de aviso del prototipo, no límites universales de daño. Temperatura y humedad corresponden al aire.",
    "sources": [
        {"title": "Cornell · Hydroponic Lettuce Handbook", "url": "https://cpb-us-e1.wpmucdn.com/blogs.cornell.edu/dist/8/8824/files/2019/06/Cornell-CEA-Lettuce-Handbook-.pdf"},
        {"title": "Oklahoma State · Conductividad y pH", "url": "https://extension.okstate.edu/fact-sheets/electrical-conductivity-and-ph-guide-for-hydroponics"},
    ],
}
# pH/EC: solución nutritiva. Temperatura/humedad: aire del invernadero.
SPECS = {
    "ph": dict(label="pH de la solución", pin=34, unit="pH", minimum=0, maximum=14,
               normal=[5.6, 6.0], critical=[4.5, 7.5],
               low="La acidez puede alterar la disponibilidad de nutrientes. Verificá con una sonda calibrada antes de ajustar la solución.",
               high="El pH elevado puede limitar micronutrientes. Confirmá la medición y revisá la solución nutritiva."),
    "humidity": dict(label="Humedad del aire", pin=33, unit="% HR", minimum=0, maximum=100,
                     normal=[50, 70], critical=[30, 90],
                     low="El aire seco aumenta la demanda de agua. Revisá ventilación y humedad ambiental.",
                     high="La humedad alta favorece condensación y enfermedades. Revisá circulación de aire y superficies húmedas."),
    "ec": dict(label="Conductividad", pin=32, unit="mS/cm", minimum=0, maximum=5,
               normal=[1.2, 1.8], critical=[0.5, 3.0],
               low="La solución puede estar demasiado diluida. Verificá la EC y la preparación de nutrientes.",
               high="La concentración de sales puede dificultar la absorción de agua. Revisá EC, agua de reposición y mezcla."),
    "temperature": dict(label="Temperatura del aire", pin=35, unit="°C", minimum=0, maximum=45,
                        normal=[19, 24], critical=[10, 32],
                        low="El frío puede ralentizar el crecimiento. Revisá el ambiente y la protección térmica.",
                        high="El calor puede causar estrés y favorecer espigado en lechuga. Revisá sombreo y ventilación."),
}


def from_raw(raw, spec):
    if type(raw) is not int or not 0 <= raw <= 4095:
        raise ValueError("ADC debe ser un entero entre 0 y 4095")
    return round(spec["minimum"] + raw / 4095 * (spec["maximum"] - spec["minimum"]), 3)


def serial_metrics(frame):
    if not isinstance(frame, dict) or not isinstance(frame.get("channels"), list):
        raise ValueError("Se esperan cuatro canales ADC")
    channels = frame["channels"]
    if len(channels) != 4 or any(not isinstance(c, dict) or type(c.get("pin")) is not int for c in channels):
        raise ValueError("Canales inválidos")
    by_pin = {c["pin"]: c for c in channels}
    if set(by_pin) != {34, 33, 32, 35}:
        raise ValueError("Faltan pines o hay duplicados")
    return {key: {"pin": s["pin"], "raw": by_pin[s["pin"]].get("raw"),
                  "value": from_raw(by_pin[s["pin"]].get("raw"), s)} for key, s in SPECS.items()}


def validate_metrics(metrics):
    if not isinstance(metrics, dict) or set(metrics) != set(SPECS):
        raise ValueError("Se requieren ph, humidity, ec y temperature")
    result = {}
    for key, spec in SPECS.items():
        m = metrics[key]
        if not isinstance(m, dict) or type(m.get("pin")) is not int or m["pin"] != spec["pin"]:
            raise ValueError(f"Pin inválido para {key}")
        value = from_raw(m.get("raw"), spec)
        reported = m.get("value")
        if type(reported) not in (int, float) or not math.isfinite(reported) or abs(reported-value) > .002:
            raise ValueError(f"Valor inconsistente con ADC para {key}")
        low, high = spec["normal"]
        clow, chigh = spec["critical"]
        level = "critical" if value <= clow or value >= chigh else "warning" if value < low or value > high else "safe"
        result[key] = dict(m, value=value, level=level, direction="low" if value < low else "high" if value > high else "normal",
                           advice=spec["low"] if value < low else spec["high"] if value > high else "Dentro del objetivo del perfil de demostración.")
    return result
