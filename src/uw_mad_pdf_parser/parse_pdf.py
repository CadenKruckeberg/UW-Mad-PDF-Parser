import heuristics

import csv
import os
import pdfplumber
from pathlib import Path
import re
import sys

def identify_pdf(path: str):
    pdf_type = ''
    term_code = ''

    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        if 'DEPARTMENT INSTRUCTIONAL REPORT' in text.upper():
            pdf_type = 'dir'
            match = re.search(r'TERM *: *(\d+)', text.upper())
            if match:
                term_code = match.group(1)
                term = int(term_code)
        elif 'percentage distribution of grades' in text.lower():
            pdf_type = 'grades'
            match = re.search(r'TERM *: *(\d+)', text.upper())
            if match:
                term_code = match.group(1)
                term = int(term_code)
        return (pdf_type, term_code)

def parse_pdf(path: str, debug_pages: list = [], output_skipped: bool = False, output_dir: str = '.'):
    pdf_type, term_code = identify_pdf(path)
    if not pdf_type: print(f'Unable to identify pdf as either dir or grades: {path}.')
    if not term_code: print(f'Unable to identify which term pdf is for {path}.')
    if not pdf_type or not term_code: sys.exit(1)

    match pdf_type:
        case 'dir':
            parse_dir(term_code, path, debug_pages=debug_pages, output_skipped=output_skipped, output_dir=output_dir)
        case 'grades':
            parse_grades(term_code, path, debug_pages=debug_pages, output_skipped=output_skipped, output_dir=output_dir)

def get_min_x0_and_max_x1(page):
    '''
    Return horizontal text bounds on a pdfplumber page.

    Uses `page.extract_words()` to find:
    - min_x0: leftmost word position
    - max_x1: rightmost word position

    Returns:
        (min_x0, max_x1) as floats.
    '''
    words = page.extract_words()
    min_x0 = page.width + 1
    max_x1 = 0
    for word in words:
        if word['x0'] < min_x0:
            min_x0 = word['x0']
        if word['x1'] > max_x1:
            max_x1 = word['x1']
    return (min_x0, max_x1)


def parse_dir(term_code: str, path_to_dir_pdf: str, delimiter: str = '\t', debug_pages: list = [], output_skipped: bool = False,
              output_dir: str = '.'):
    term_heuristics = heuristics.get_dir_heuristics(int(term_code))

    with pdfplumber.open(path_to_dir_pdf) as pdf:

        if debug_pages:
            for page_num in debug_pages:
                page = pdf.pages[page_num-1]
                min_x0, max_x1 = get_min_x0_and_max_x1(page)
                cropped = page.crop((term_heuristics['margins']['left'], term_heuristics['margins']['upper'], page.width - term_heuristics['margins']['right'], page.height - term_heuristics['margins']['lower']))
                im = cropped.to_image(resolution=150)
                im.draw_rects(cropped.extract_words())
                for x in (min_x0 - 3,) + term_heuristics['column_lines'] + (max_x1 + 3,):
                    im.draw_vline(x, stroke='red', stroke_width=2)
                im.save(Path(output_dir) / f'{term_code}-dir-{page_num}.png')
            return

        with open(Path(output_dir) / f'{term_code}-dir.tsv', 'w', newline='', encoding='utf-8') as csvfile, \
             open(Path(output_dir) / f'{term_code}-dir-skipped.tsv', 'w', newline='', encoding='utf-8') if output_skipped else open(os.devnull, 'w') as skipfile:
            writer = csv.writer(csvfile, delimiter=delimiter)
            skip_writer = csv.writer(skipfile, delimiter=delimiter)
            writer.writerow(tuple( additional_header['header'] for additional_header in term_heuristics['additional_headers'] ) + term_heuristics['pdf_headers'])

            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    for additional_header in term_heuristics['additional_headers']:
                        match = re.search(additional_header['regex'], text)
                        if match:
                            additional_header['value'] = match.group(1)

                cropped = page.crop((term_heuristics['margins']['left'], term_heuristics['margins']['upper'], page.width - term_heuristics['margins']['right'], page.height - term_heuristics['margins']['lower']))

                min_x0, max_x1 = get_min_x0_and_max_x1(cropped) # we do this because pdfplumber doesn't really respect the explicit columns, so we have to define the first and last column borders to be close to the extremes of where the data are actually placed on the page

                table = cropped.extract_table({
                    'vertical_strategy': 'explicit',
                    'horizontal_strategy': term_heuristics['horizontal_strategy'],
                    'explicit_vertical_lines': (min_x0 - 3,) + term_heuristics['column_lines'] + (max_x1 + 3,),
                })

                if table:
                    for row in table:
                        if any(row):
                            cleaned_row = [ ' '.join(cell.split()) if cell else '' for cell in row ] # take newlines out of values
                            if tuple(cleaned_row) == term_heuristics['pdf_headers'] or \
                                len(cleaned_row) != len(term_heuristics['pdf_headers']) or \
                                not ''.join(cleaned_row[-4:]): # if the last 4 columns are empty, we assume it isn't a valid row. the benefit is that sometime the subject: foo is a row and gets rejected
                                if output_skipped: skip_writer.writerow(cleaned_row)
                                continue
                            writer.writerow([additional_header['value'] for additional_header in term_heuristics['additional_headers']] + cleaned_row)

