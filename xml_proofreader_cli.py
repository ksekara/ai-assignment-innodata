import argparse
import logging
import sys
import time
import tracemalloc
from pathlib import Path

from xml_proofreader.proofreader import Proofreader
from xml_proofreader.style_guide_loader import load_style_guide
from xml_proofreader.xml_handler import (
    extract_p_elements,
    get_inner_text,
    inject_errors,
    load_xml,
    write_xml,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Proofread <p> elements in XML files using GenAI",
    )
    parser.add_argument("input", help="Path to the input XML file")
    parser.add_argument(
        "--lang",
        default="en",
        help="BCP-47 language tag (default: en)",
    )
    parser.add_argument(
        "--style-guide",
        required=True,
        help="Path to the style guide document (.docx or .md)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (default: <input>.corrected.xml)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Start performance tracking
    tracemalloc.start()
    start_time = time.perf_counter()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.with_suffix(".corrected.xml"))

    logger.info(f"Input:  {args.input}")
    logger.info(f"Output: {output_path}")
    logger.info(f"Language: {args.lang}")
    logger.info(f"Model: {args.model}")

    # Load style guide
    logger.info(f"Loading style guide from: {args.style_guide}")
    style_guide = load_style_guide(args.style_guide)
    logger.info(f"Style guide loaded")

    # Parse XML
    logger.info("Parsing XML...")
    tree, raw = load_xml(args.input)

    # Extract <p> elements
    p_elements = extract_p_elements(tree)
    logger.info(f"Found {len(p_elements)} <p> elements")

    if not p_elements:
        logger.info("No <p> elements found. Writing output as-is.")
        write_xml(tree, output_path)
        return

    # Initialize proofreader
    proofreader = Proofreader(
        style_guide=style_guide,
        lang=args.lang,
        model=args.model,
    )

    # Proofread each <p> element
    total = len(p_elements)
    for i, p_elem in enumerate(p_elements, 1):
        original_text = get_inner_text(p_elem)
        if not original_text.strip():
            logger.debug(f"  [{i}/{total}] Empty paragraph, skipping")
            continue

        logger.info(f"  [{i}/{total}] Proofreading ({len(original_text)} chars)...")
        logger.debug(f"  Original: {original_text[:100]}...")

        p_start = time.perf_counter()
        annotated = proofreader.proofread(original_text)
        p_elapsed = time.perf_counter() - p_start

        logger.info(f"  [{i}/{total}] Done in {p_elapsed:.2f}s")

        if annotated != original_text:
            logger.info(f"  [{i}/{total}] errors found, injecting annotations")
            inject_errors(p_elem, annotated)
        else:
            logger.info(f"  [{i}/{total}] no errors found")

    # Write output
    write_xml(tree, output_path)

    # Performance summary
    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    logger.info("=" * 60)
    logger.info("PERFORMANCE SUMMARY")
    logger.info(f"  Total time:       {elapsed:.2f}s")
    logger.info(f"  Paragraphs:       {total}")
    logger.info(f"  Avg time/para:    {elapsed / total:.2f}s")
    logger.info(f"  Current memory:   {current / 1024 / 1024:.2f} MB")
    logger.info(f"  Peak memory:      {peak / 1024 / 1024:.2f} MB")
    logger.info(f"  Output written:   {output_path}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

