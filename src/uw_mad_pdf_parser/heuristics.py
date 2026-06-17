DIR = {
    'format_1': {
        'additional_headers': (
            {'header': 'SUBJECT', 'regex': r'SUBJECT:(.*\))'},
        ),
        'column_lines': (52, 76, 105, 129, 149, 212, 227, 239, 251, 263, 275, 287, 300, 365, 430, 485, 549),
        'horizontal_strategy': 'text',
        'pdf_headers': ('SESS', 'CAT', 'COMP', 'SECT', 'OFFER', 'Time', 'M', 'T', 'W', 'R', 'F', 'S', 'X', 'FACILITY_ID', 'COMB_ENRN', 'ENRL_TOT', 'EMPLID', 'INSTRUCTOR ROLE/NAME'),
        'margins': {
            'upper': 118,
            'lower': 34,
            'left': 0,
            'right': 0,
        },
    },
    'format_2': {
        'additional_headers': (
            {'header': 'Subject', 'regex': r'Subject: (.*\))'},
        ),
        'column_lines': (57, 80, 99, 123, 250, 286, 305, 324, 340, 357, 373, 389, 437, 488, 526, 578),
        'horizontal_strategy': 'text',
        'pdf_headers': ('Session', 'Category', 'Section', 'Component', 'Time', 'M', 'T', 'W', 'R', 'F', 'S', 'X', 'Facil ID', 'Comb Enrl', 'Tot Enrl', 'Emplid', 'Instructor Name'),
        'margins': {
            'upper': 81,
            'lower': 45,
            'left': 0,
            'right': 0,
        },
    },
    'format_3': {
        'additional_headers': (
            {'header': 'COLLEGE', 'regex': r'COLLEGE: (.*)\n'},
            {'header': 'SUBJECT', 'regex': r'SUBJECT: (.*\))'},
        ),
        'column_lines': (63, 90, 126, 158, 194, 252, 270, 288, 306, 324, 342, 360, 378, 450, 486, 518, 581),
        'horizontal_strategy': 'lines',
        'pdf_headers': ('SESS', 'CAT', 'COMP', 'SECT', 'OFFER', 'Time', 'M', 'T', 'W', 'R', 'F', 'S', 'X', 'FACILITY', 'COMB ENRN', 'ENRL TOT', 'EMPLID', 'Instructor role / name'),
        'margins': {
            'upper': 104,
            'lower': 43,
            'left': 0,
            'right': 0,
        },
    },
}

GRADES = {
    'format_1': {
        'additional_headers': (
            {'header': 'College', 'regex': r'\n(.*)\n.*Section'},
            {'header': 'Subject', 'regex': r'\n(.*)Section'},
            {'header': 'Subject Code', 'regex': r'(\d+).+Grades *GPA'},
            {'header': 'Subject Short Description', 'regex': r'\d+ (.+) Grades *GPA'},
        ),
        'column_lines': (202, 253, 280, 305, 332, 358, 384, 407, 433, 457, 482, 508, 532, 559, 584, 608, 633, 659, 689),
        'horizontal_strategy': 'text',
        'pdf_headers': ('Course Name', 'Section', '# Grades', 'Ave GPA', 'A', 'AB', 'B', 'BC', 'C', 'D', 'F', 'S', 'U', 'CR', 'N', 'P', 'I', 'NW', 'NR', 'Other'),
        'margins': {
            'upper': 119,
            'lower': 0,
            'left': 0,
            'right': 0,
        },
    }
}

def get_dir_heuristics(term_code: int):
    if 1066 <= term_code and term_code <= 1122:
        return DIR['format_1']
    elif term_code == 1124:
        return DIR['format_2']
    elif 1126 <= term_code and term_code <= 1202:
        return DIR['format_1']
    elif 1204 <= term_code and term_code <= 9996:
        return DIR['format_3']
    else:
        print('unknown term heuristics')

def get_grades_heuristics(term_code: int):
    return GRADES['format_1'] # if there is ever another grade report pdf format, this has to be fleshed out
