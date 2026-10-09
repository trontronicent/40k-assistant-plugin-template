# Changelog

## 1.2.0 — 2026-10-09

- The code shape every plugin keeps: `ruff.toml` and `tests/test_code_shape.py`, to copy into a new plugin on day
  one (app `docs/architecture/code-shape.md`).
- `tests/test_plugin_contents.py` — the manifest and content rules the app checks on install, checked locally in a
  second: known keys, description length, a CHANGELOG entry for the version, contributed paths confined to the
  plugin, no remote resources in a theme, no silently dropped persona keys, personas claiming only this plugin's
  Codex libraries, Codex documents with front matter and a title.
- README and HELP now state the install status plainly: app 3.12.0 installs only `backend` contributions, so this
  template is a manifest and content reference and is listed as blocked. It previously described the theme, persona
  and library as appearing in the app.

## 1.1.0 — 2026-10-04

- Help (`HELP.md`) and credits, shown in the app's manual under *Plugin Help*.
- Author: Reto Kummer alias Reat Kay.
- Needs the 40k Assistant 3.4.0.

## 1.0.0 — 2026-10-03

- First release: Ember Forge theme, Lexicanum Adept persona, Example Lore Codex library.
