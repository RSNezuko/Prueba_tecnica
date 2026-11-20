import os
from typing import Literal, List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="API Gestor de Tareas", version="1.0.0")

# Permitir peticiones desde el frontend en React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de conexión a PostgreSQL
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "gestor_tareas"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "port": os.getenv("DB_PORT", "5432"),
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


# Esquemas de validación de datos
class TareaCreate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    prioridad: Literal["alta", "media", "baja"]

    @field_validator("titulo")
    @classmethod
    def titulo_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El título no puede estar vacío ni contener solo espacios.")
        return v.strip()


class TareaResponse(BaseModel):
    id: int
    titulo: str
    prioridad: str
    completada: bool


# 4.1. Registrar una tarea
@app.post("/api/tareas", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(tarea: TareaCreate):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tareas (titulo, prioridad, completada)
                VALUES (%s, %s, FALSE)
                RETURNING id, titulo, prioridad, completada;
                """,
                (tarea.titulo, tarea.prioridad),
            )
            nueva_tarea = cur.fetchone()
            conn.commit()
            return nueva_tarea
    finally:
        conn.close()


# 4.2. Consultar todas las tareas
@app.get("/api/tareas", response_model=List[TareaResponse])
def listar_tareas():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, prioridad, completada FROM tareas ORDER BY id ASC;")
            return cur.fetchall()
    finally:
        conn.close()


# 4.3. Buscar una tarea por ID
@app.get("/api/tareas/{tarea_id}", response_model=TareaResponse)
def buscar_tarea(tarea_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, titulo, prioridad, completada FROM tareas WHERE id = %s;",
                (tarea_id,),
            )
            tarea = cur.fetchone()
            if not tarea:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No se encontró ninguna tarea con el ID {tarea_id}.",
                )
            return tarea
    finally:
        conn.close()


# 4.4. Completar una tarea
@app.patch("/api/tareas/{tarea_id}/completar", response_model=TareaResponse)
def completar_tarea(tarea_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, titulo, prioridad, completada FROM tareas WHERE id = %s;",
                (tarea_id,),
            )
            tarea = cur.fetchone()

            if not tarea:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No se encontró ninguna tarea con el ID {tarea_id}.",
                )

            if tarea["completada"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La tarea con ID {tarea_id} ya se encuentra completada.",
                )

            cur.execute(
                """
                UPDATE tareas
                SET completada = TRUE
                WHERE id = %s
                RETURNING id, titulo, prioridad, completada;
                """,
                (tarea_id,),
            )
            tarea_actualizada = cur.fetchone()
            conn.commit()
            return tarea_actualizada
    finally:
        conn.close()


# 4.5. Eliminar una tarea
@app.delete("/api/tareas/{tarea_id}")
def eliminar_tarea(tarea_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tareas WHERE id = %s RETURNING id;", (tarea_id,))
            eliminada = cur.fetchone()
            if not eliminada:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No se encontró ninguna tarea con el ID {tarea_id}.",
                )
            conn.commit()
            return {"mensaje": f"Tarea con ID {tarea_id} eliminada correctamente."}
    finally:
        conn.close()