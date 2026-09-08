# Field terminal / maintenance

The profile is a native GitHub README with custom SVG artwork, progressive disclosure, and a public-data instrument. All essential content is readable as Markdown without images. The single-column layout avoids fixed-width tables on phones. GitHub-compatible picture elements select compact SVG compositions below 600px.

## Update

- Edit `README.md` for copy. Keep private projects at the high level approved by their owner.
- Edit `scripts/render.py` for artwork. Run `python scripts/render.py --cached` to rebuild assets from the existing public snapshot.
- Run `python scripts/render.py` for a fresh public GitHub snapshot. No dependencies or token are required.
- Run `python -m unittest discover -s tests` to verify data boundaries and generation.
- The daily **Refresh public signal** workflow also supports manual dispatch. It commits only the snapshot and SVG assets, and skips empty commits.

## Data contract

The signal shows twelve Monday-based UTC weeks, including the current partial week. Counts cover commits on the default branch of the explicitly selected public repository, across all authors. They are not personal contribution counts. GitHub's commit API applies its own history/date semantics; this is a repository activity view, not an audit log.

Only `NyKurr/NyKurEdge` is queried. Requests deliberately omit authentication. A repository must explicitly report `private: false` before its commits are read. Only aggregate weekly counts and the UTC snapshot date are persisted. No commit messages, identities, private repository names, or credentials are published. Pagination is bounded and fails rather than silently truncating.

Fetch and validation finish before any generated files are written. A failed API request fails the workflow and leaves the last committed snapshot intact. The SVG visibly states its snapshot date; it does not imply real-time freshness. GitHub Actions schedules can be delayed or disabled for inactivity; use manual dispatch to recover.

## Visual system

- Background `#080e0c`, panel `#0d1712`, primary text `#edf7ef`.
- Signal green `#a3ff70`, secondary green `#51c987`, muted text `#9bac9f`.
- Topographic paths are original procedural artwork, not measured data. Only the signal histogram encodes activity.
- Slow decorative motion respects `prefers-reduced-motion`; all artwork is complete in its static state.
- SVGs contain no scripts, external fonts, remote images, or `foreignObject`.

## Editorial sources

Profile copy was grounded in the public NyKurEdge README and architecture/status documentation, public account activity, and the owner's supplied description of their work. Nyxterra is mentioned only as game-development work. No private code or infrastructure was used in public assets.
