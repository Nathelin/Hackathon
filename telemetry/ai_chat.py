"""Chat determinista sobre la captura actual; no usa servicios externos."""
import secrets


MODEL_NAME = 'Analizador local por reglas'
METRIC_ORDER = ('ph', 'humidity', 'ec', 'temperature')
KEYWORDS = {
    'ph': ('ph', 'p.h', 'acidez', 'alcalin'),
    'humidity': ('humedad', 'aire seco', 'condensacion', 'condensación'),
    'ec': ('conductividad', ' ec ', 'sales', 'nutriente'),
    'temperature': ('temperatura', 'calor', 'frio', 'frío', 'termic', 'térmic'),
}
LEVEL_TEXT = {'safe': 'en objetivo', 'warning': 'fuera del objetivo', 'critical': 'en nivel crítico'}


class ChatError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def _format(value, key):
    decimals = 2 if key in ('ph', 'ec') else 1
    return f'{value:.{decimals}f}'.replace('.', ',')


def _metric_line(key, metric, spec):
    value = _format(metric['value'], key)
    low, high = spec['normal']
    status = LEVEL_TEXT[metric['level']]
    if metric['level'] == 'safe':
        return (f"✓ {spec['label']}: {value} {spec['unit']}. Está {status} "
                f"({low:g}–{high:g} {spec['unit']}).")
    severity = 'Atención' if metric['level'] == 'warning' else 'Crítico'
    direction = 'por debajo' if metric['direction'] == 'low' else 'por encima'
    return (f"{'!' if metric['level'] == 'warning' else '⚠'} {spec['label']}: {value} {spec['unit']}. "
            f"Está {status} y {direction} del objetivo ({low:g}–{high:g} {spec['unit']}).\n"
            f"  {severity}: {metric['advice']}")


def _relationships(metrics):
    notes = []
    temperature = metrics['temperature']
    humidity = metrics['humidity']
    ph = metrics['ph']
    ec = metrics['ec']
    if temperature['direction'] == 'high' and humidity['direction'] == 'low':
        notes.append('Temperatura alta y humedad baja aparecen juntas: el ambiente simulado combina calor y aire seco. Revisá ventilación, sombreo y la medición de humedad antes de actuar.')
    elif temperature['direction'] == 'high' and humidity['direction'] == 'high':
        notes.append('Temperatura y humedad altas aparecen juntas: revisá circulación de aire y condensación, además del control térmico.')
    elif temperature['direction'] == 'low' and humidity['direction'] == 'high':
        notes.append('Temperatura baja y humedad alta aparecen juntas: controlá superficies húmedas y ventilación sin provocar más enfriamiento.')
    if ph['level'] != 'safe' and ec['level'] != 'safe':
        notes.append('pH y conductividad están fuera del objetivo al mismo tiempo. Confirmá ambos con instrumentos calibrados y revisá la preparación de la solución antes de corregirla; estos potenciómetros sólo simulan sensores.')
    return notes


def analyze(snapshot, question):
    latest = snapshot.get('latest')
    if not snapshot.get('connected') or not latest:
        return ('No puedo describir el estado actual porque el ESP32 no tiene una lectura vigente. '
                'El tablero conserva la última captura sólo como referencia y no la interpreta como condición actual. '
                'Revisá la conexión USB y volvé a consultar cuando figure “datos en vivo”.')

    metrics = latest['metrics']
    specs = snapshot['specs']
    normalized = f" {question.casefold()} "
    focused = [key for key in METRIC_ORDER if any(word in normalized for word in KEYWORDS[key])]
    selected = focused or list(METRIC_ORDER)
    critical = [key for key in METRIC_ORDER if metrics[key]['level'] == 'critical']
    warning = [key for key in METRIC_ORDER if metrics[key]['level'] == 'warning']
    safe = [key for key in METRIC_ORDER if metrics[key]['level'] == 'safe']

    if critical:
        opening = f"Veo {len(critical)} parámetro{'s' if len(critical) != 1 else ''} en nivel crítico"
        if warning:
            opening += f" y {len(warning)} que necesita{'n' if len(warning) != 1 else ''} atención"
        opening += '. Empezaría por los críticos y confirmaría esas lecturas antes de hacer ajustes.'
    elif warning:
        opening = f"No veo niveles críticos. Hay {len(warning)} parámetro{'s que necesitan' if len(warning) != 1 else ' que necesita'} atención porque salió del objetivo. Conviene revisarlo antes de que se aleje más."
    else:
        opening = ('Por ahora se ve todo bien: las cuatro lecturas están dentro del objetivo del perfil de lechuga. '
                   'La condición simulada es favorable; podés mantener el monitoreo habitual.')

    priority = {'critical': 0, 'warning': 1, 'safe': 2}
    if not focused:
        selected = sorted(selected, key=lambda key: (priority[metrics[key]['level']], METRIC_ORDER.index(key)))
    lines = [opening, '', 'Esto es lo que muestran los datos:',
             *(_metric_line(key, metrics[key], specs[key]) for key in selected)]
    relations = _relationships(metrics)
    if relations and not focused:
        lines.extend(['', 'Mirando los valores en conjunto:', *relations])
    if focused and len(selected) < len(METRIC_ORDER):
        other_bad = [specs[key]['label'] for key in METRIC_ORDER if key not in selected and metrics[key]['level'] != 'safe']
        if other_bad:
            lines.extend(['', 'También detecté otros valores para revisar: ' + ', '.join(other_bad) + '. Si querés, pedime un resumen completo.'])
    if safe and (critical or warning):
        lines.extend(['', 'Lo que está bien: ' + ', '.join(specs[key]['label'] for key in safe) + '.'])
    return '\n'.join(lines)


class Chat:
    def __init__(self):
        self.token = secrets.token_urlsafe(32)

    def config(self):
        return {'configured': True, 'model': MODEL_NAME, 'csrf_token': self.token,
                'external_api': False, 'cost': 0}

    def ask(self, body, snapshot):
        if not isinstance(body, dict):
            raise ChatError('Se espera una consulta JSON.')
        question = body.get('message', '')
        history = body.get('history', [])
        if not isinstance(question, str) or not 1 <= len(question.strip()) <= 1200:
            raise ChatError('La consulta debe tener entre 1 y 1200 caracteres.')
        if not isinstance(history, list) or len(history) > 6:
            raise ChatError('Enviar como máximo seis mensajes anteriores.')
        total = 0
        for item in history:
            if (not isinstance(item, dict) or item.get('role') not in ('user', 'assistant')
                    or not isinstance(item.get('content'), str) or len(item['content']) > 2000):
                raise ChatError('Historial inválido.')
            total += len(item['content'])
        if total > 8000:
            raise ChatError('El historial supera el límite de contexto.')
        return {'reply': analyze(snapshot, question.strip()), 'model': MODEL_NAME,
                'incomplete': False, 'usage': {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0},
                'captured_at': snapshot.get('latest', {}).get('captured_at') if snapshot.get('latest') else None,
                'connected_at_analysis': bool(snapshot.get('connected'))}
