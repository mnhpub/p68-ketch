import {useState} from 'react';
import {BIRDSEYE, CUTAWAYS, ENGINEERING, ENGINEERING_PDF, EXTERIORS, FINISH_PLANS, INTERIORS, RENDERS, SHEETS, type Shot} from './projections/drawings';
import './scope.css';

// Presentation only. Sheet and render lists come from the drawings projection.
function ShotGroup({title, shots, open}: {title: string; shots: Shot[]; open: (src: string) => void}) {
  return (
    <>
      <h2 className="sheet-group">{title}</h2>
      <div className="sheet-grid">
        {shots.map((r) => (
          <figure key={r.file} className="sheet">
            <button type="button" onClick={() => open(`/renders/${r.file}`)} aria-label={`Open ${r.title}`}>
              <img src={`/renders/${r.file}`} alt={`${r.title}. ${r.note}. Blender concept render.`} loading="lazy" />
            </button>
            <figcaption><b>{r.title}</b><span>{r.note}</span></figcaption>
          </figure>
        ))}
      </div>
    </>
  );
}

export default function DrawingsView() {
  const [open, setOpen] = useState<string | null>(null);
  return (
    <section className="drawings">
      <div className="explorer-head">
        <span className="eyebrow">LAYOUT / PROVISIONAL / NOT FOR CONSTRUCTION</span>
        <h1>Drawings and renders.</h1>
        <p>
          Engineering deck plans are AutoCAD DXF sources generated from the layout data; plans and elevations are schematic.
          Finish-out, exterior and interior renders are built in Blender from the DXF geometry with proposed finishes and
          indicative furniture. AI renders are concept illustrations for mood and material only.
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

      <ShotGroup title="Finish-out plans" shots={FINISH_PLANS} open={setOpen} />
      <ShotGroup title="Finish-out cutaways" shots={CUTAWAYS} open={setOpen} />
      <ShotGroup title="Exterior renders: at port, at anchor, underway" shots={EXTERIORS} open={setOpen} />
      <ShotGroup title="Interior renders: controls, features, accommodation" shots={INTERIORS} open={setOpen} />

      <h2 className="sheet-group">Concept renders (AI)</h2>
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
