# xraylib MCP Server

<!-- mcp-name: io.github.tschoonj/xraylib-mcp-server -->

[![CI](https://github.com/tschoonj/xraylib-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/tschoonj/xraylib-mcp-server/actions/workflows/ci.yml)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io%2Ftschoonj%2Fxraylib--mcp--server-blue)](https://github.com/tschoonj/xraylib-mcp-server/pkgs/container/xraylib-mcp-server)
[![PyPI](https://img.shields.io/pypi/v/xraylib-mcp-server)](https://pypi.org/project/xraylib-mcp-server/)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that provides access to [xraylib](https://github.com/tschoonj/xraylib) X-ray interaction data through a standardized interface. Query cross-sections, fluorescence lines, edge energies, and more from any MCP-compatible client.

## Features

This server exposes 101 tools organized into the following categories:

### Utility tools
- **AtomicNumberToSymbol** / **SymbolToAtomicNumber** -- convert between atomic numbers and element symbols
- **AtomicWeight** -- atomic weight (g/mol)
- **ElementDensity** -- element density (g/cm3)
- **ElectronConfig** -- electron configuration for a given shell
- **CompoundParser** -- parse chemical formulas (e.g. `SiO2`, `Ca5(PO4)3F`)
- **Atomic_Factors** -- atomic scattering factors f0, f', f''

### Line, edge, and shell properties
- **LineEnergy** / **EdgeEnergy** -- fluorescence line and absorption edge energies (keV)
- **FluorYield** / **JumpFactor** / **RadRate** -- fluorescence yields, jump factors, radiative rates
- **AtomicLevelWidth** -- natural widths of atomic levels (keV)

### Cross-sections (element)
- **CS_Total**, **CS_Photo**, **CS_Rayl**, **CS_Compt**, **CS_Energy**, **CS_KN** -- mass cross-sections (cm2/g)
- **CSb_Total**, **CSb_Photo**, **CSb_Rayl**, **CSb_Compt** -- atomic cross-sections (barn/atom)

### Fluorescence cross-sections
- **CS_FluorLine** / **CSb_FluorLine** -- line fluorescence cross-sections
- **CS_FluorShell** / **CSb_FluorShell** -- shell fluorescence cross-sections
- Kissel photoionization variants with full, radiative, nonradiative, and no cascade options

### Differential cross-sections
- **DCS_Rayl** / **DCS_Compt** and barn/atom variants -- unpolarized differential cross-sections
- **DCSP_Rayl** / **DCSP_Compt** and barn/atom variants -- polarized differential cross-sections

### Scattering factors
- **FF_Rayl** / **SF_Compt** -- Rayleigh form factor and Compton scattering function
- **MomentTransf** / **ComptonEnergy** -- momentum transfer and Compton-scattered photon energy
- **Fi** / **Fii** -- anomalous scattering factors
- **ComptonProfile** / **ComptonProfile_Partial** -- Compton profiles (total and per-shell)

### Auger and Coster-Kronig transitions
- **AugerRate** / **AugerYield** -- Auger transition rates and yields
- **CosKronTransProb** -- Coster-Kronig transition probabilities

### Compound cross-sections
- All CS/CSb, DCS/DCSb, and DCSP/DCSPb variants for compounds (by chemical formula)
- Kissel photoionization variants for compounds

### Refractive index
- **Refractive_Index_Re** / **Refractive_Index_Im** -- real and imaginary parts of the refractive index

### NIST compounds
- **GetCompoundDataNISTByName** / **GetCompoundDataNISTByIndex** / **GetCompoundDataNISTList** -- access the built-in NIST compound database

### Constant listings
- **ListLineConstants** / **ListShellConstants** / **ListTransitionConstants** / **ListAugerConstants** / **ListNISTCompoundConstants** -- enumerate valid constant names

## Installation

### Using uv (recommended)

```bash
uv tool install xraylib-mcp-server
```

### Using pip

```bash
pip install xraylib-mcp-server
```

## Usage

### As a standalone server

```bash
# Run with stdio transport (for Claude Desktop, etc.)
xraylib-mcp-server

# Run with HTTP transport
xraylib-mcp-server --transport http --port 8000

# Run with SSE transport
xraylib-mcp-server --transport sse --port 8000
```

### With Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "xraylib": {
      "command": "uvx",
      "args": ["xraylib-mcp-server"]
    }
  }
}
```

Or using the pre-built Docker image:

```json
{
  "mcpServers": {
    "xraylib": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "ghcr.io/tschoonj/xraylib-mcp-server:latest"]
    }
  }
}
```

### With VS Code

Add to your VS Code settings (`.vscode/settings.json` or user settings):

```json
{
  "mcp.servers": {
    "xraylib": {
      "command": "uvx",
      "args": ["xraylib-mcp-server"]
    }
  }
}
```

Or using the pre-built Docker image:

```json
{
  "mcp.servers": {
    "xraylib": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "ghcr.io/tschoonj/xraylib-mcp-server:latest"]
    }
  }
}
```

### With Claude Code

Add the server using the CLI:

```bash
claude mcp add xraylib -- uvx xraylib-mcp-server
```

Or using the pre-built Docker image:

```bash
claude mcp add xraylib -- docker run -i --rm ghcr.io/tschoonj/xraylib-mcp-server:latest
```

### As a development server

```bash
# Run in development mode with MCP inspector
uv run mcp dev src/xraylib_mcp_server/server.py
```

### Using Docker

#### Pre-built images from GitHub Container Registry

```bash
# Pull the latest image
docker pull ghcr.io/tschoonj/xraylib-mcp-server:latest

# Run with stdio transport
docker run -i --rm ghcr.io/tschoonj/xraylib-mcp-server:latest

# Run with HTTP transport on port 8000
docker run --rm -p 8000:8000 ghcr.io/tschoonj/xraylib-mcp-server:latest xraylib-mcp-server --transport http --port 8000

# Use a specific version
docker pull ghcr.io/tschoonj/xraylib-mcp-server:0.1.0
docker run -i --rm ghcr.io/tschoonj/xraylib-mcp-server:0.1.0
```

#### Local development with Docker

```bash
# Build the Docker image locally
docker build -t xraylib-mcp-server .

# Run with stdio transport
docker run -i --rm xraylib-mcp-server

# Run with HTTP transport on port 8000
docker run --rm -p 8000:8000 xraylib-mcp-server xraylib-mcp-server --transport http --port 8000
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/tschoonj/xraylib-mcp-server.git
cd xraylib-mcp-server

# Install development dependencies
uv sync --dev
```

### Running tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/xraylib_mcp_server --cov-report=html
```

### Code quality

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy src/ --ignore-missing-imports
```

## License

BSD 3-Clause License -- see [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request
