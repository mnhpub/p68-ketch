import {scopeCoverage, scopeOpenItems, scopeRows} from './projections/scope';
import './scope.css';

// Presentation only. The rows and coverage come from the scope projection.
export default function ScopeView() {
  const rows = scopeRows();
  const {covered, total} = scopeCoverage();
  return (
    <section className="scope">
      <div className="explorer-head">
        <span className="eyebrow">SCOPE / BRIEF COVERAGE</span>
        <h1>Scope and status.</h1>
        <p>
          Every item from the brief, where it appears in the app, where it sits on the provisional layout, and what is still
          open. {covered} of {total} items are covered in the app.
        </p>
      </div>

      <div className="scope-table" role="table" aria-label="Scope items">
        <div className="scope-row scope-head" role="row">
          <span role="columnheader">Brief item</span>
          <span role="columnheader">Register entry</span>
          <span role="columnheader">Layout</span>
          <span role="columnheader">Status</span>
        </div>
        {rows.map((r) => (
          <div className="scope-row" role="row" key={r.item}>
            <span role="cell"><b>{r.item}</b></span>
            <span role="cell">{r.register}</span>
            <span role="cell">{r.layout}</span>
            <span role="cell" className={`status-${r.status}`}>{r.statusLabel}</span>
          </div>
        ))}
      </div>

      <div className="review-box">
        <h3>Open items</h3>
        {scopeOpenItems().map((o) => (
          <div key={o}>
            <strong>Open</strong>
            <span>{o}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
