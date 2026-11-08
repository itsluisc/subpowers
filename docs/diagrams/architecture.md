# How subpowers fits together

GitHub renders this diagram. The source is the `mermaid` block below; edit it when a piece changes.

```mermaid
flowchart LR
  A[Your agent or terminal] --> F["bin/subpowers<br/>(front door)"]
  F -->|--refs NAME| R[("~/.subpowers/refs")]
  F -->|auto: first connected, then next| P{Pick painter}
  F -->|council| ALL[All connected painters in parallel]
  P --> C[bin/chatgpt-image]
  P --> G[bin/antigravity-image]
  P --> K[bin/grok-image]
  ALL --> C & G & K
  C -->|codex exec, API keys stripped| CX[codex CLI<br/>ChatGPT plan]
  G -->|agy, sandbox + empty profile| AG[agy CLI<br/>Google AI plan]
  K -->|grok, API-key auth off| GK[grok CLI<br/>SuperGrok plan]
  CX & AG & GK --> I[bin/imgops<br/>resize, crop, convert]
  I --> O[out.png + out.prompt.txt receipt]
  O --> L[("~/.subpowers/library.jsonl")]
  L -.-> H[hooks/after-image<br/>optional backup]
  ALL --> S[side-by-side sheet<br/>needs Pillow]
  D[bin/doctor] -.checks.-> CX & AG & GK
  U[bin/update-codex<br/>daily, opt out] -.-> CX
```

- **Solid arrows** run on every image. **Dotted arrows** are health checks and optional extras.
- A painter that fails in `auto` mode hands off to the next connected one. Exit 5 (painted but not delivered) never repaints, because the plan already paid for it.
- No path ever uses an API key. Each painter removes the provider's key variables before calling its CLI.
