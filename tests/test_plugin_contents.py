"""What the app checks when it reads this plugin, checked here instead — before an install, not after.

The app validates the manifest in `src/plugins/manifest.py` and refuses the whole plugin with a list of problems.
Finding out that way means a release, an index pin and a reinstall per typo. These tests mirror those rules for the
files in this repository, so the same mistakes fail in one second locally.

They are deliberately about *this plugin's* content, not about the app: copy them with the template and keep them
pointed at your own manifest."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "strategicum-plugin.json"

# Keys the app keeps in a persona contributed as a .json file; anything else is dropped (see README,
# "Persona fields"). name and system_prompt are required.
PERSONA_KEYS = {
    "name", "system_prompt", "appearance", "clothing", "personality", "speech_style", "background", "custom",
    "system_prompt_locked", "model", "voice", "temperature", "repeat_penalty", "top_p", "top_k",
    "roleplay_helpers", "mnemo_vigil_threshold_hours", "web_search_mode", "knowledge_mode", "knowledge_top_k",
    "knowledge_all_libraries", "create_memories", "read_memories", "knowledge_plugin_libraries",
}
MANIFEST_KEYS = {"$schema", "manifest_version", "id", "name", "version", "description", "author", "license",
                 "app", "contributes", "help", "credits", "data_version"}
ALL_KINDS = ("themes", "personas", "codex", "backend")

# @import or a protocol-relative / absolute remote url() in a theme stylesheet: the app rejects both, because a
# theme must not load anything from the internet.
REMOTE_CSS_RE = re.compile(r"@import|url\(\s*['\"]?(?:https?:)?//", re.IGNORECASE)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


@pytest.fixture(scope="module")
def manifest() -> dict:
    """The parsed manifest, so a syntax error fails one test rather than every one."""
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))


def _contributed(manifest: dict, kind: str) -> list[dict]:
    """The entries of one contribution kind, or [] when the plugin does not contribute it."""
    return manifest.get("contributes", {}).get(kind) or []


# ── The manifest ─────────────────────────────────────────────────────────────

def test_the_manifest_is_valid_json_with_only_known_keys(manifest):
    """The manifest parses and carries no key the app does not know.

    Expected: every top-level key is in MANIFEST_KEYS. An unknown key is not ignored — the app lists it as a
    problem and refuses the plugin, so a typo like "contributions" blocks the whole install.
    """
    assert set(manifest) <= MANIFEST_KEYS, f"unknown keys: {sorted(set(manifest) - MANIFEST_KEYS)}"
    for key in ("manifest_version", "id", "name", "version", "description", "author", "license", "app",
                "contributes"):
        assert manifest.get(key), f"{key} is required"


def test_the_description_fits_the_app_limit(manifest):
    """`description` is at most 300 characters.

    Expected: within the limit. The app's plugin cards and the STC Index show it untruncated, and a longer one is
    a validation problem, not a cut-off string.
    """
    assert len(manifest["description"]) <= 300


def test_the_id_is_a_stable_lowercase_slug(manifest):
    """`id` is lowercase letters, digits and hyphens.

    Expected: matches the slug pattern. The id becomes part of every derived name the app stores (theme keys,
    persona ids), so it can never be renamed after a release.
    """
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]*", manifest["id"]), manifest["id"]


def test_the_version_is_a_three_part_number(manifest):
    """`version` is `MAJOR.MINOR.PATCH`.

    Expected: three numeric parts. The registry pins a tag `v<version>` and compares versions to offer updates;
    anything else sorts unpredictably.
    """
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]), manifest["version"]


def test_the_version_has_a_changelog_entry(manifest):
    """The manifest version appears as a heading in CHANGELOG.md.

    Expected: a `## <version>` line. Releasing without the entry is the mistake that makes an update show up in
    the app with nothing to say about what changed.
    """
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {manifest['version']}" in changelog


def test_every_contribution_kind_is_one_the_app_knows(manifest):
    """`contributes` is non-empty and names only known kinds.

    Expected: each key is in ALL_KINDS. An unknown kind is a validation problem; a plugin that contributes
    nothing is rejected outright.
    """
    contributes = manifest["contributes"]
    assert contributes, "contributes must not be empty"
    assert set(contributes) <= set(ALL_KINDS), f"unknown kinds: {sorted(set(contributes) - set(ALL_KINDS))}"


def test_the_help_file_exists_and_fits_the_size_limit(manifest):
    """The file named by `help` is present and at most 100 KB.

    Expected: readable and under the limit. It is rendered into the app's manual, and a missing file is a
    validation problem rather than a silently empty section.
    """
    if "help" not in manifest:
        pytest.skip("this plugin declares no help file")
    help_path = ROOT / manifest["help"]
    assert help_path.is_file(), help_path
    assert help_path.stat().st_size <= 100 * 1024


def test_the_credits_follow_the_app_rules(manifest):
    """Each credit has a name, an optional `for` and an `https://` URL only.

    Expected: at most 30 entries, names <= 80 chars, `for` <= 200, URLs https. The app drops an `http://` link
    rather than displaying it, so a plain-http URL silently loses the attribution.
    """
    credits = manifest.get("credits") or []
    assert len(credits) <= 30
    for entry in credits:
        assert set(entry) <= {"name", "for", "url"}, entry
        assert entry.get("name") and len(entry["name"]) <= 80
        assert len(entry.get("for", "")) <= 200
        if "url" in entry:
            assert entry["url"].startswith("https://"), entry["url"]


# ── The contributed files ────────────────────────────────────────────────────

def test_every_contributed_path_stays_inside_the_plugin(manifest):
    """No contributed path escapes the plugin folder or is absolute.

    Expected: each path resolves under the repository root. The app confines them the same way and refuses the
    plugin otherwise; this is the rule that keeps a manifest from reading `../../`.
    """
    for kind in ALL_KINDS:
        for item in _contributed(manifest, kind):
            path = item.get("path")
            if path is None:
                continue
            resolved = (ROOT / path).resolve()
            assert resolved.is_relative_to(ROOT.resolve()), f"{kind}: {path} leaves the plugin"


def test_each_theme_has_its_two_required_files_and_loads_nothing_remote(manifest):
    """Every theme folder holds theme.json and theme.css, and the CSS loads nothing from the internet.

    Expected: both files present, no `@import` and no remote `url(...)` outside comments. A theme that fetches a
    font or an image makes every app start depend on a third-party host.
    """
    for item in _contributed(manifest, "themes"):
        folder = ROOT / item["path"]
        assert (folder / "theme.json").is_file(), folder
        assert (folder / "theme.css").is_file(), folder
        css = CSS_COMMENT_RE.sub("", (folder / "theme.css").read_text(encoding="utf-8"))
        assert not REMOTE_CSS_RE.search(css), f"{folder}: theme.css loads a remote resource"
        meta = json.loads((folder / "theme.json").read_text(encoding="utf-8-sig"))
        assert meta.get("displayName"), folder


def test_each_persona_file_has_the_required_fields_and_no_dropped_keys(manifest):
    """Every persona .json has a non-empty name and system_prompt, and only documented keys.

    Expected: no key outside PERSONA_KEYS. An unknown key is dropped without a word — the usual cause of "my
    setting does nothing" — and a missing name or system_prompt is a validation problem.
    """
    for item in _contributed(manifest, "personas"):
        path = ROOT / item["path"]
        assert path.suffix == ".json" and path.is_file(), path
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        for key in ("name", "system_prompt"):
            assert isinstance(data.get(key), str) and data[key].strip(), f"{path}: {key} is required"
        assert set(data) <= PERSONA_KEYS, f"{path}: dropped keys {sorted(set(data) - PERSONA_KEYS)}"


def test_a_persona_only_claims_codex_libraries_this_plugin_contributes(manifest):
    """`knowledge_plugin_libraries` names libraries from this manifest's own codex contributions.

    Expected: every name matches a contributed library. The app links the persona to the plugin's libraries by
    name, so a typo leaves the persona with no sources at all.
    """
    libraries = {item.get("library") for item in _contributed(manifest, "codex")}
    for item in _contributed(manifest, "personas"):
        data = json.loads((ROOT / item["path"]).read_text(encoding="utf-8-sig"))
        for name in data.get("knowledge_plugin_libraries") or []:
            assert name in libraries, f"{item['path']}: no contributed library named {name!r}"


def test_each_codex_library_has_a_plain_name_and_documents(manifest):
    """Every Codex contribution names a library and points at a folder containing .md files.

    Expected: a plain library name and at least one document. An empty folder is a validation problem, and the
    app has no way to show an empty library.
    """
    for item in _contributed(manifest, "codex"):
        assert re.fullmatch(r"[\w][\w .-]*", item.get("library", "")), item
        folder = ROOT / item["path"]
        assert folder.is_dir(), folder
        assert list(folder.rglob("*.md")), f"{folder}: no .md documents"


def test_every_codex_document_starts_with_front_matter(manifest):
    """Each contributed document opens with a `---` front-matter block carrying a title.

    Expected: front matter with a title line. The app indexes the title and category from it; without them a
    document is searchable only by its body and shows up in the Codex with its filename.
    """
    for item in _contributed(manifest, "codex"):
        for doc in sorted((ROOT / item["path"]).rglob("*.md")):
            text = doc.read_text(encoding="utf-8")
            assert text.startswith("---"), f"{doc}: no front matter"
            end = text.find("\n---", 3)
            assert end > 0, f"{doc}: front matter is not closed"
            assert re.search(r"^title:\s*\S", text[:end], re.MULTILINE), f"{doc}: front matter has no title"