def parse_grades(term_code: str, path_to_grades_pdf: str, delimiter: str = '\t', debug_pages: list = [], output_skipped: bool = False, \
              output_dir: str = '.'):
    term_heuristics = heuristics.get_grades_heuristics(int(term_code))

    with pdfplumber.open(path_to_grades_pdf) as pdf:

        if debug_pages:
            for page_num in debug_pages:
                page = pdf.pages[page_num-1]
                min_x0, max_x1 = get_min_x0_and_max_x1(page)
                cropped = page.crop((term_heuristics['margins']['left'], term_heuristics['margins']['upper'], page.width - term_heuristics['margins']['right'], page.height - term_heuristics['margins']['lower']))
                im = cropped.to_image(resolution=150)
                im.draw_rects(cropped.extract_words())
                for x in (min_x0 - 3,) + term_heuristics['column_lines'] + (max_x1 + 3,):
                    im.draw_vline(x, stroke='red', stroke_width=2)
                im.save(Path(output_dir) / f'{term_code}-grades-{page_num}.png')
            return


        with open(Path(output_dir) / f'{term_code}-grades.tsv', 'w', newline='', encoding='utf-8') as csvfile, \
             open(Path(output_dir) / f'{term_code}-grades-skipped.tsv', 'w', newline='', encoding='utf-8') if output_skipped else open(os.devnull, 'w') as skipfile:
            writer = csv.writer(csvfile, delimiter=delimiter)
            writer.writerow(tuple( additional_header['header'] for additional_header in term_heuristics['additional_headers'] ) + term_heuristics['pdf_headers'])
            skip_writer = csv.writer(skipfile, delimiter=delimiter)

            queued = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    for additional_header in term_heuristics['additional_headers']:
                        match = re.search(additional_header['regex'], text)
                        if match:
                            additional_header['value'] = match.group(1)

                cropped = page.crop((term_heuristics['margins']['left'], term_heuristics['margins']['upper'], page.width - term_heuristics['margins']['right'], page.height - term_heuristics['margins']['lower']))

                min_x0, max_x1 = get_min_x0_and_max_x1(cropped) # we do this because pdfplumber doesn't really respect the explicit columns, so we have to define the first and last column borders to be close to the extremes of where the data are actually placed on the page

                table = cropped.extract_table({
                    'vertical_strategy': 'explicit',
                    'horizontal_strategy': term_heuristics['horizontal_strategy'],
                    'explicit_vertical_lines': (min_x0 - 3,) + term_heuristics['column_lines'] + (max_x1 + 3,),
                })

                if table:
                    i = 0
                    while i < len(table):
                        row = table[i]
                        if any(row):
                            cleaned_row = [ ' '.join(cell.split()) if cell else '' for cell in row ] # take newlines out of values
                            pattern = r'\d+ (\d|[A-Z])+.*' # everything after the \d|[A-Z] is due to an error in the pdf I think, but here is where I draw the boundry between data parser and wrangler
                            '''
                            pdf plumber will completely ignore a column if it is completely empty and the leftmost or rightmost despite providing explicit columns.
                            this happens when the contents of a page of the grades pdf is entirely filled with sections to the same course.
                            we remedy this by checking if there are too few columns and if the first entry is the course code (which is expected to instead come second)
                            '''
                            if len(cleaned_row) < len(term_heuristics['pdf_headers']) and re.fullmatch(pattern, cleaned_row[0]):
                                cleaned_row = [''] + cleaned_row

                            if tuple(cleaned_row) == term_heuristics['pdf_headers']:
                                i+=1
                                continue
                            elif cleaned_row[1].strip() == 'Course Total': # this is often where we get the course name for the previously "processed" (put into the queued list) rows
                                pass # so we continue on
                            elif not re.fullmatch(pattern, cleaned_row[1]):
                                if output_skipped: skip_writer.writerow(cleaned_row)
                                i+=1
                                continue
                            else:
                                queued.append(cleaned_row) # we might have the course name in this row, we might not. we don't write the row yet regardless

                            # now if we DO have the course name, write each row we saw before this one (and itself) with the course name (in order they were initally seen)
                            course_name = cleaned_row[0]
                            if course_name:
                                next_row = table[i+1]
                                next_course_name = next_row[0]
                                if not any(next_row[1:]) and next_course_name: # this handles the case when a row is two rows tall because of a long course name. if it were longer than 2, this still wouldn't be perfect
                                    course_name = course_name + next_course_name
                                    i+=1
                                while queued:
                                    record = queued.pop(0)
                                    record[0] = course_name
                                    writer.writerow([additional_header['value'] for additional_header in term_heuristics['additional_headers']] + record)
                        i+=1

