# Grupo 3

Proyecto web desarrollado con Vue 3, TypeScript y Vite.

## Requisitos

- Node.js 20.19 o superior (o Node.js 22.12 o superior).
- npm, incluido con Node.js.
- Git.
- Un IDE.

Puedes comprobar las versiones instaladas con:

```bash
node --version
npm --version
git --version
```

## Instalación

1. Clona el repositorio:

	```bash
	git clone <URL>
	```

2. Entra en la carpeta del proyecto:

	```bash
	cd dashboard
	```

3. Instala las dependencias:

	```bash
	npm install
	```

## Desarrollo

Inicia el servidor de desarrollo con recarga automática:

```bash
npm run dev
```

Vite mostrará en la terminal la dirección local, normalmente `http://localhost:5173/`. Abre esa dirección en el navegador.

Para detener el servidor, pulsa `Ctrl+C` en la terminal.

## Compilación y previsualización

Comprueba que el proyecto compila correctamente y genera la versión de producción en `dist/`:

```bash
npm run build
```

Para previsualizar localmente esa compilación:

```bash
npm run preview
```

## Estructura principal

```text
src/
├── App.vue          # Componente principal
├── main.ts          # Punto de entrada de la aplicación
├── style.css        # Estilos globales
├── assets/          # Recursos estáticos importados por la aplicación
└── components/      # Componentes Vue reutilizables
public/              # Archivos públicos servidos sin transformación
```

## Flujo de trabajo recomendado

1. Ejecuta `npm install` después de clonar el repositorio o cuando cambien las dependencias.
2. Trabaja con `npm run dev` mientras desarrollas.
3. Ejecuta `npm run build` antes de entregar cambios para comprobar tipos y compilación.
4. No subas `node_modules/` ni `dist/` al repositorio; ambos se generan automáticamente.

## Tecnologías

- [Vue 3](https://vuejs.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vite.dev/)
