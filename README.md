<div align="center">

<img src="./cover.png" alt="shadcn-htmx — shadcn-style components for htmx v4 + Tailwind v4" width="100%">

# shadcn-htmx

**shadcn-style UI components for [htmx v4](https://htmx.org) + [Tailwind CSS v4](https://tailwindcss.com) — built on web standards, not hacks.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
![Components: 82](https://img.shields.io/badge/components-82-8b5cf6)
![Flavours: 6](https://img.shields.io/badge/flavours-6-1f2937)
![htmx v4](https://img.shields.io/badge/htmx-v4-3366cc)
![Tailwind CSS v4](https://img.shields.io/badge/Tailwind%20CSS-v4-38bdf8)
![a11y: WAI-ARIA APG](https://img.shields.io/badge/a11y-WAI--ARIA%20APG-22c55e)

### [📖 Documentation & live previews → shadcn-htmx.productdevbook.com](https://shadcn-htmx.productdevbook.com)

One design. **82 components.** Six backends — **Hono JSX, Jinja2, Go templates, Phoenix, Django-Cotton, and raw HTML** — generated from a single source of truth. Copy what you need, ship it in any stack.

</div>

---

## Why

Most component libraries assume React. shadcn-htmx assumes the **platform**: a real
`<button>`, a real `<dialog>`, real `aria-*`, real `<input type="date">`. Behaviour
the browser already ships is never re-implemented in JavaScript — the only script is
a tiny, shared keyboard layer for the composite ARIA widgets the platform *doesn't*
cover (menus, listboxes, trees…).

- **Web standards first.** Every component is justified against the WAI-ARIA APG, MDN, the htmx v4 source, and the Tailwind v4 source before it ships. No polyfills, no emulation, no "browsers will support this eventually."
- **Six flavours, one design.** Each component exists as a typed Hono JSX component, a Jinja2 macro, a Go `html/template`, a Phoenix function component, Django-Cotton templates, and a copy-paste HTML snippet — all rendering identical, accessible markup.
- **Server-rendered + htmx-native.** Components are built for server rendering and wired for the htmx v4 attribute set (live search, infinite scroll, inline edit, optimistic toggles…).
- **Accessible by construction.** Keyboard interaction, focus management, and ARIA roles are checked against the spec — and against an axe-core + APG keyboard test suite.
- **Your code, your repo.** Copy a component in and it's yours. No runtime dependency, no version lock-in.

## Flavours

| Flavour      | Language / engine          | What you copy                     |
| ------------ | -------------------------- | --------------------------------- |
| **Hono JSX** | TypeScript (`.tsx`)        | A typed component you import      |
| **Jinja2**   | Python templates (`.html`) | A `{% macro %}` you call          |
| **Go**       | `html/template` (`.tmpl`)  | A `{{ define }}` template         |
| **Phoenix**  | Elixir (`.ex`)             | A `~H` function component         |
| **Django-Cotton** | Django templates (`.html`) | `<c-button>` tags and slots |
| **HTML**     | Raw markup (`.html`)       | A copy-paste snippet              |

The Hono JSX file is the canonical source; the other five mirror its semantics exactly — same elements, roles, ARIA, and Tailwind classes. Only the templating syntax differs.

## Quick start

The fastest path is the **flavour-aware CLI**. Pick your stack once, then add components — only *your* framework's file lands in your project.

```sh
npx shadcn-htmx init --flavour jinja        # jsx | jinja | go | phoenix | cotton | html
npx shadcn-htmx add button dialog combobox  # writes only the Jinja2 files
npx shadcn-htmx list                         # browse every component
```

`init` writes a `shadcn-htmx.json` so later commands need no flags — it's
pre-pointed at the hosted registry (`https://shadcn-htmx.productdevbook.com/r`);
override it with the `registry` field or `--registry` to self-host.

<details>
<summary><b>Other ways to install</b></summary>

**shadcn CLI** — the registry follows the shadcn `registry-item` schema, so the
stock CLI works too (but it copies *all six* flavours' files; delete the ones you
don't need):

```sh
npx shadcn@latest add https://shadcn-htmx.productdevbook.com/r/button.json
```

**curl** — pull a raw flavour file straight into your project:

```sh
curl -o templates/components/button.html \
  https://raw.githubusercontent.com/productdevbook/shadcn-htmx/main/registry/jinja2/button.html
```

**Copy-paste** — open the component's docs page, switch the framework selector to
your stack, and copy the source.

</details>

## Django-Cotton

Requires Django 4.2+ and Django-Cotton 2.9+.
Install [Django-Cotton](https://django-cotton.com/docs/quickstart) and select the
`cotton` flavour from your Django project root (beside `manage.py`):

```sh
python -m pip install "django-cotton>=2.9,<3"
npx shadcn-htmx init --flavour cotton
npx shadcn-htmx add button card dialog
```

Add `"django_cotton"` to `INSTALLED_APPS`. In your existing **DjangoTemplates**
backend, include `BASE_DIR / "templates"` in `DIRS` and keep `APP_DIRS = True`.
Cotton configures its loader automatically; projects with custom loaders should
follow its [manual configuration](https://django-cotton.com/docs/quickstart).
Django-Cotton uses Django's template engine, not Jinja2.

The installer writes each family to `templates/cotton/<name>/`. Cotton's default
filename convention uses underscores (`radio_group/`); call sites use kebab case
(`<c-radio-group>`). Compound components install together:

```html
<c-card>
  <c-card.header>
    <c-card.title as="h2">Account</c-card.title>
    <c-card.description>Update your settings.</c-card.description>
  </c-card.header>
  <c-card.content>
    <c-button variant="outline" hx-post="/save/" hx-target="#result">
      Save {{ user.first_name }}
    </c-button>
  </c-card.content>
</c-card>
<div id="result"></div>
```

Use `class` for additional classes, literal HTML names for `hx-*`, `aria-*`, and
`data-*`, and `:prop="context_variable"` for dynamic values. Bare boolean props
are true; use `:disabled="False"` to pass false. Text is escaped by Django;
put rich markup in the default body or a named `<c-slot>`, rather than marking
untrusted strings safe. See [Cotton's component API](https://django-cotton.com/docs/components).

Progress, range slider, splitter, file upload, rating, and highlight also install
`shadcn_htmx.py` beside `manage.py`. It contains server-side numeric and search
helpers. After adding one of these components, register the module in your
existing DjangoTemplates backend (preserve your other options):

```python
TEMPLATES[0]["OPTIONS"].setdefault("libraries", {})["shadcn_htmx"] = "shadcn_htmx"
```

If you install under an app with `--out myapp`, use the import path
`"myapp.shadcn_htmx"` instead. Restart Django after registering the library.
This is Django's standard [template library registration](https://docs.djangoproject.com/en/5.2/howto/custom-template-tags/#code-layout);
no additional Python package or client runtime is required by the helper.

As with the other flavours, include the shared theme CSS, htmx v4, and
`public/site.js` for components with behavior hooks. Copy these to your Django
static directory and load them using `{% static %}`. In a custom Tailwind v4
stylesheet, include the library theme tokens and scan the installed templates,
e.g. `@source "../../templates/**/*.html";` (relative to your stylesheet).
For unsafe requests, send Django's CSRF header from a base template:

```html
{% load static %}
<body hx-headers:inherited='{"X-CSRFToken": "{{ csrf_token }}"}'>
  <!-- page content -->
  <script src="{% static 'htmx.min.js' %}" defer></script>
  <script src="{% static 'site.js' %}" defer></script>
</body>
```

Use `{% csrf_token %}` inside ordinary POST forms as well. The explicit
`:inherited` modifier follows htmx v4's attribute rules
([vendored guidance](repos/htmx/src/skills/htmx-guidance.md)). Native buttons and
dialog commands retain the contracts in the
[APG button pattern](repos/aria-practices/content/patterns/button/button-pattern.html)
and [MDN button reference](repos/mdn/files/en-us/web/html/reference/elements/button/index.md).

To try these changes before a CLI/registry release, use this checkout directly:

```sh
bun run build:registry
node scripts/cli.mjs init --flavour cotton --cwd /path/to/django-project --registry "$PWD/public/r"
node scripts/cli.mjs add button card dialog --cwd /path/to/django-project
```

## Components

**82 components** across six categories — every interactive one mapped to its
WAI-ARIA APG pattern, every other to a native HTML element, Web API, or modern CSS
feature.

| Category       | Components |
| -------------- | ---------- |
| **Forms**      | Button · Input · Textarea · Label · Checkbox · Combobox · Switch · Radio Group · Select · Slider · Number Input · Range Slider · Listbox · Form Field · File Upload · Date Time Picker · Active Search · Edit In Place · Output · Segmented Control · Rating · Color Picker · Autosize Textarea · Cascading Select · Autocomplete |
| **Layout**     | Card · Table · Collapsible · Toolbar · Grid · Treegrid · Splitter · Landmarks · Aspect Ratio · Auto Grid · Scroll Area · Snap List · Container Card · Sticky Header · Exclusive Accordion |
| **Display**    | Avatar · Badge · Separator · Carousel · Copy Button · Kbd · Highlight · Relative Time · Figure · Responsive Image · Media Player · Selectable Table · Delete Row |
| **Feedback**   | Alert · Progress · Skeleton · Toast · Meter · Feed · Status · Lazy Load · Optimistic Toggle · Scroll Progress |
| **Overlays**   | Dialog · Dropdown Menu · Popover · Tooltip · Alert Dialog · Sheet · Hover Card |
| **Navigation** | Accordion · Pagination · Tabs · Breadcrumb · Link · Menubar · Tree · Skip Link · Theme Toggle · Split Button · Sidebar · Load More |

## Accessibility

Interactive components implement the matching [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
pattern — keyboard interaction, focus management, and ARIA roles checked against the
spec. The repo ships a Playwright suite that enforces it: axe-core on every page,
APG keyboard contracts, overlay geometry, an interaction smoke sweep, and a
console-error sweep.

## How it works

`registry.json` is the manifest — one entry per component, listing files for all six
flavours. `scripts/build-registry.ts` reads it and emits `public/r/<name>.json` (the
shadcn `registry-item` schema, with each file's contents inlined) plus an
`index.json`. The docs app serves `/r/*`, so the CLI — or any HTTP consumer — pulls
items straight over the wire. The `shadcn-htmx` CLI reads that same JSON and writes
only the file for your chosen flavour.

## Local development

The repository **is** the docs site — a [Hono](https://hono.dev) + JSX app rendered
on [Bun](https://bun.sh).

```sh
bun install
bun dev                  # docs at http://localhost:3000 (server + Tailwind watcher)
```

```sh
bun run typecheck        # tsc --noEmit
bun run build            # build:registry (public/r/*.json) + build:css (minified)
bun run build:registry   # regenerate the registry JSON from registry.json
bun run build:css        # compile app/styles/input.css -> public/styles.css
```

### Tests

Cotton templates are tested with the real Django template engine and Cotton loader:

```sh
python -m pip install -r tests/cotton/requirements.txt
python -m unittest discover -s tests/cotton -v
bun run test:cli
```


End-to-end tests run on Playwright (Chromium). The config does **not** start the
server — run the app on port **3010** in one terminal and the tests in another:

```sh
PORT=3010 bun run app/server.tsx     # terminal 1
bun run test:e2e                     # terminal 2 — all browser suites
bun run test:a11y                    # axe-core accessibility checks
bun run test:kbd                     # APG keyboard contracts
bun run test:geom                    # overlay positioning
bun run test:cli                     # the flavour-aware CLI (bun test)
```

## Project structure

```
registry/
  ui/            *.tsx     Hono JSX — canonical source of truth
  jinja2/        *.html    Jinja2 macros
  go-templates/  *.tmpl    Go html/template
  phoenix/       *.ex      Phoenix function components
  django-cotton/ */*.html Django-Cotton components and a Python template helper
  html/          *.html    raw HTML snippets
  lib/           cn.ts     class-name joiner
app/             Hono docs site (routes, layout, shared components, demo endpoints)
tests/           Playwright e2e (a11y, keyboard, geometry, smoke, console)
scripts/         build-registry.ts · cli.mjs (the shadcn-htmx CLI) · sync-repos.sh
public/r/        generated registry JSON (served at /r/*)
repos/           vendored upstream sources, read-only — see AGENTS.md
```

## Philosophy

This project ships only what the web platform supports natively today. The sources
it's measured against — the WAI-ARIA APG, MDN, the htmx v4 source, and the Tailwind
v4 source — are vendored under `repos/` so contributors (human or agent) read
current ground truth instead of recalling from memory. The full rules live in
[`AGENTS.md`](./AGENTS.md). Vendored sources are refreshed with `./scripts/sync-repos.sh`.

## Contributing & sponsoring

Issues and PRs are welcome. If shadcn-htmx saves you time, you can sponsor ongoing
maintenance and new components at
**[github.com/sponsors/productdevbook](https://github.com/sponsors/productdevbook)**.

## License

[MIT](./LICENSE) © [productdevbook](https://github.com/productdevbook)
