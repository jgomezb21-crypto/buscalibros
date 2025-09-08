import { useEffect, useState } from "react";

type Registro = {
  id: string;
  nombre: string;
  categoria?: string | null;
  fecha?: string | null;
  valor?: number | null;
  lat?: number | null;
  lon?: number | null;
};

// Usa VITE_API_URL si la defines en .env, si no, cae a 127.0.0.1
const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export default function App() {
  const [status, setStatus] = useState("...");
  const [items, setItems] = useState<Registro[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();

    // health
    fetch(`${API}/api/health/`, { signal: ac.signal })
      .then((r) => r.json())
      .then((d) => setStatus(d?.ok ? "OK" : "FAIL"))
      .catch(() => setStatus("ERROR"));

    // registros
    fetch(`${API}/api/registros/`, { signal: ac.signal })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => setItems(Array.isArray(d) ? d : d.results ?? []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));

    return () => ac.abort();
  }, []);

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: 24 }}>
      <h1>Buscalibros</h1>
      <p>API status: {status}</p>

      <h2>Registros</h2>
      {loading && <p>Cargando…</p>}
      {error && <p style={{ color: "crimson" }}>Error: {error}</p>}

      {!loading && !error && (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Categoría</th>
              <th>Fecha</th>
              <th>Valor</th>
              <th>Lat</th>
              <th>Lon</th>
            </tr>
          </thead>
          <tbody>
            {items.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.nombre}</td>
                <td>{r.categoria ?? ""}</td>
                <td>{r.fecha ?? ""}</td>
                <td>{r.valor ?? ""}</td>
                <td>{r.lat ?? ""}</td>
                <td>{r.lon ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
