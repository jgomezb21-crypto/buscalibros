import { useEffect, useMemo, useState } from "react";
import "./App.css";

/* Tipos */
type Registro = {
  id: number;
  nombre: string;
  categoria?: string | null;
  fecha?: string | null;
  valor?: number | null;
  lat?: number | null;
  lon?: number | null;
};

type Page<T> =
  | T[]
  | { count: number; next: string | null; previous: string | null; results: T[] };

/* Config */
const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

/* Utils */
const getResults = <T,>(d: Page<T>) => (Array.isArray(d) ? d : d.results ?? []);
const getCount = <T,>(d: Page<T>) => (Array.isArray(d) ? d.length : d.count);
const isAbs = (u: string) => /^https?:\/\//i.test(u);
const isAbort = (e: unknown) =>
  (e as any)?.name === "AbortError" ||
  String((e as any)?.message ?? "").toLowerCase().includes("interrump") ||
  String((e as any)?.message ?? "").toLowerCase().includes("abort");

async function fetchJSON<T>(url: string, signal?: AbortSignal): Promise<T> {
  const r = await fetch(url, { signal, headers: { Accept: "application/json" } });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return (await r.json()) as T;
}

function useDebounce<T>(v: T, ms = 350) {
  const [val, setVal] = useState(v);
  useEffect(() => {
    const id = setTimeout(() => setVal(v), ms);
    return () => clearTimeout(id);
  }, [v, ms]);
  return val;
}

export default function App() {
  const [status, setStatus] = useState("…");
  const [items, setItems] = useState<Registro[]>([]);
  const [count, setCount] = useState<number | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Registro | null>(null);

  // Controles
  const [q, setQ] = useState("");
  const qDeb = useDebounce(q, 350);
  const [categoria, setCategoria] = useState(""); // filtro por categoría
  const [ordering, setOrdering] = useState<"" | "nombre" | "-nombre">("");
  const [pageSize] = useState(12);

  // Paginación
  const [nextUrl, setNextUrl] = useState<string | null>(null);
  const [prevUrl, setPrevUrl] = useState<string | null>(null);

  // URL base con parámetros
  const baseUrl = useMemo(() => {
    const p = new URLSearchParams();
    if (qDeb.trim()) p.set("search", qDeb.trim());
    if (categoria.trim()) p.set("categoria", categoria.trim()); // backend filtra exacto
    if (ordering) p.set("ordering", ordering);
    p.set("page_size", String(pageSize));
    return `${API}/api/registros/${p.toString() ? `?${p}` : ""}`;
  }, [qDeb, categoria, ordering, pageSize]);

  // Health + carga de datos
  useEffect(() => {
    const ac = new AbortController();
    const { signal } = ac;

    fetchJSON<{ status: string }>(`${API}/health`, signal)
      .then((d) => setStatus(d.status === "OK" ? "OK" : "FAIL"))
      .catch((e) => !isAbort(e) && setStatus("ERROR"));

    setLoading(true);
    setError(null);

    fetchJSON<Page<Registro>>(baseUrl, signal)
      .then((d) => {
        setItems(getResults(d));
        setCount(getCount(d));
        setNextUrl(Array.isArray(d) ? null : d.next ?? null);
        setPrevUrl(Array.isArray(d) ? null : d.previous ?? null);
        setLoading(false);
      })
      .catch((e) => {
        if (!isAbort(e)) setError(e instanceof Error ? e.message : String(e));
        setLoading(false);
      });

    return () => ac.abort();
  }, [baseUrl]);

  // Paginación con next/prev
  async function go(dir: "next" | "prev") {
    const url = dir === "next" ? nextUrl : prevUrl;
    if (!url) return;
    setLoading(true);
    setError(null);
    const target = isAbs(url) ? url : `${API}${url.startsWith("/") ? "" : "/"}${url}`;
    try {
      const d = await fetchJSON<Page<Registro>>(target);
      setItems(getResults(d));
      setCount(getCount(d));
      setNextUrl(Array.isArray(d) ? null : d.next ?? null);
      setPrevUrl(Array.isArray(d) ? null : d.previous ?? null);
    } catch (e) {
      if (!isAbort(e)) setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="wrap">
      <header className="hero">
        <h1>Buscalibros</h1>
        <p>
          API: <code>{API}</code> • Estado:{" "}
          <strong className={status === "OK" ? "ok" : "bad"}>{status}</strong>{" "}
          {typeof count === "number" && <>• {count} registro(s)</>}
        </p>
      </header>

      {/* Barra de búsqueda / filtros */}
      <div className="toolbar">
        <input
          className="input"
          placeholder="Buscar por nombre…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <input
          className="input"
          placeholder="Categoría (exacta)…"
          value={categoria}
          onChange={(e) => setCategoria(e.target.value)}
          list="sugerencias-categoria"
        />
        <datalist id="sugerencias-categoria">
          {[...new Set(items.map((i) => i.categoria).filter(Boolean))]
            .slice(0, 20)
            .map((c) => (
              <option key={String(c)} value={String(c)} />
            ))}
        </datalist>

        <select
          className="select"
          value={ordering}
          onChange={(e) => setOrdering(e.target.value as any)}
        >
          <option value="">(Sin orden)</option>
          <option value="nombre">Nombre A–Z</option>
          <option value="-nombre">Nombre Z–A</option>
        </select>
      </div>

      <h2>Registros</h2>

      {loading && (
        <div className="grid">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card skeleton" />
          ))}
        </div>
      )}

      {error && <p className="err">Error: {error}</p>}

      {!loading && !error && items.length === 0 && (
        <p className="muted">Sin resultados.</p>
      )}

      {!loading && !error && items.length > 0 && (
        <>
          <div className="grid">
            {items.map((r) => (
              <article
                key={r.id}
                className="card"
                onClick={() => setSelected(r)}
              >
                <div className="card-head">
                  <span className="badge">{r.categoria ?? "—"}</span>
                  <span className="id">#{r.id}</span>
                </div>
                <h3 className="title">{r.nombre}</h3>
                <dl className="meta">
                  <div>
                    <dt>Fecha</dt>
                    <dd>{r.fecha ?? "—"}</dd>
                  </div>
                  <div>
                    <dt>Valor</dt>
                    <dd>{r.valor ?? "—"}</dd>
                  </div>
                  <div>
                    <dt>Lat/Lon</dt>
                    <dd>
                      {r.lat ?? "—"} / {r.lon ?? "—"}
                    </dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>

          <div className="pager">
            <button className="btn" onClick={() => go("prev")} disabled={!prevUrl}>
              ← Anterior
            </button>
            <button className="btn" onClick={() => go("next")} disabled={!nextUrl}>
              Siguiente →
            </button>
          </div>
        </>
      )}

      {/* Modal de detalle */}
      {selected && (
        <div className="modal" onClick={() => setSelected(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <button className="close" onClick={() => setSelected(null)}>
              ×
            </button>
            <h3>{selected.nombre}</h3>
            <p className="muted">
              ID #{selected.id} • {selected.categoria ?? "Sin categoría"}
            </p>
            <ul className="detail">
              <li>
                <strong>Fecha:</strong> {selected.fecha ?? "—"}
              </li>
              <li>
                <strong>Valor:</strong> {selected.valor ?? "—"}
              </li>
              <li>
                <strong>Coordenadas:</strong> {selected.lat ?? "—"} / {selected.lon ?? "—"}
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
