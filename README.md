# Gestor de Tareas del Equipo

Aplicación web Full Stack para administrar las tareas pendientes de un equipo de desarrollo. Permite registrar, consultar, buscar por ID, completar y eliminar tareas con persistencia en base de datos relacional.

---

## 1. Qué lenguaje utilizaste

* **Backend:** **Python 3.11** utilizando **FastAPI** para construir la API REST, **Pydantic** para la validación de esquemas y tipos de datos, y **Psycopg2** para la conexión y ejecución de consultas SQL en PostgreSQL.
* **Frontend:** **JavaScript (ES6+)** con **React 18** (empaquetado con **Vite**) y **CSS3** para el diseño y estilos de la interfaz.
* **Base de datos:** **SQL** sobre **PostgreSQL 16** con restricciones de integridad (`CHECK`, `NOT NULL`, `PRIMARY KEY`).
* **Infraestructura:** **Docker** y **Docker Compose** para la orquestación de los servicios.

---

## 2. Cómo ejecutar el programa

### Requisitos previos
* Tener instalado **Docker** y **Docker Compose** (Docker Desktop en Windows/macOS o Docker Engine en Linux).
* Asegurarse de que los puertos `5173`, `8000` y `5432` estén disponibles en el equipo.

### Levantar los contenedores
Abre una terminal en la carpeta raíz del proyecto y ejecuta:

```bash
docker compose up --build
```

Al ejecutar este comando:
1. **PostgreSQL** creará automáticamente la base de datos `gestor_tareas` y ejecutará el script `database/init.sql` para crear la tabla `tareas` con un registro inicial de prueba.
2. **FastAPI** esperará a que PostgreSQL pase su `healthcheck` antes de iniciar la API en el puerto `8000`.
3. **React** iniciará el servidor web en el puerto `5173`.

### Acceder a la aplicación
Una vez que los servicios estén activos en la terminal, abre en tu navegador:

* **Aplicación Web (Frontend React):** [http://localhost:5173](http://localhost:5173)
* **Documentación interactiva de la API (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)


## 3. Qué funcionalidades implementaste

Se implementaron todos los requerimientos funcionales solicitados, con validación tanto en el frontend como en el backend y la base de datos:

1. **Registrar una tarea (`POST /api/tareas`):**
   * Crea una nueva tarea asignándole un `id` único autoincremental.
   * Valida que el `titulo` no esté vacío ni compuesto únicamente por espacios en blanco (retorna `422` si es inválido).
   * Valida que la `prioridad` sea exclusivamente `alta`, `media` o `baja`.
   * Registra toda tarea nueva por defecto como pendiente (`completada = false`).
2. **Consultar todas las tareas (`GET /api/tareas`):**
   * Obtiene y muestra todas las tareas registradas ordenadas por `id` ascendente junto con su título, prioridad y estado.
3. **Buscar una tarea (`GET /api/tareas/{id}`):**
   * Permite buscar una tarea específica utilizando su `id`.
   * Si la tarea no existe, la API responde con HTTP `404` y la interfaz informa al usuario mediante una notificación.
4. **Completar una tarea (`PATCH /api/tareas/{id}/completar`):**
   * Permite marcar una tarea pendiente como completada (`completada = true`).
   * Si la tarea no existe (`404`) o si ya estaba completada (`400`), el sistema informa al usuario en pantalla sin alterar la base de datos.
5. **Eliminar una tarea (`DELETE /api/tareas/{id}`):**
   * Elimina una tarea de la base de datos utilizando su `id`.
   * Si el `id` no existe, devuelve HTTP `404` e informa al usuario.

---

## 4. Si existe alguna funcionalidad pendiente

* **Ninguna.** Todos los requerimientos funcionales y técnicos solicitados en la prueba fueron completados y verificados mediante pruebas unitarias y manuales.

---

## 5. Qué recursos o herramientas de apoyo utilizaste

* **Documentación oficial:** Guías oficiales de FastAPI, Pydantic, Psycopg2, PostgreSQL, React y Docker Compose.
* **Inteligencia Artificial:** Utilizada como herramienta de apoyo puntual para:
  * La revisión y estructuración de las pruebas unitarias con `pytest` y `TestClient`.
  * Apoyo en el diseño base de las hojas de estilo en CSS.
  * La configuración de los archivos de contenedores (`Dockerfile` y `docker-compose.yml`).
  * La configuración inicial del entorno de React con Vite (`package.json` y `vite.config.js`).