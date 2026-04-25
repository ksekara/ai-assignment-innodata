"""XML parsing and manipulation utilities."""

import logging
from io import BytesIO
from pathlib import Path
from typing import List, Tuple

from lxml import etree

logger = logging.getLogger(__name__)


def load_xml(path: str) -> Tuple[etree._ElementTree, bytes]:
    """Load XML file preserving structure. Returns (tree, original_bytes)."""
    raw = Path(path).read_bytes()
    parser = etree.XMLParser(
        remove_blank_text=False,
        strip_cdata=False,
        resolve_entities=False,
    )
    tree = etree.parse(BytesIO(raw), parser)
    return tree, raw


def extract_p_elements(tree: etree._ElementTree) -> List[etree._Element]:
    """Extract all <p> elements in document order, including nested ones."""
    return list(tree.iter("p"))


def get_inner_text(elem: etree._Element) -> str:
    """Get the full inner text of an element (text + tail of children recursively)."""
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        parts.append(_get_all_text(child))
    return "".join(parts)


def _get_all_text(elem: etree._Element) -> str:
    """Get all text from element including its tail."""
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        parts.append(_get_all_text(child))
    if elem.tail:
        parts.append(elem.tail)
    return "".join(parts)


def inject_errors(p_elem: etree._Element, annotated_text: str) -> None:
    """Replace <p> element's content with annotated text containing <error> tags.

    The annotated_text is expected to contain <error> tags wrapping original text.
    """
    original_text = get_inner_text(p_elem)

    # Parse the annotated content
    try:
        wrapper = etree.fromstring(f"<p>{annotated_text}</p>")
    except etree.XMLSyntaxError as e:
        logger.warning(f"Failed to parse annotated text, skipping: {e}")
        return

    # Validate length invariant: text content excluding error tags must match original
    reconstructed = get_inner_text(wrapper)
    if reconstructed != original_text:
        logger.warning(
            f"Length invariant violated. Original ({len(original_text)} chars) vs "
            f"annotated ({len(reconstructed)} chars). Skipping this paragraph."
        )
        logger.debug(f"  Original:  {original_text!r}")
        logger.debug(f"  Reconstructed: {reconstructed!r}")
        return

    # Replace content of p_elem with annotated content
    p_elem.text = wrapper.text
    for child in list(p_elem):
        p_elem.remove(child)
    for child in wrapper:
        p_elem.append(child)


def serialize_xml(tree: etree._ElementTree) -> bytes:
    """Serialize the XML tree back to bytes, preserving declaration."""
    return etree.tostring(
        tree,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=False,
    )


def write_xml(tree: etree._ElementTree, output_path: str) -> None:
    """Write the XML tree to a file."""
    result = serialize_xml(tree)
    # Ensure the output matches the original formatting style
    Path(output_path).write_bytes(result)
    logger.info(f"Output written to: {output_path}")

