# Grupo 3

Proyecto desarrollado para el Hackathon de Hidroponía 2026, orientado al monitoreo de distintas condiciones de los tanques en los invernaderos de los productores. El frontend está desarrollado con Vue 3, TypeScript y Vite.

## Tecnologías principales

- Vue 3 con Composition API y `<script setup>`.
- TypeScript para tipado estático.
- Vite como servidor de desarrollo y herramienta de compilación.
- Tailwind CSS 4 para estilos y modo claro/oscuro.
- Vue Router 4 para la navegación.
- ApexCharts para gráficos y visualización de lecturas.
- FullCalendar, Leaflet, Swiper y Flatpickr para calendarios, mapas, carruseles y selectores de fecha.
- ESLint y Prettier para calidad y formato del código.

## Requisitos

- Node.js 20.19 o superior, o Node.js 22.12 o superior.
- npm, incluido con Node.js.
- Git.

Comprueba las versiones instaladas con:

```bash
node --version
npm --version
git --version
```

## Clonar y ejecutar

1. Clona el repositorio:

	```bash
	git clone <URL>
	```

2. Entra en la carpeta de la aplicación:

	```bash
	cd Hackathon/dashboard
	```

3. Instala las dependencias:

	```bash
	npm install
	```

4. Inicia el servidor de desarrollo:

	```bash
	npm run dev
	```

Abre la dirección que muestre Vite, normalmente `http://localhost:5173/`.

## Comandos disponibles

```bash
npm run dev         # Inicia el servidor de desarrollo
npm run build       # Comprueba tipos y genera la versión de producción
npm run preview     # Previsualiza la compilación de producción
npm run type-check  # Ejecuta la comprobación de TypeScript
npm run lint        # Ejecuta ESLint
npm run format      # Formatea el código de src/
```

La compilación de producción se genera en `dashboard/dist/`. No es necesario subir `node_modules/` ni `dist/` al repositorio.

## Estructura principal

```text
dashboard/
├── public/          # Imágenes y recursos públicos
├── src/
│   ├── components/  # Componentes reutilizables y layouts
│   ├── data/        # Datos de sensores y modelos de dominio
│   ├── router/      # Rutas de la aplicación
│   ├── views/       # Pantallas del dashboard
│   └── App.vue      # Componente principal
├── package.json     # Dependencias y scripts
└── vite.config.ts   # Configuración de Vite
```
