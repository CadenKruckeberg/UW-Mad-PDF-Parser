import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import os
import sys

import parse_pdf

def collect_pdfs(paths):
    pdf_files = []
    for p in paths:
        target_path = Path(p)
        if not target_path.exists():
            print(f'Error: The path "{target_path}" does not exist.', file=sys.stderr)
            continue
        if target_path.is_dir():
            found = list(target_path.glob("*.pdf"))
            if not found:
                print(f'No PDF files found in directory: {target_path}')
            pdf_files.extend(found)
        elif target_path.is_file() and target_path.suffix.lower() == '.pdf':
            pdf_files.append(target_path)
    return pdf_files

def process(pdf_file, output_skipped, output_dir, debug_pages):
    try:
        parse_pdf.parse_pdf(
            str(pdf_file),
            debug_pages=debug_pages,
            output_skipped=output_skipped,
            output_dir=str(output_dir) if output_dir else '.'
        )
    except Exception as e:
        print(f'Error processing {pdf_file.name}: {e}', file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description='Extract data from PDF files or directories of PDFs.'
    )

    parser.add_argument(
        'paths',
        nargs='+',
        metavar='PATH',
        help='One or more PDF files or directories containing PDFs.'
    )

    parser.add_argument(
        '-p',
        '--debug-page',
        type=int,
        action='append',
        metavar='N',
        help='Generate debug images for the specified page number. '
            'Can be used multiple times (e.g. -p 1 -p 3).'
    )

    parser.add_argument(
        '-s',
        '--output-skipped',
        action='store_true',
        help='Write skipped rows to a separate TSV output file.'
    )

    parser.add_argument(
        '-j',
        '--jobs',
        type=int,
        default=max(1, (os.cpu_count() or 1) - 1),
        metavar='N',
        help='Number of PDFs to process in parallel.'
    )

    parser.add_argument(
        '-o',
        '--output-dir',
        type=str,
        metavar='DIR',
        help='Directory to write output files (default: current directory).'
    )

    args = parser.parse_args()

    debug_pages = args.debug_page

    output_dir = Path(args.output_dir) if args.output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = collect_pdfs(args.paths)

    if not pdf_files:
        sys.exit(0)

    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        futures = [
            executor.submit(
                process,
                pdf_file,
                args.output_skipped,
                output_dir,
                debug_pages
            )
            for pdf_file in pdf_files
        ]
        for _ in as_completed(futures):
            pass

if __name__ == '__main__':
    main()
