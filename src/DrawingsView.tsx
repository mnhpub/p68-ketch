import {useState} from 'react';
import {BIRDSEYE, ENGINEERING, ENGINEERING_PDF, RENDERS, SHEETS} from './projections/drawings';
import './scope.css';

// Presentation only. Sheet and render lists come from the drawings projection.
export default function DrawingsView() {
  const [open, setOpen] = useState<string | null>(null);
  return (
    <section className="drawings">
      <div className="explorer-head">
        <span className="eyebrow">LAYOUT / PROVISIONAL / NOT FOR CONSTRUCTION</span>
        <h1>Drawings and renders.</h1>
        <p>
          Deck plans and elevations are generated from the layout data and are schematic. Renders are AI concept illustrations
          for mood and material only.
        </p>
      </div>

      <h2 className="sheet-group">Engineering deck plans</h2>
      <p className="sheet-links">
        A3 at 1:200, plotted from the AutoCAD DXF sources. <a href={`/drawings/${ENGINEERING_PDF}`} download>Download the PDF set</a>
      </p>
      <div className="sheet-grid">
        {ENGINEERING.map((s) => (
          <figure key={s.file} className="sheet">
            <button type="button" onClick={() => setOpen(`/drawings/${s.file}`)} aria-label={`Open ${s.title}`}>
              <img src={`/drawings/${s.file}`} alt={`${s.title}: ${s.note}`} loading="lazy" />
            </button>
            <figcaption>
              <b>{s.title}</b>
              <span>{s.note}</span>
              <a href={`/drawings/cad/${s.dxf}`} download>DXF source</a>
            </figcaption>
          </figure>
        ))}
      </div>

      <h2 className="sheet-group">Plans and elevations</h2>
      <div className="sheet-grid">
        {SHEETS.map((s) => (
          <figure key={s.file} className="sheet">
            <button type="button" onClick={() => setOpen(`/drawings/${s.file}`)} aria-label={`Open ${s.title}`}>
              <img src={`/drawings/${s.file}`} alt={`${s.title}: ${s.note}`} loading="lazy" />
            </button>
            <figcaption><b>{s.title}</b><span>{s.note}</span></figcaption>
          </figure>
        ))}
      </div>

      <h2 className="sheet-group">Bird's-eye views and area maps</h2>
      <div className="sheet-grid">
        {BIRDSEYE.map((s) => (
          <figure key={s.file} className="sheet">
            <button type="button" onClick={() => setOpen(`/drawings/${s.file}`)} aria-label={`Open ${s.title}`}>
              <img src={`/drawings/${s.file}`} alt={`${s.title}: ${s.note}`} loading="lazy" />
            </button>
            <figcaption><b>{s.title}</b><span>{s.note}</span></figcaption>
          </figure>
        ))}
      </div>

      <h2 className="sheet-group">Concept renders</h2>
      <div className="sheet-grid">
        {RENDERS.map((r) => (
          <figure key={r.file} className="sheet">
            <button type="button" onClick={() => setOpen(`/renders/${r.file}`)} aria-label={`Open ${r.title}`}>
              <img src={`/renders/${r.file}`} alt={`${r.title}. Concept illustration.`} loading="lazy" />
            </button>
            <figcaption><b>{r.title}</b><span>Concept illustration</span></figcaption>
          </figure>
        ))}
      </div>

      {open && (
        <div className="lightbox" onClick={() => setOpen(null)} role="dialog" aria-label="Enlarged view">
          <button type="button" onClick={() => setOpen(null)}>CLOSE ×</button>
          <img src={open} alt="Enlarged view" />
        </div>
      )}
    </section>
  );
}
