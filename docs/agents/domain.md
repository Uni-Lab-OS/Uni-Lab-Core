# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- `CONTEXT.md` at the repo root.
- `CONTEXT-MAP.md` instead, if it exists; read every mapped context relevant to the work.
- ADRs under `docs/adr/` that affect the area being changed.
- The Feishu OKF root and relevant stage documents described below.

If local domain files do not exist, proceed silently. The domain-modeling workflow creates them lazily when terminology or decisions are resolved.

## Feishu OKF knowledge source

The authoritative external knowledge entry is the Feishu wiki page “敏捷开发文档规范”:

- Root node: `AaokwPX7viwZpTk52Vxcnw6jnCh`
- Space: `7498240950477668371`
- Collaboration guide: `IDO1wrptGiPZl3k6GnDcbqy5nMg`
- Protocol index: `DzjFwDOoBijr25khEoTcFxBdnfb`
- Implementation index: `TcvWwOFeYiAzQsk425PcDAgCnqb`
- Testing index: `DM4cwsJLoisGhBkxS6XcPx2jnac`
- Development standards: `YZPPwcge6ipaPukG542ctbqXnZb`

Read the collaboration guide first, then the relevant protocol, implementation, testing, or development-standard page. Use `lark-cli` with user identity for interactive exploration:

```bash
lark-cli wiki +node-get --as user --node-token "AaokwPX7viwZpTk52Vxcnw6jnCh"
lark-cli wiki +node-list --as user --space-id "7498240950477668371" --parent-node-token "AaokwPX7viwZpTk52Vxcnw6jnCh" --page-all
lark-cli docs +fetch --as user --doc "IDO1wrptGiPZl3k6GnDcbqy5nMg"
```

GitHub remains authoritative for work state. Feishu remains authoritative for the current protocol, implementation mapping, test evidence, and development standards.

If local ADRs or context documents conflict with Feishu, surface the conflict with both revision or commit references. Do not silently choose one or overwrite either source.

## File structure

This repository uses the single-context layout:

```text
/
├── CONTEXT.md
├── docs/adr/
└── src/
```

`CONTEXT.md` and `docs/adr/` are created only when the domain-modeling workflow has resolved content worth recording.

## Use the glossary's vocabulary

When output names a domain concept in an Issue title, refactor proposal, hypothesis, or test, use the term defined in `CONTEXT.md` and the relevant Feishu protocol. Do not drift to synonyms that either source explicitly avoids.

If the required concept is absent, reconsider whether the term is being invented or record the gap for domain modeling.

## Flag ADR conflicts

If output contradicts an existing ADR, surface it explicitly rather than silently overriding it:

> Contradicts ADR-0007 — but worth reopening because…
