export type SensorEstado = 'operativo' | 'revision' | 'sin_conexion' | 'fuera_servicio'

export type SensorTipo =
  'ph' | 'ec' | 'temperatura' | 'humedad_aire' | 'humedad_sustrato' | 'luz_par' | 'nivel_tanque'

export type BombaEstado = 'operativa' | 'detenida' | 'alarma'

export interface Sector {
  id: string
  nombre: string
  invernadero: string
  superficie: string
}

export interface Plantacion {
  id: string
  cultivo: string
  variedad: string
  fechaSiembra: string
  sectorId: string
}

export interface Revision {
  fecha: string
  tecnico: string
  detalle: string
}

export interface Lectura {
  fecha: string
  valor: number
}

export interface RangoNormal {
  min: number
  max: number
}

export interface Medicion {
  tipo: SensorTipo
  ultimaLectura: Lectura
  rangoNormal: RangoNormal
  serie24h: number[]
  serie7d: number[]
}

export interface Dispositivo {
  id: string
  codigo: string
  nombre: string
  sectorId: string
  plantacionId: string
  ubicacionDetalle: string
  tanqueId?: string
  estado: SensorEstado
  ultimaRevision: string
  tecnicoRevision: string
  proximaRevision: string
  instalado: string
  firmware: string
  bateria: number
  senal: number
  mediciones: Medicion[]
  revisiones: Revision[]
}

export interface Tanque {
  id: string
  nombre: string
  sectorId: string
  cama: string
  capacidadLitros: number
  dispositivoId: string
  bomba: BombaEstado
}

export const hoy = '2026-09-24'

export const tipoSensor: Record<SensorTipo, { label: string; unidad: string }> = {
  ph: { label: 'pH', unidad: 'pH' },
  ec: { label: 'Conductividad (EC)', unidad: 'mS/cm' },
  temperatura: { label: 'Temperatura', unidad: '°C' },
  humedad_aire: { label: 'Humedad ambiental', unidad: '%' },
  humedad_sustrato: { label: 'Humedad de sustrato', unidad: '%' },
  luz_par: { label: 'Luz PAR', unidad: 'µmol/m²·s' },
  nivel_tanque: { label: 'Nivel de agua', unidad: '%' },
}

export const estadoSensor: Record<
  SensorEstado,
  { label: string; color: 'success' | 'warning' | 'error' | 'info' }
> = {
  operativo: { label: 'Operativo', color: 'success' },
  revision: { label: 'Requiere revisión', color: 'warning' },
  sin_conexion: { label: 'Sin conexión', color: 'info' },
  fuera_servicio: { label: 'Fuera de servicio', color: 'error' },
}

export const bombaEstado: Record<
  BombaEstado,
  { label: string; color: 'success' | 'warning' | 'error' | 'info' }
> = {
  operativa: { label: 'Operativa', color: 'success' },
  detenida: { label: 'Detenida', color: 'info' },
  alarma: { label: 'Alarma', color: 'error' },
}

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

