# Profile badges

Static SVGs generated with [Shields.io](https://shields.io/) on 2026-10-23.
Technology logos are provided by [Simple Icons](https://simpleicons.org/) through
Shields' `logo` parameter. Simple Icons is CC0; brand trademarks remain their
owners' property. Shields is Apache-2.0. These badges describe technologies I use,
not endorsements or certifications.

The images are stored in this repository so profile rendering does not depend on
live requests to the Shields service. The generated SVG includes the logo data.
LinkedIn uses text only; no substitute or unofficial icon is embedded.

## Regeneration

Request `https://img.shields.io/badge/LABEL-25292E` with the query parameters
`style=flat-square`, `logoColor=white` and the logo slug below. URL-encode spaces in
labels. Download the response as the matching file in `badges/`; verify it is SVG
and inspect it before committing. No token or personal data is needed.

| File | Label | Simple Icons slug |
| --- | --- | --- |
| php.svg | PHP | php |
| symfony.svg | Symfony | symfony |
| go.svg | Go | go |
| typescript.svg | TypeScript | typescript |
| react.svg | React | react |
| postgresql.svg | PostgreSQL | postgresql |
| redis.svg | Redis | redis |
| rabbitmq.svg | RabbitMQ | rabbitmq |
| docker.svg | Docker | docker |
| github-actions.svg | GitHub Actions | githubactions |
| linkedin.svg | LinkedIn | none |
| projects.svg | All projects | github |

Shields controls its deployed Simple Icons version. The committed SVG bytes are
our reproducible rendering snapshot, not a claim that the service pins an
upstream icon revision. Review regenerated badges as asset changes.
