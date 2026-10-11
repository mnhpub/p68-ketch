# Gap closure process

The gap register is `layout/gap-closure.json`. Each gap has a checklist of steps. A step is either automated or manual.

## How a gap closes

- **Automated steps** are tested by `scripts/validate-gap-closure.mjs` against the repository. A step passes when the file or check it names is in the state the step requires. Example: the weight register covers at least 95% of 1,487 t.
- **Manual steps** are closed by a person who has done the work. They are closed by setting `"done": true` and naming the evidence in `"evidence"`. The evidence is a path in the repository, such as a drawing, a schedule or a report, or a commit reference.
- A **gap is closed** when every step in its checklist is done. Otherwise it is open.

## Running the check

    npm run validate:gaps

The check prints each gap, its step count and its status, and lists the steps still open. It exits with code 1 only if a check cannot run. An open gap does not fail the run.

## Closing a manual step

1. Add the evidence to the repository (drawing, schedule, report).
2. Edit the step in `layout/gap-closure.json`: set `"done": true` and `"evidence": "<path or commit>"`.
3. Run `npm run validate:gaps` and confirm the count changed.
4. Note the change in the pull request.

Do not set `"done": true` without evidence in the repository. The evidence field is the record.

## Adding a gap

Add an entry with `id`, `severity`, `title`, `source`, `owner` and a `checklist`. Use the next free ID. If the gap comes from the 68 m list, keep the old ID in `source`. If an automated step needs a new check, add the function to `checks` in the validator and name it in the step.

## Rules

- Do not remove a gap to make the count look better. Close it, or mark it with a clear reason.
- A gap closed by an automated check should stay closed only while the check passes. If the file changes and the check fails, the gap reopens.
