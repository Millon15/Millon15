# Profile card generation

The profile README uses one GitHub Profile Summary Cards image in two themes:
`profile-summary-card-output/default/0-profile-details.svg` and
`profile-summary-card-output/github_dark/0-profile-details.svg`. The paths are
generated, committed assets, not placeholders or remote image hotlinks.

`.github/workflows/profile-cards.yml` runs daily, on manual dispatch, and when
its workflow or selector script changes on `main`. Changes to generated cards,
README or documentation do not trigger a push run, avoiding commit loops. Its
generation job gives the upstream action a read-only built-in `GITHUB_TOKEN` and
checks out without persisted credentials. A separate publish job has
`contents: write` only to commit changed images to this repository. No personal
access token or custom secret is needed. The upstream action has `AUTO_PUSH`
set to `false`; the local workflow owns its small, conditional commit and push.
The action generates all themes. `scripts/select-profile-cards.py` validates
the two required 700-pixel SVGs,
rejects executable/external SVG content, and retains only those images. It also
removes the upstream card's optional fourth metadata row (email, company or
location, including its icon). This is presentation-only: contribution counts,
public repository count and chart stay intact. It validates the pinned row
structure and fails closed if that structure changes, preventing a stale
location or future public contact field from being published automatically.
Missing or incomplete cards fail the job before commit.

## Pinned source and audit

- Summary Cards: `vn7n24fzkq/github-profile-summary-cards` release commit
  `58ec032e39377dd38329bdc1db70074fe74fbb17` (v0.12.1, 2026-10-19).
  `action.yml` runs bundled `dist/index.js` on Node 24. Its `src/app.ts` reads
  `GITHUB_TOKEN`, deletes its own relative output directory, calls GitHub API,
  generates cards, and only calls git commit/push when `AUTO_PUSH` is true.
  `src/utils/request.ts` targets `api.github.com`; analytics requires Vercel
  variables that this workflow does not provide. The release tree contains the
  bundle; no npm install is performed in this repository.
- Checkout: `actions/checkout` v4 tag commit
  `11d5960a326750d5838078e36cf38b85af677262`. Artifact transfer:
  `actions/upload-artifact` v4 tag commit
  `ea165f8d65b6e75b540449e92b4886f43607fa02` and
  `actions/download-artifact` v4 tag commit
  `d3f86a106a0bac45b974a628896c90dbdf5c8093`.
- All actions use fixed full commits, not moving tags. Review upstream changes before
  updating any SHA. The Summary Cards source review is not a runtime success
  claim; the first successful Actions run and resulting committed images are
  the generation proof.

The card queries GitHub's public-facing profile and contribution counts using
this public repository's token. It has no private-repository read scopes. The
optional public profile location/contact row is omitted from the published SVG.
GitHub may include anonymized private contribution totals already visible on a
public profile; no private repository details are queried or shown.

## Verification

A push to `main` changing the workflow or selector script starts the first run.
It can also be launched with `workflow_dispatch` in GitHub Actions. Inspect a
successful run and its committed images, then run:

```sh
python3 scripts/select-profile-cards.py --check-only
```

The verifier requires both themes, valid SVG, expected card text and no other
generated files. A workflow execution failure or missing assets is a blocker,
not a successful generation.