export const etiquetas24h = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`)

export const etiquetas7d = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

export function formatoFecha(iso: string): string {
  const [anio, mes, dia] = iso.split('-')
  return `${dia} ${MESES[Number(mes) - 1]} ${anio}`
}

export function formatoFechaHora(iso: string): string {
  const [fecha, hora] = iso.split('T')
  return `${formatoFecha(fecha)}, ${hora}`
}

export function formatoHora(iso: string): string {
  return iso.split('T')[1] ?? ''
}

export function diasDesde(iso: string): number {
  const desde = Date.parse(`${iso}T00:00:00`)
  const hasta = Date.parse(`${hoy}T00:00:00`)
  return Math.round((hasta - desde) / 86400000)
}

function serie(seed: number, base: number, amplitud: number, puntos: number): number[] {
  let s = seed
  const siguiente = () => {
    s = (s * 1664525 + 1013904223) % 4294967296
    return s / 4294967296
  }
  return Array.from({ length: puntos }, () =>
    Number((base + (siguiente() - 0.5) * amplitud).toFixed(2)),
  )
}

function crearSeries(seed: number, base: number, amplitud: number, valorActual: number) {
  const serie24h = serie(seed, base, amplitud, 24)
  const serie7d = serie(seed + 7, base, amplitud * 1.5, 7)
  serie24h[serie24h.length - 1] = valorActual
  serie7d[serie7d.length - 1] = valorActual
  return { serie24h, serie7d }
}

export const sectores: Sector[] = [
  {
    id: 'sec-a',
    nombre: 'Sector A – Bancadas Norte',
    invernadero: 'Invernadero 1',
    superficie: '420 m²',
  },
  {
    id: 'sec-b',
    nombre: 'Sector B – Bancadas Sur',
    invernadero: 'Invernadero 1',
    superficie: '380 m²',
  },
  {
    id: 'sec-c',
    nombre: '',
    invernadero: 'Invernadero 2',
    superficie: '260 m²',
  },
  {
    id: 'sec-d',
    nombre: 'Banco de aclimatación',
    invernadero: 'Vivero',
    superficie: '150 m²',
  },
]

export const plantaciones: Plantacion[] = [
  {
    id: 'pla-1',
    cultivo: 'Lechuga romana',
    variedad: '',
    fechaSiembra: '2026-08-12',
    sectorId: 'sec-a',
  },
  {
    id: 'pla-2',
    cultivo: 'Albahaca genovesa',
    variedad: 'Genovese',
    fechaSiembra: '2026-08-28',
    sectorId: 'sec-b',
  },
  {
    id: 'pla-3',
    cultivo: 'Tomillo limón',
    variedad: 'Limón',
    fechaSiembra: '2026-07-15',
    sectorId: 'sec-c',
  },
  {
    id: 'pla-4',
    cultivo: 'Plantines de tomate',
    variedad: 'Cocktail',
    fechaSiembra: '2026-09-01',
    sectorId: 'sec-d',
  },
]

export const tanques: Tanque[] = [
  {
    id: 'tq-a',
    nombre: 'Tanque A',
    sectorId: 'sec-a',
    cama: 'Bancada Norte',
    capacidadLitros: 900,
    dispositivoId: 'sn-020',
    bomba: 'operativa',
  },
  {
    id: 'tq-b',
    nombre: 'Tanque B',
    sectorId: 'sec-b',
    cama: 'Bancada Sur',
    capacidadLitros: 900,
    dispositivoId: 'sn-021',
    bomba: 'operativa',
  },
  {
    id: 'tq-norte',
    nombre: 'Tanque Norte',
    sectorId: 'sec-c',
    cama: 'Bancada 1',
    capacidadLitros: 1000,
    dispositivoId: 'sn-007',
    bomba: 'alarma',
  },
  {
    id: 'tq-sur',
    nombre: 'Tanque Sur',
    sectorId: 'sec-c',
    cama: 'Bancada 2',
    capacidadLitros: 800,
    dispositivoId: 'sn-008',
    bomba: 'operativa',
  },
  {
    id: 'tq-respaldo',
    nombre: 'Tanque de respaldo',
    sectorId: 'sec-c',
    cama: 'Bancada 2',
    capacidadLitros: 500,
    dispositivoId: 'sn-017',
    bomba: 'detenida',
  },
]

export const dispositivos: Dispositivo[] = [
  {
    id: 'sn-001',
    codigo: 'SNS-001',
    nombre: 'Sonda de pH principal',
    sectorId: 'sec-a',
    plantacionId: 'pla-1',
    ubicacionDetalle: 'Mesa 1, fila A',
    estado: 'operativo',
    ultimaRevision: '2026-09-05',
    tecnicoRevision: 'M. Fernández',
    proximaRevision: '2026-12-05',
    instalado: '2026-03-18',
    firmware: 'v2.4.1',
    bateria: 92,
    senal: 88,
    mediciones: [
      {
        tipo: 'ph',
        ultimaLectura: { fecha: '2026-09-24T10:42', valor: 5.9 },
        rangoNormal: { min: 5.5, max: 6.5 },
        ...crearSeries(11, 5.9, 0.5, 5.9),
      },
    ],
    revisiones: [
      {
        fecha: '2026-09-05',
        tecnico: 'M. Fernández',
        detalle: 'Calibración con soluciones pH 4.0 y 7.0',
      },
      {
        fecha: '2026-06-05',
        tecnico: 'M. Fernández',
        detalle: 'Limpieza de electrodos y revisión de junta',
      },
      { fecha: '2026-03-18', tecnico: 'A. Ríos', detalle: 'Instalación y verificación inicial' },
    ],
  },
  {
    id: 'sn-002',
    codigo: 'SNS-002',
    nombre: 'Sensor de conductividad',
    sectorId: 'sec-a',
    plantacionId: 'pla-1',
    ubicacionDetalle: 'Mesa 2, fila B',
    estado: 'operativo',
    ultimaRevision: '2026-09-05',
    tecnicoRevision: 'M. Fernández',
    proximaRevision: '2026-12-05',
    instalado: '2026-03-18',
    firmware: 'v2.4.1',
    bateria: 78,
    senal: 84,
    mediciones: [
      {
        tipo: 'ec',
        ultimaLectura: { fecha: '2026-09-24T10:41', valor: 1.6 },
        rangoNormal: { min: 1.2, max: 2.4 },
        ...crearSeries(23, 1.6, 0.5, 1.6),
      },
    ],
    revisiones: [
      {
        fecha: '2026-09-05',
        tecnico: 'M. Fernández',
        detalle: 'Verificación con solución patrón 1.413 mS/cm',
      },
      {
        fecha: '2026-05-20',
        tecnico: 'L. Ortiz',
        detalle: 'Limpieza de sonda y sellado del cable',
      },
    ],
  },
  {
    id: 'sn-003',
    codigo: 'SNS-003',
    nombre: 'Sonda de humedad de sustrato',
    sectorId: 'sec-a',
    plantacionId: 'pla-1',
    ubicacionDetalle: 'Mesa 3, fila A',
    estado: 'revision',
    ultimaRevision: '2026-06-18',
    tecnicoRevision: 'L. Ortiz',
    proximaRevision: '2026-09-18',
    instalado: '2026-03-18',
    firmware: 'v2.3.8',
    bateria: 41,
    senal: 76,
    mediciones: [
      {
        tipo: 'humedad_sustrato',
        ultimaLectura: { fecha: '2026-09-24T10:38', valor: 52 },
        rangoNormal: { min: 40, max: 70 },
        ...crearSeries(37, 52, 14, 52),
      },
    ],
    revisiones: [
      {
        fecha: '2026-06-18',
        tecnico: 'L. Ortiz',
        detalle: 'Reemplazo de sonda por desgaste del elemento',
      },
      { fecha: '2026-03-18', tecnico: 'A. Ríos', detalle: 'Instalación en línea de riego' },
    ],
  },
  {
    id: 'sn-004',
    codigo: 'SNS-004',
    nombre: 'Termopar de ambiente',
    sectorId: 'sec-b',
    plantacionId: 'pla-2',
    ubicacionDetalle: 'Mesa 1, fila C',
    estado: 'operativo',
    ultimaRevision: '2026-08-30',
    tecnicoRevision: 'A. Ríos',
    proximaRevision: '2026-11-30',
    instalado: '2026-04-02',
    firmware: 'v2.4.1',
    bateria: 87,
    senal: 91,
    mediciones: [
      {
        tipo: 'temperatura',
        ultimaLectura: { fecha: '2026-09-24T10:44', valor: 23.4 },
        rangoNormal: { min: 18, max: 26 },
        ...crearSeries(41, 23, 3.5, 23.4),
      },
    ],
    revisiones: [
      {
        fecha: '2026-08-30',
        tecnico: 'A. Ríos',
        detalle: 'Verificación con termómetro de referencia',
      },
      {
        fecha: '2026-05-30',
        tecnico: 'A. Ríos',
        detalle: 'Ajuste de calibración',
      },
    ],
  },
  {
    id: 'sn-005',
    codigo: 'SNS-005',
    nombre: 'Higrómetro ambiental',
    sectorId: 'sec-b',
    plantacionId: 'pla-2',
    ubicacionDetalle: 'Mesa 2, fila A',
    estado: 'operativo',
    ultimaRevision: '2026-08-30',
    tecnicoRevision: 'A. Ríos',
    proximaRevision: '2026-11-30',
    instalado: '2026-04-02',
    firmware: 'v2.4.0',
    bateria: 65,
    senal: 79,
    mediciones: [
      {
        tipo: 'humedad_aire',
        ultimaLectura: { fecha: '2026-09-24T10:40', valor: 68 },
        rangoNormal: { min: 55, max: 75 },
        ...crearSeries(53, 68, 10, 68),
      },
    ],
    revisiones: [
      { fecha: '2026-08-30', tecnico: 'A. Ríos', detalle: 'Limpieza del filtro de aspiración' },
      {
        fecha: '2026-04-02',
        tecnico: 'A. Ríos',
        detalle: 'Instalación y emparejamiento con gateway',
      },
    ],
  },
  {
    id: 'sn-006',
    codigo: 'SNS-006',
    nombre: 'Sensor PAR de dosel',
    sectorId: 'sec-b',
    plantacionId: 'pla-2',
    ubicacionDetalle: 'Dosel, eje central',
    estado: 'sin_conexion',
    ultimaRevision: '2026-07-22',
    tecnicoRevision: 'L. Ortiz',
    proximaRevision: '2026-10-22',
    instalado: '2026-04-02',
    firmware: 'v2.4.0',
    bateria: 12,
    senal: 0,
    mediciones: [
      {
        tipo: 'luz_par',
        ultimaLectura: { fecha: '2026-09-23T18:05', valor: 310 },
        rangoNormal: { min: 200, max: 400 },
        ...crearSeries(67, 310, 90, 310),
      },
    ],
    revisiones: [
      { fecha: '2026-07-22', tecnico: 'L. Ortiz', detalle: 'Actualización de firmware a v2.4.0' },
      { fecha: '2026-04-02', tecnico: 'A. Ríos', detalle: 'Montaje en dosel y ajuste de altura' },
    ],
  },
  {
    id: 'sn-007',
    codigo: 'SNS-007',
    nombre: 'Dispositivo multi-sensor · Tanque Norte',
    sectorId: 'sec-c',
    plantacionId: 'pla-3',
    ubicacionDetalle: 'Tanque Norte · Bancada 1',
    tanqueId: 'tq-norte',
    estado: 'revision',
    ultimaRevision: '2026-06-01',
    tecnicoRevision: 'L. Ortiz',
    proximaRevision: '2026-09-01',
    instalado: '2026-02-20',
    firmware: 'v2.3.8',
    bateria: 18,
    senal: 69,
    mediciones: [
      {
        tipo: 'ph',
        ultimaLectura: { fecha: '2026-09-24T10:43', valor: 6.9 },
        rangoNormal: { min: 5.5, max: 6.5 },
        ...crearSeries(71, 6.4, 0.6, 6.9),
      },
      {
        tipo: 'ec',
        ultimaLectura: { fecha: '2026-09-24T10:41', valor: 1.9 },
        rangoNormal: { min: 1.4, max: 2.6 },
        ...crearSeries(141, 1.9, 0.4, 1.9),
      },
      {
        tipo: 'nivel_tanque',
        ultimaLectura: { fecha: '2026-09-24T10:45', valor: 17 },
        rangoNormal: { min: 20, max: 100 },
        ...crearSeries(97, 45, 30, 17),
      },
    ],
    revisiones: [
      {
        fecha: '2026-06-01',
        tecnico: 'L. Ortiz',
        detalle: 'Sustitución del flotador y purga de conducto',
      },
      { fecha: '2026-02-20', tecnico: 'A. Ríos', detalle: 'Instalación en depósito de nutrientes' },
    ],
  },
  {
    id: 'sn-008',
    codigo: 'SNS-008',
    nombre: 'Dispositivo multi-sensor · Tanque Sur',
    sectorId: 'sec-c',
    plantacionId: 'pla-3',
    ubicacionDetalle: 'Tanque Sur · Bancada 2',
    tanqueId: 'tq-sur',
    estado: 'operativo',
    ultimaRevision: '2026-09-10',
    tecnicoRevision: 'M. Fernández',
    proximaRevision: '2026-12-10',
    instalado: '2026-05-11',
    firmware: 'v2.4.1',
    bateria: 58,
    senal: 74,
    mediciones: [
      {
        tipo: 'ph',
        ultimaLectura: { fecha: '2026-09-24T10:43', valor: 5.7 },
        rangoNormal: { min: 5.5, max: 6.5 },
        ...crearSeries(149, 5.8, 0.5, 5.7),
      },
      {
        tipo: 'ec',
        ultimaLectura: { fecha: '2026-09-24T10:39', valor: 2.1 },
        rangoNormal: { min: 1.4, max: 2.6 },
        ...crearSeries(83, 2.1, 0.4, 2.1),
      },
      {
        tipo: 'nivel_tanque',
        ultimaLectura: { fecha: '2026-09-24T10:45', valor: 48 },
        rangoNormal: { min: 20, max: 100 },
        ...crearSeries(151, 55, 25, 48),
      },
    ],
    revisiones: [
      { fecha: '2026-09-10', tecnico: 'M. Fernández', detalle: 'Verificación con solución patrón' },
      { fecha: '2026-05-11', tecnico: 'A. Ríos', detalle: 'Instalación y alta en la red LoRaWAN' },
    ],
  },
  {
    id: 'sn-010',
    codigo: 'SNS-010',
    nombre: 'Termopar de aclimatación',
    sectorId: 'sec-d',
    plantacionId: 'pla-4',
    ubicacionDetalle: 'Módulo 1, estante alto',
    estado: 'operativo',
    ultimaRevision: '2026-09-12',
    tecnicoRevision: 'A. Ríos',
    proximaRevision: '2026-12-12',
    instalado: '2026-08-01',
    firmware: 'v2.4.1',
    bateria: 95,
    senal: 93,
    mediciones: [
      {
        tipo: 'temperatura',
        ultimaLectura: { fecha: '2026-09-24T10:42', valor: 24.8 },
        rangoNormal: { min: 20, max: 28 },
        ...crearSeries(101, 24, 3, 24.8),
      },
    ],
    revisiones: [
      { fecha: '2026-09-12', tecnico: 'A. Ríos', detalle: 'Calibración de rutina' },
      { fecha: '2026-08-01', tecnico: 'A. Ríos', detalle: 'Instalación en módulo de aclimatación' },
    ],
  },
  {
    id: 'sn-011',
    codigo: 'SNS-011',
    nombre: 'Higrómetro de aclimatación',
    sectorId: 'sec-d',
    plantacionId: 'pla-4',
    ubicacionDetalle: 'Módulo 2, estante bajo',
    estado: 'fuera_servicio',
    ultimaRevision: '2026-08-20',
    tecnicoRevision: 'L. Ortiz',
    proximaRevision: '2026-09-20',
    instalado: '2026-08-01',
    firmware: 'v2.4.0',
    bateria: 0,
    senal: 0,
    mediciones: [
      {
        tipo: 'humedad_aire',
        ultimaLectura: { fecha: '2026-09-21T07:15', valor: 61 },
        rangoNormal: { min: 55, max: 75 },
        ...crearSeries(113, 61, 8, 61),
      },
    ],
    revisiones: [
      {
        fecha: '2026-08-20',
        tecnico: 'L. Ortiz',
        detalle: 'Diagnóstico: fallo de placa, unidad en reposición',
      },
      { fecha: '2026-08-01', tecnico: 'A. Ríos', detalle: 'Instalación en módulo de aclimatación' },
    ],
  },
  {
    id: 'sn-012',
    codigo: 'SNS-012',
    nombre: 'Termopar de ambiente',
    sectorId: 'sec-c',
    plantacionId: 'pla-3',
    ubicacionDetalle: 'Mesa central, altura de dosel',
    estado: 'operativo',
    ultimaRevision: '2026-09-10',
    tecnicoRevision: 'M. Fernández',
    proximaRevision: '2026-12-10',
    instalado: '2026-05-11',
    firmware: 'v2.4.1',
    bateria: 81,
    senal: 86,
    mediciones: [
      {
        tipo: 'temperatura',
        ultimaLectura: { fecha: '2026-09-24T10:44', valor: 22.6 },
        rangoNormal: { min: 18, max: 26 },
        ...crearSeries(127, 22.5, 3.5, 22.6),
      },
    ],
    revisiones: [
      {
        fecha: '2026-09-10',
        tecnico: 'M. Fernández',
        detalle: 'Verificación con termómetro de referencia',
      },
      { fecha: '2026-05-11', tecnico: 'A. Ríos', detalle: 'Instalación en altura de dosel' },
    ],
  },
  {
    id: 'sn-013',
    codigo: 'SNS-013',
    nombre: 'Higrómetro ambiental',
    sectorId: 'sec-c',
    plantacionId: 'pla-3',
    ubicacionDetalle: 'Pasillo central, altura de dosel',
    estado: 'operativo',
    ultimaRevision: '2026-09-10',
    tecnicoRevision: 'M. Fernández',
    proximaRevision: '2026-12-10',
    instalado: '2026-05-11',
    firmware: 'v2.4.1',
    bateria: 74,
    senal: 83,
    mediciones: [
      {
        tipo: 'humedad_aire',
        ultimaLectura: { fecha: '2026-09-24T10:40', valor: 64 },
        rangoNormal: { min: 55, max: 75 },
        ...crearSeries(131, 64, 9, 64),
      },
    ],
    revisiones: [
      {
        fecha: '2026-09-10',
        tecnico: 'M. Fernández',
        detalle: 'Limpieza del filtro de aspiración',
      },
      { fecha: '2026-05-11', tecnico: 'A. Ríos', detalle: 'Instalación en altura de dosel' },
    ],
  },
  {
    id: 'sn-017',
    codigo: 'SNS-017',
    nombre: 'Dispositivo multi-sensor · Tanque de respaldo',
    sectorId: 'sec-c',
    plantacionId: 'pla-3',
    ubicacionDetalle: 'Tanque de respaldo · Bancada 2',
    tanqueId: 'tq-respaldo',
    estado: 'operativo',
    ultimaRevision: '2026-09-08',
    tecnicoRevision: 'M. Fernández',
    proximaRevision: '2026-12-08',
    instalado: '2026-05-11',
    firmware: 'v2.4.1',
    bateria: 58,
    senal: 71,
    mediciones: [
      {
        tipo: 'ph',
        ultimaLectura: { fecha: '2026-09-24T10:42', valor: 6.1 },
        rangoNormal: { min: 5.5, max: 6.5 },
        ...crearSeries(157, 6.0, 0.5, 6.1),
      },
      {
        tipo: 'ec',
        ultimaLectura: { fecha: '2026-09-24T10:40', valor: 2.3 },
        rangoNormal: { min: 1.4, max: 2.6 },
        ...crearSeries(163, 2.2, 0.4, 2.3),
      },
      {
        tipo: 'nivel_tanque',
        ultimaLectura: { fecha: '2026-09-24T10:46', valor: 12 },
        rangoNormal: { min: 20, max: 100 },
        ...crearSeries(167, 35, 25, 12),
      },
    ],
    revisiones: [
      { fecha: '2026-09-08', tecnico: 'M. Fernández', detalle: 'Calibración de electrodos' },
      { fecha: '2026-05-11', tecnico: 'A. Ríos', detalle: 'Instalación en tanque de respaldo' },
    ],
  },
  {
    id: 'sn-020',
    codigo: 'SNS-020',
    nombre: 'Dispositivo multi-sensor · Tanque A',
    sectorId: 'sec-a',
    plantacionId: 'pla-1',
    ubicacionDetalle: 'Tanque A · Bancada Norte',
    tanqueId: 'tq-a',
    estado: 'operativo',
    ultimaRevision: '2026-09-05',
    tecnicoRevision: 'M. Fernández',
    proximaRevision: '2026-12-05',
    instalado: '2026-03-18',
    firmware: 'v2.4.1',
    bateria: 88,
    senal: 87,
    mediciones: [
      {
        tipo: 'ph',
        ultimaLectura: { fecha: '2026-09-24T10:42', valor: 5.9 },
        rangoNormal: { min: 5.5, max: 6.5 },
        ...crearSeries(211, 5.9, 0.5, 5.9),
      },
      {
        tipo: 'ec',
        ultimaLectura: { fecha: '2026-09-24T10:41', valor: 1.6 },
        rangoNormal: { min: 1.2, max: 2.4 },
        ...crearSeries(223, 1.6, 0.5, 1.6),
      },
      {
        tipo: 'nivel_tanque',
        ultimaLectura: { fecha: '2026-09-24T10:45', valor: 72 },
        rangoNormal: { min: 20, max: 100 },
        ...crearSeries(227, 70, 15, 72),
      },
    ],
    revisiones: [
      {
        fecha: '2026-09-05',
        tecnico: 'M. Fernández',
        detalle: 'Calibración de sondas y verificación de nivel',
      },
      { fecha: '2026-03-18', tecnico: 'A. Ríos', detalle: 'Instalación en tanque de nutrientes' },
    ],
  },
  {
    id: 'sn-021',
    codigo: 'SNS-021',
    nombre: 'Dispositivo multi-sensor · Tanque B',
    sectorId: 'sec-b',
    plantacionId: 'pla-2',
    ubicacionDetalle: 'Tanque B · Bancada Sur',
    tanqueId: 'tq-b',
    estado: 'operativo',
    ultimaRevision: '2026-08-30',
    tecnicoRevision: 'A. Ríos',
    proximaRevision: '2026-11-30',
    instalado: '2026-04-02',
    firmware: 'v2.4.1',
    bateria: 84,
    senal: 89,
    mediciones: [
      {
        tipo: 'ph',
        ultimaLectura: { fecha: '2026-09-24T10:43', valor: 6.0 },
        rangoNormal: { min: 5.5, max: 6.5 },
        ...crearSeries(233, 6.0, 0.5, 6.0),
      },
      {
        tipo: 'ec',
        ultimaLectura: { fecha: '2026-09-24T10:41', valor: 1.8 },
        rangoNormal: { min: 1.4, max: 2.6 },
        ...crearSeries(239, 1.8, 0.5, 1.8),
      },
      {
        tipo: 'nivel_tanque',
        ultimaLectura: { fecha: '2026-09-24T10:46', valor: 65 },
        rangoNormal: { min: 20, max: 100 },
        ...crearSeries(241, 65, 15, 65),
      },
    ],
    revisiones: [
      {
        fecha: '2026-08-30',
        tecnico: 'A. Ríos',
        detalle: 'Calibración de sondas y prueba de bomba',
      },
      {
        fecha: '2026-04-02',
        tecnico: 'A. Ríos',
        detalle: 'Instalación y emparejamiento con gateway',
      },
    ],
  },
]

export function sectorPorId(id: string): Sector | undefined {
  return sectores.find((sector) => sector.id === id)
}

export function plantacionPorId(id: string): Plantacion | undefined {
  return plantaciones.find((plantacion) => plantacion.id === id)
}

export function dispositivoPorId(id: string): Dispositivo | undefined {
  return dispositivos.find((dispositivo) => dispositivo.id === id)
}

export function medicionPorTipo(dispositivo: Dispositivo, tipo: SensorTipo): Medicion | undefined {
  return dispositivo.mediciones.find((medicion) => medicion.tipo === tipo)
}

export function fechaUltimaLectura(dispositivo: Dispositivo): string {
  return dispositivo.mediciones.reduce(
    (max, medicion) => (medicion.ultimaLectura.fecha > max ? medicion.ultimaLectura.fecha : max),
    '',
  )
}

export function tanquePorId(id: string): Tanque | undefined {
  return tanques.find((tanque) => tanque.id === id)
}

export function tanquesDeInvernadero(invernadero: string): Tanque[] {
  return tanques.filter((tanque) => sectorPorId(tanque.sectorId)?.invernadero === invernadero)
}

export function dispositivoDelTanque(tanque: Tanque): Dispositivo | undefined {
  return dispositivoPorId(tanque.dispositivoId)
}

export function medicionEnAlerta(dispositivo: Dispositivo, medicion: Medicion): boolean {
  if (dispositivo.estado === 'sin_conexion' || dispositivo.estado === 'fuera_servicio') {
    return false
  }
  const { valor } = medicion.ultimaLectura
  return valor < medicion.rangoNormal.min || valor > medicion.rangoNormal.max
}

export function enAlerta(dispositivo: Dispositivo): boolean {
  return dispositivo.mediciones.some((medicion) => medicionEnAlerta(dispositivo, medicion))
}

export function revisionVencida(dispositivo: Dispositivo): boolean {
  return dispositivo.proximaRevision < hoy
}

export function bateriaBaja(dispositivo: Dispositivo): boolean {
  return dispositivo.bateria <= 20
}
