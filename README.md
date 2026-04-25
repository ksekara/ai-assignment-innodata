# XML Proofreader

A production-grade CLI tool that uses GenAI (OpenAI) to proofread `<p>` elements in XML files, inject `<error>` annotations, and guarantee strict text-length invariants.

## Features

- **GenAI-powered proofreading** — detects grammar, spelling, punctuation, capitalization, clarity, and style guide violations
- **Error annotation injection** — wraps errors with `<error>` tags preserving the original text exactly
- **Length invariant** — text content (excluding `<error>` tags/attributes) matches the original character-for-character
- **XML preservation** — all namespaces, attributes, CDATA, and non-`<p>` elements are preserved unchanged
- **Locale-aware** — supports BCP-47 language tags via `--lang`
- **Style guide support** — accepts `.docx` or `.md` style guide files
- **Performance metrics** — logs runtime and memory usage summary

## Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- An OpenAI API key

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd ai_engineer_assignment_innodata

# Install dependencies with uv
uv sync

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
or create .env file and add
OPENAI_API_KEY="your-api-key-here"
```

## Usage

```bash
# Basic usage
uv run xml_proofreader input.xml --style-guide "Style Guide.docx"

# With language and model options
uv run xml_proofreader --style-guide "Style Guide.docx" --lang en --model gpt-4o

# With custom output path
uv run xml_proofreader --style-guide "Style Guide.docx" --output output.xml

# Verbose mode for debugging
uv run xml_proofreader input.xml --style-guide "Style Guide.docx" -v
```

### Arguments

| Argument | Required | Default                 | Description |
|---|---|-------------------------|---|
| `input` | Yes | —                       | Path to the input XML file |
| `--style-guide` | Yes | —                       | Path to style guide (.docx or .md) |
| `--lang` | No | `en`                    | BCP-47 language tag |
| `--model` | No | `gpt-4o-mini`           | OpenAI model name |
| `--output` | No | `<input>.corrected.xml` | Output file path |
| `-v, --verbose` | No | Off                     | Enable debug logging |

### Example

```bash
uv run xml_proofreader sample_input.xml --style-guide "Style Guide.docx"
```

This will produce `sample_input.corrected.xml` in the same directory.

## Output Format

Errors are annotated inline:

```xml
<p>The <error type="spelling" correction="committee">committe</error> met on
<error type="styleguide" correction="January 2024" reason="No comma between month and year">January, 2024</error>.</p>
```

### Error Types

| Type | Description |
|---|---|
| `grammar` | Subject-verb agreement, tense, etc. |
| `spelling` | Misspelled words |
| `punctuation` | Missing/incorrect punctuation |
| `capitalization` | Proper nouns, sentence starts, etc. |
| `clarity` | Awkward phrasing, wordiness |
| `styleguide` | Violations of the provided style guide |

## Project Structure

```
├── xml_proofreader/
│   ├── __init__.py
│   ├── proofreader.py         # GenAI proofreading logic
│   ├── style_guide_loader.py  # Style guide file loading
│   └── xml_handler.py         # XML parsing and manipulation
├── xml_proofreader_xml.py     # Cli entry point
├── pyproject.xml
├── style_guide.md
├── example_input.xml
├── example_output.xml
├── sample_input.xml
└── README.md
```
