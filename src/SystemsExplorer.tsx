import {useMemo, useState} from 'react';
import {AlertTriangle, Lock} from 'lucide-react';
import {basisLabel, statusLabel, type Checklist, type Domain, type System} from './aggregates/system';
import './systems.css';

type Props = {
  domains: Domain[];
  systems: System[];
  checklists: Checklist[];
};

export default function SystemsExplorer({domains, systems, checklists}: Props) {
  const [domain, setDomain] = useState('all');
  const [selected, setSelected] = useState<string | null>(null);

  const visible = useMemo(
    () => systems.filter((s) => domain === 'all' || s.domain === domain),
    [domain, systems],
  );
  const current = visible.find((s) => s.id === selected) ?? visible[0];
  const domainLabel = (id: string) => domains.find((d) => d.id === id)?.label ?? id;

  return (
    <section className="systems-explorer">
      <div className="explorer-head">
        <span className="eyebrow">SYSTEMS REGISTER / CONCEPT STAGE</span>
        <h1>Systems by domain.</h1>
        <p>
          Each system separates what is known, what is a design target and what is still to be
          determined. Nothing here is reviewed or approved.
        </p>
      </div>

      <div className="deck-pills">
        <button className={domain === 'all' ? 'active' : ''} onClick={() => { setDomain('all'); setSelected(null); }}>
          All ({systems.length})
        </button>
        {domains.map((d) => (
          <button
            key={d.id}
            className={domain === d.id ? 'active' : ''}
            onClick={() => { setDomain(d.id); setSelected(null); }}
          >
            {d.label} ({systems.filter((s) => s.domain === d.id).length})
          </button>
        ))}
      </div>

      <div className="systems-frame">
        <div className="systems-list">
          {visible.length === 0 && <p className="systems-empty">No systems registered in this domain yet.</p>}
          {visible.map((s) => (
            <button
              key={s.id}
              className={`system-row ${current?.id === s.id ? 'sel' : ''}`}
              onClick={() => setSelected(s.id)}
            >
              <span>{s.name}</span>
              <small>{statusLabel[s.status]}{s.safety_critical ? ' · safety-critical' : ''}</small>
            </button>
          ))}
        </div>

        {current && (
          <article className="system-detail">
            <span className="eyebrow">{domainLabel(current.domain)}</span>
            <h2>{current.name}</h2>

            <div className="system-flags">
              {current.safety_critical && (
                <span className="flag warn"><AlertTriangle size={13} /> Safety-critical</span>
              )}
              {!current.public_release && (
                <span className="flag"><Lock size={13} /> Not for public release</span>
              )}
              <span className="flag">{statusLabel[current.status]}</span>
            </div>

            <p className="system-summary">{current.summary}</p>
            <div className="approval"><strong>APPROVAL</strong> {current.approval_status}</div>

            <h3>Key parameters</h3>
            <div className="param-list">
              {current.key_parameters.map((p) => (
                <div key={p.label} className="param">
                  <span>{p.label}</span>
                  <b>{p.value}</b>
                  <em>{basisLabel[p.basis]}</em>
                </div>
              ))}
            </div>

            <h3>Open risks</h3>
            <ul className="risk-list">
              {current.risks.map((r) => <li key={r}>{r}</li>)}
            </ul>

            {checklists.filter((c) => c.system === current.id).map((c) => (
              <div key={c.id} className="checklist">
                <h3>{c.title}</h3>
                <span className="flag warn">Draft, not for use on a vessel</span>
                <ol>
                  {c.steps.map((step) => (
                    <li key={step.text} className={step.critical ? 'critical' : ''}>
                      {step.critical && <b>CRITICAL </b>}{step.text}
                    </li>
                  ))}
                </ol>
              </div>
            ))}

            <div className="access">
              RELATED DECKS
              <b>{current.related_decks.length ? current.related_decks.join(', ') : 'Not yet placed on the general arrangement'}</b>
            </div>
          </article>
        )}
      </div>
    </section>
  );
}
