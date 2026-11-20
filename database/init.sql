CREATE TABLE IF NOT EXISTS tareas (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL CHECK (LENGTH(TRIM(titulo)) > 0),
    prioridad VARCHAR(10) NOT NULL CHECK (prioridad IN ('alta', 'media', 'baja')),
    completada BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO tareas (titulo, prioridad, completada)
VALUES ('Corregir error de inicio de sesión', 'alta', FALSE);