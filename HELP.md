# Example STC

The reference plugin of the 40k Assistant: it shows what a plugin can add.

Made by **Reto Kummer alias Reat Kay**.

## What you get

- **Ember Forge** - a dark theme with forge-orange accents; pick it in the theme selector.
- **Lexicanum Adept** - a persona that answers from the *Example Lore* library.
- **Example Lore** - a small read-only Codex library with two documents.

## Using it

This app version installs only plugins that bring a **backend** module. A plugin
that contributes a theme, a persona or a Codex library — as this one does — is
listed in the STC Archive with the note that it cannot be installed yet, because
those adapters are not built. Nothing is missing on your side.

It is still the reference for anyone writing a plugin: the manifest, the theme,
the persona and the Codex documents here are the formats the app validates.

## Making your own plugin

Start from this template on GitHub (*Use this template*), change the manifest
(`strategicum-plugin.json`) and replace the example content. Your help file
(this file) and your credits appear in the app's manual under *Plugin Help*.
