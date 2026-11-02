# Evidence-linked acceptance

Prefer the host project's current work logs and tests. If traceability is missing, use the offline manifest CLI at this repo's root:

```
python src/flow_parity.py init --out flow.json --name "My application"
python src/flow_parity.py validate flow.json
python src/flow_parity.py cases flow.json
python src/flow_parity.py report flow.json --json
python src/flow_parity.py gate flow.json
```

`init` creates an incomplete draft intentionally. `validate` checks JSON structure and trace references. `cases` writes suggested case ideas **to stdout**, not runnable E2E tests. `report` summarizes recorded verification. `gate` checks written approvals, must-haves and tests; it is NOT an independent security, legal or functional assessment. A synthetic fixture can produce a passing recorded gate without a real app — never equate that with verified production readiness.

Test the local implementation: positive/negative outcomes, empty/invalid/long/Unicode inputs, duplicate submits, connectivity interruptions, restricted data, preservation after restart, supported OS/viewport, accessible roles and labels. Only mark N/A after reasoned evaluation.

Issue priority: S1=data loss/security/core safety; S2=core user flow without workaround; S3=workaround exists; S4=cosmetic. Never invent a bug. Note steps and evidence for observed defects. Deployment requires independent project approvals and explicitly granted publication permission.
