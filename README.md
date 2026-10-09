# Example STC — Strategicum plugin template

A plugin (**STC**) for the [40k Assistant / Strategicum](https://github.com/trontronicent/40k-assistant).
Install it from the app's **STC Archive** page once it is listed in the
[STC Index](https://github.com/trontronicent/40k-assistant-plugins).

## What it adds

| Kind | Item | Shown in the app as |
|---|---|---|
| Theme | Ember Forge | `example-stc--ember-forge` in the theme selector |
| Persona | Lexicanum Adept | a persona with an *STC* badge, answering from the Example Lore library |
| Codex | Example Lore (2 documents) | a read-only Codex library |

## What the app can install today (status, app 3.12.0)

**This template cannot be installed yet, by design of the app.** The app installs only `backend`
contributions (`INSTALLABLE_KINDS` in `src/plugins/compat.py`). Themes, personas and Codex libraries are
fully validated, but their adapters are not built, so a plugin contributing them is listed in the STC
Archive with a `blocked_reason` — *"contributes themes, personas, codex, which this app version cannot
install yet"* — instead of installing half-way.

So use this repository as the **reference for the manifest and the content formats**, and expect the table
above to describe what happens once those adapters ship. If you are writing a plugin to run today, it needs
`contributes.backend` with `app.plugin_api: 2`; the worked example is the
[No Man's Sky plugin](https://github.com/trontronicent/40k-assistant-nomanssky), and the app side is
documented in `docs/architecture/plugins.md`.

## Making your own plugin from this template

1. *Use this template* on GitHub, clone your new repository.
2. In `strategicum-plugin.json` change `id` (unique, lowercase, never reused),
   `name`, `description`, `author`, and list what you contribute. Remove the
   kinds you do not use, and their folders.
3. Validate — the tests first (they are the same rules, one second, no download):

   ```
   python -m pytest tests -q
   ```

   then the registry's own check:

   ```
   curl -fsSLO https://raw.githubusercontent.com/trontronicent/40k-assistant-plugins/main/tools/registry_tool.py
   python registry_tool.py manifest .
   ```

4. Release: set `version`, add its `## <version>` heading to `CHANGELOG.md`, commit, `git tag v<version>`,
   `git push --tags`. Never move a released tag — bump the version instead.
5. Submit it to the index (see the registry's CONTRIBUTING.md).

## Layout

```
strategicum-plugin.json         manifest (required)
HELP.md                         help shown in the app's manual (optional)
themes/<id>/theme.json          displayName, description, author, version, isMobileCompatible
themes/<id>/theme.css           :root custom properties only; nothing loaded from the internet
themes/<id>/preview.png         optional, 300x180
personas/<id>.json              persona fields (below)
codex/<Library>/**/*.md         Markdown; subfolders = categories; front matter title/category/tags
ruff.toml                       the code shape every plugin keeps (copy it unchanged)
tests/                          the checks below; `python -m pytest tests -q`
```

### Persona fields

`name` and `system_prompt` are required. Allowed besides: `appearance`,
`clothing`, `personality`, `speech_style`, `background`, `custom`,
`system_prompt_locked`, `model` (`""` = whatever model the user has selected —
recommended, since you cannot know which models a user has), `voice`,
`temperature`, `repeat_penalty`, `top_p`, `top_k`, `roleplay_helpers`,
`mnemo_vigil_threshold_hours`, `web_search_mode` (`off`/`tool`/`auto`),
`knowledge_mode` (`off`/`tool`/`auto`), `knowledge_top_k` (1–10),
`knowledge_all_libraries`, `create_memories`, `read_memories`, and
`knowledge_plugin_libraries` — names of Codex libraries **this plugin**
contributes; the app links them to the persona on install. Any other key is
dropped.

## Help and credits (app 3.4.0+)

`help` names a Markdown file in the plugin (here `HELP.md`, at most 100 KB) and
`credits` lists who made or contributed what (`[{name, for?, url?}]`, at most
30 entries, `https://` links only). The app shows both in its manual, in a
section of the *Plugin Help* chapter, with the plugin's version and author.
Your headings there become sub-headings of that section; images and HTML are
not shown.

## Code shape and tests

A plugin is held to the same code shape as the app: **complexity <= 12, <= 50 statements, <= 12 branches,
<= 8 returns and <= 6 parameters per function**, no unused names or arguments, no implicit `zip` length. The
full guide — why those limits exist and the patterns that keep functions under them (dispatch table, parameter
object, section builders, pure core) — is `docs/architecture/code-shape.md` in the app repository. `ruff.toml`
here applies it and `tests/test_code_shape.py` fails with the findings, so copy **both** into your plugin on day
one, before there is any code to clean up.

`tests/test_plugin_contents.py` checks this plugin's own files the way the app does when it reads a manifest:
known keys only, `description` <= 300 characters, a CHANGELOG entry for the manifest version, contributed paths
that stay inside the plugin, a theme that loads nothing from the internet, persona files whose keys are not
silently dropped, personas that only claim Codex libraries this manifest contributes, and Codex documents with
front matter and a title. Point them at your own manifest and they keep checking your plugin.

```
python -m pytest tests -q       # 15 checks, no app and no network needed
```

## License

MIT, see [LICENSE](LICENSE).
