import logging
from pathlib import Path
from docx import Document

logger = logging.getLogger(__name__)


def load_style_guide(path: str) -> str:
    """Load style guide content from a docx or markdown file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Style guide not found: {path}")

    suffix = p.suffix.lower()
    if suffix == ".docx":
        return _load_docx(p)
    elif suffix in (".md", ".markdown", ".txt"):
        return p.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported style guide format: {suffix}. Use .docx or .md")


def _load_docx(path: Path) -> str:
    """Extract text content from a docx file."""
    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)

