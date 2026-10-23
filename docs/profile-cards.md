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
The action displays the full `Vitautas Brazas` title instead of truncating the
longer login-plus-name default. It generates all themes without animation (its
default). The jobs run on the fixed GitHub-hosted `ubuntu-24.04` image, avoiding
`ubuntu-latest` image migrations. `scripts/select-profile-cards.py` validates
the two required 700-pixel SVGs, rejects executable/external SVG content, and
retains only those images. It also removes the upstream card's optional fourth
metadata row (email, company or
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
- Checkout: `actions/checkout` v7.0.1 commit
  `3d3c42e5aac5ba805825da76410c181273ba90b1`. Artifact transfer:
  `actions/upload-artifact` v7.0.2 commit
  `cf430e030ddbb5b0abf93d22962f4752f3646cd9` and
  `actions/download-artifact` v8.0.2 commit
  `9000827ccba6bdab643e8b6fd33ac0654aef8333`. Their action manifests
  specify Node 24. Checkout and artifact actions require a recent runner
  (at least 2.327.1); this workflow uses GitHub-hosted runners. Upload keeps
  its default archive mode for the two SVGs; download v8 fails on an artifact
  digest mismatch. The source-to-publish artifact contract remains the same.
- All actions use fixed full commits, not moving tags. Review upstream changes
  before updating any SHA. Source review alone is not a runtime success claim;
  each changed workflow needs a successful run and verified published images.

The card queries GitHub's public-facing profile and contribution counts using
this public repository's token. It has no private-repository read scopes. The
optional public profile location/contact row is omitted from the published SVG.
GitHub may include anonymized private contribution totals already visible on a
public profile; no private repository details are queried or shown. The displayed
public-repository count excludes forks, as the upstream query specifies.

## Verification

A push to `main` changing the workflow or selector script starts a run.
It can also be launched with `workflow_dispatch` in GitHub Actions. Inspect a
successful run and its committed images, then run:

```sh
python3 scripts/select-profile-cards.py --check-only
```

The verifier requires both themes, valid SVG, expected card text and no other
generated files. A workflow execution failure or missing assets is a blocker,
not a successful generation.
