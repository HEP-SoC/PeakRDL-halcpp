# PeakRDL-halcpp Documentation

This website is built using [Docusaurus 3](https://docusaurus.io/) and served at
[hep-soc.github.io/PeakRDL-halcpp](https://hep-soc.github.io/PeakRDL-halcpp/).

The full documentation pipeline, driven by CMake, combines two API doc generators:

1. **sphinx-apidoc** — generates HTML API docs embedded as a Docusaurus static asset.
2. **pydoc-markdown** — generates Docusaurus-native Markdown pages under `docs/api/`.

---

## CMake Build Flow (recommended)

### Prerequisites

| Tool | Minimum version | Notes |
|---|---|---|
| CMake | 3.25 | |
| Python 3 | any | with `sphinx-apidoc` and `pydoc-markdown` available |
| Node.js | 18 | see [NVM](#nodejs-via-nvm) if not installed |
| npm | bundled with Node | |

#### Node.js via NVM

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22
```

### Configure

```bash
cmake -S docs -B build/docs
```

CMake reads the package version from `src/peakrdl_halcpp/__about__.py` automatically.

### Available targets

| Target | What it does |
|---|---|
| `api_doc` | Runs `sphinx-apidoc --full` then `make html` to build the Sphinx API docs. |
| `copy_sphinx_static` | Copies the Sphinx HTML output into `docs/static/api_sphinx/`. |
| `api_doc_md` | Runs `pydoc-markdown` to generate Markdown API pages in `docs/docs/api/`. |
| `docusaurus_doc` | Full build — depends on `api_doc_md` and `copy_sphinx_static`, then `npm run build`. Output lands in `build/docs/docusaurus/`. |
| `docusaurus_start` | Dev server — depends on `api_doc_md` and `copy_sphinx_static`, then `npm start`. |

### Full documentation build

```bash
cmake --build build/docs --target docusaurus_doc
```

The static site is written to `build/docs/docusaurus/`.

### Local development server

```bash
cmake --build build/docs --target docusaurus_start
```

Opens a live-reloading server at `http://localhost:3000`.

---

## Standalone npm workflow

Use these commands if you only need to work on the Docusaurus content and the API docs
are already generated (i.e. `docs/docs/api/` and `docs/static/api_sphinx/` are populated).

### Install dependencies

```bash
npm install
```

### Start dev server

```bash
npm start
```

### Build

```bash
npm run build
```

Static output goes to the `build/` directory inside `docs/`.

---

## Deployment

The site is deployed to GitHub Pages via CI. Manual deployment:

Using SSH:

```bash
USE_SSH=true npm run deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> npm run deploy
```
