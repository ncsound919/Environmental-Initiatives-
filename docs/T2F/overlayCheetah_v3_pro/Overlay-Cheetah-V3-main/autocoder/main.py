#!/usr/bin/env python3
"""
Overlay Cheetah V3 - Advanced Autocoder Tool
Main entry point for the autocoder CLI
"""

import argparse
import sys
from pathlib import Path
from .core.engine import AutocoderEngine
from .core.config import Config
from .utils.logger import setup_logger

__version__ = "3.0.0"


def main():
    """Main entry point for the Overlay Cheetah autocoder"""
    parser = argparse.ArgumentParser(
        description="Overlay Cheetah V3 - Advanced AI-Powered Autocoder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate --input prompt.txt --output output.py
  %(prog)s analyze --file code.py
  %(prog)s refactor --file code.py --style pep8
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"Overlay Cheetah V3 {__version__}"
    )

    parser.add_argument(
        "--config", type=str, help="Path to configuration file", default="config.yaml"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate code from prompts"
    )
    generate_parser.add_argument("--input", required=True, help="Input prompt file")
    generate_parser.add_argument("--output", required=True, help="Output code file")
    generate_parser.add_argument("--language", default="python", help="Target language")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze existing code")
    analyze_parser.add_argument("--file", required=True, help="File to analyze")
    analyze_parser.add_argument("--report", help="Output report file")

    # Refactor command
    refactor_parser = subparsers.add_parser("refactor", help="Refactor existing code")
    refactor_parser.add_argument("--file", required=True, help="File to refactor")
    refactor_parser.add_argument(
        "--style", default="default", help="Coding style guide"
    )
    refactor_parser.add_argument(
        "--output", help="Output file (default: overwrite input)"
    )

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Auto-complete code")
    complete_parser.add_argument("--file", required=True, help="File to complete")
    complete_parser.add_argument("--context", help="Additional context")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Setup logger
    logger = setup_logger()

    # Load configuration
    config = Config.load(args.config)

    # Initialize engine
    engine = AutocoderEngine(config)

    try:
        if args.command == "generate":
            logger.info(f"Generating code from {args.input}")
            engine.generate(args.input, args.output, args.language)
            logger.info(f"Code generated successfully: {args.output}")

        elif args.command == "analyze":
            logger.info(f"Analyzing {args.file}")
            results = engine.analyze(args.file)
            if args.report:
                engine.save_report(results, args.report)
            else:
                print(results)
            logger.info("Analysis complete")

        elif args.command == "refactor":
            logger.info(f"Refactoring {args.file}")
            output = args.output or args.file
            engine.refactor(args.file, output, args.style)
            logger.info(f"Refactoring complete: {output}")

        elif args.command == "complete":
            logger.info(f"Auto-completing {args.file}")
            engine.complete(args.file, args.context)
            logger.info("Completion successful")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
