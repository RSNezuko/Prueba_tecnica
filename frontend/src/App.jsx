import { useState, useEffect } from "react";
import "./App.css";

const API_URL = "http://localhost:8000/api/tareas";

export default function App() {
  const [tareas, setTareas] = useState([]);
  const [titulo, setTitulo] = useState("");
  const [prioridad, setPrioridad] = useState("media");
  const [busquedaId, setBusquedaId] = useState("");
  const [tareaEncontrada, setTareaEncontrada] = useState(null);
  const [mensaje, setMensaje] = useState({ texto: "", tipo: "" });

  const mostrarNotificacion = (texto, tipo = "exito") => {
    setMensaje({ texto, tipo });
    setTimeout(() => setMensaje({ texto: "", tipo: "" }), 4000);
  };

  // 4.2. Consultar todas las tareas
  const cargarTareas = async () => {
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      setTareas(data);
    } catch {
      mostrarNotificacion("Error al conectar con el servidor.", "error");
    }
  };

  useEffect(() => {
    cargarTareas();
  }, []);

  // 4.1. Registrar una tarea
  const handleCrear = async (e) => {
    e.preventDefault();
    if (!titulo.trim()) {
      mostrarNotificacion("El título no puede estar vacío.", "error");
      return;
    }

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ titulo, prioridad }),
      });

      const data = await res.json();
      if (!res.ok) {
        mostrarNotificacion(data.detail || "Error al registrar la tarea.", "error");
        return;
      }

      setTitulo("");
      setPrioridad("media");
      mostrarNotificacion("Tarea registrada correctamente.");
      cargarTareas();
    } catch {
      mostrarNotificacion("No se pudo registrar la tarea.", "error");
    }
  };

  // 4.3. Buscar una tarea por ID
  const handleBuscar = async (e) => {
    e.preventDefault();
    if (!busquedaId) return;

    try {
      const res = await fetch(`${API_URL}/${busquedaId}`);
      const data = await res.json();

      if (!res.ok) {
        setTareaEncontrada(null);
        mostrarNotificacion(data.detail, "error");
        return;
      }

      setTareaEncontrada(data);
    } catch {
      mostrarNotificacion("Error al buscar la tarea.", "error");
    }
  };

  // 4.4. Completar una tarea
  const handleCompletar = async (id) => {
    try {
      const res = await fetch(`${API_URL}/${id}/completar`, {
        method: "PATCH",
      });
      const data = await res.json();

      if (!res.ok) {
        mostrarNotificacion(data.detail, "error");
        return;
      }

      mostrarNotificacion(`Tarea #${id} marcada como completada.`);
      if (tareaEncontrada && tareaEncontrada.id === id) {
        setTareaEncontrada(data);
      }
      cargarTareas();
    } catch {
      mostrarNotificacion("Error al completar la tarea.", "error");
    }
  };

  // 4.5. Eliminar una tarea
  const handleEliminar = async (id) => {
    try {
      const res = await fetch(`${API_URL}/${id}`, {
        method: "DELETE",
      });
      const data = await res.json();

      if (!res.ok) {
        mostrarNotificacion(data.detail, "error");
        return;
      }

      mostrarNotificacion(data.mensaje);
      if (tareaEncontrada && tareaEncontrada.id === id) {
        setTareaEncontrada(null);
      }
      cargarTareas();
    } catch {
      mostrarNotificacion("Error al eliminar la tarea.", "error");
    }
  };

  return (
    <div className="container">
      <h1>Gestor de Tareas del Equipo</h1>

      {mensaje.texto && (
        <div className={`alerta ${mensaje.tipo}`}>{mensaje.texto}</div>
      )}

      {/* Formulario de registro */}
      <section className="card">
        <h2>Nueva Tarea</h2>
        <form onSubmit={handleCrear} className="form-inline">
          <input
            type="text"
            placeholder="Descripción de la tarea..."
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
          />
          <select
            value={prioridad}
            onChange={(e) => setPrioridad(e.target.value)}
          >
            <option value="alta">Prioridad: Alta</option>
            <option value="media">Prioridad: Media</option>
            <option value="baja">Prioridad: Baja</option>
          </select>
          <button type="submit">Agregar</button>
        </form>
      </section>

      {/* Buscador por ID */}
      <section className="card">
        <h2>Buscar Tarea por ID</h2>
        <form onSubmit={handleBuscar} className="form-inline">
          <input
            type="number"
            min="1"
            placeholder="ID de la tarea"
            value={busquedaId}
            onChange={(e) => setBusquedaId(e.target.value)}
          />
          <button type="submit">Buscar</button>
          {tareaEncontrada && (
            <button
              type="button"
              className="btn-secundario"
              onClick={() => {
                setTareaEncontrada(null);
                setBusquedaId("");
              }}
            >
              Limpiar
            </button>
          )}
        </form>

        {tareaEncontrada && (
          <div className="resultado-busqueda">
            <strong>Resultado:</strong> #{tareaEncontrada.id} -{" "}
            {tareaEncontrada.titulo} | Prioridad:{" "}
            <span className={`badge ${tareaEncontrada.prioridad}`}>
              {tareaEncontrada.prioridad}
            </span>{" "}
            | Estado:{" "}
            {tareaEncontrada.completada ? "Completada" : "Pendiente"}
          </div>
        )}
      </section>

      {/* Listado general */}
      <section className="card">
        <h2>Lista de Tareas ({tareas.length})</h2>
        {tareas.length === 0 ? (
          <p className="vacio">No hay tareas registradas.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Título</th>
                <th>Prioridad</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tareas.map((tarea) => (
                <tr
                  key={tarea.id}
                  className={tarea.completada ? "fila-completada" : ""}
                >
                  <td>{tarea.id}</td>
                  <td>{tarea.titulo}</td>
                  <td>
                    <span className={`badge ${tarea.prioridad}`}>
                      {tarea.prioridad}
                    </span>
                  </td>
                  <td>{tarea.completada ? "Completada" : "Pendiente"}</td>
                  <td className="acciones">
                    <button
                      onClick={() => handleCompletar(tarea.id)}
                      className="btn-completar"
                    >
                      Completar
                    </button>
                    <button
                      onClick={() => handleEliminar(tarea.id)}
                      className="btn-eliminar"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}