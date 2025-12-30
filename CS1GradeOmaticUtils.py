''' 
The Grade-O-Matic Utils (GOMutils) module holds some utilities for the CS1 Grade-O-Matic.
Mostly, editable comments that are likely to be changed by users, constants used across
the modules, and functions used across multiple modules.

Held together by duct tape & if-loops by Iris Howley (2023)
'''

##################################
### CHANGEABLE CONSTANT VALUES ###
# directory loading
DEFAULT_RUBRICDIR = './rubrics/rubric01.csv' # default rubric directory
DEFAULT_DIR = '/grading-cs1' # default directory for opening lab folders (uses rubric directory for filepath)
DIR_RUBRIC_INIT = '.' # default directory for looking for the rubric
IGNORE_DIRS = ['autotest', 'eph1', 'eph2', 'testing', 'README.md', 'result.html', '.git', '.gitignore']

# spacing
MAX_CHARS_GRADESHEET = 75 
RUBRIC_SPACING = ' '*1
REQUIREMENT_INDENT = 3
COMMENT_INDENT = 3  

# GradeSheet bullets/delimeters
COMMENT_SEVERITY = ['+'*4, '+'*3, '+'*2, '+'*1, '-'*4, '-'*3, '-'*2, '-'*1, '~', '?', '*']  
COMMENT_BULLETS = '.*+-~?())@'
COMMENT_HEADER = '**' # makes a comment with a newline before it
COMMENT_CODE = "`" # starts/ends a code line
RUBRIC_DELIMITER = ';' # used in CSV read/write for Rubric

# string constants for parsing
SLASH = '/' # will need to change for Windows machine, but what won't?
TITLE_TXT = 'GRADE SHEET FOR CS1 LAB'
COMMENT_TXT = 'Comments from Graders:'
GRADE_TXT = 'Grade:   '
REQS_TXT = 'Requirements of this lab:'
FILENAME_GS = 'GradeSheet.txt'    
RUBRIC_QUOTE = '"' 

# Other
EXTENSIONS = ['.py', '.txt', '.java'] # detect if filename in a string

#####################
### GUI CONSTANTS ###
# GUI dimensions
WINDOW_WIDTH = 1800  
WINDOW_HEIGHT = 1500
NUM_CUSTOM_COMMENTS = 5
ENTRY_SM = 10 
ENTRY_MED = ENTRY_SM*2
ENTRY_LG = ENTRY_SM*4
TEXT_GRADESHEET = ENTRY_SM*8

# GUI constants
TEXT_0 = '1.0' # row 1, column 0 
SHIFT_KEYBD_SHORTCUTS = '!@#$%^&*()'
RUBRIC_KEYBD = 'Control' # Shortcut key for appending rubric items
CMNT_KEYBD = 'Control-Shift' # Shrotcut key for appending comment items

# GUI fonts
FONT_TITLE = ('Helvetica', 18, 'bold')
FONT_H1 = (FONT_TITLE[0], FONT_TITLE[1]-2, FONT_TITLE[2])
FONT_H2 = (FONT_H1[0], FONT_H1[1]-2, FONT_H1[2])
FONT_RUBRIC = ('Courier', 16, 'normal')
FONT_GRADESHEET = ('Courier', 16, 'normal')
RED = '#f00' # should be red on any OS?
ORANGE = '#f72'
YELLOW = '#fb1'
BLUE = '#00f'
BLACK = '#000'

#############################
### FUNCTIONS: files      ###
def read_str_file(fname: str) -> str:
    '''Reads in a file from fname, returns as a string
    '''
    list_gs = ''

    # read in from file
    with open(fname ,'r') as f:
        list_gs = f.readlines()
    return ''.join(list_gs) 

def write_str_file(a_string:str, fname='GradeSheet.txt'):
    ''' Writes the given string to a file (using 'w', does NOT append)
    '''
    with open(fname, 'w') as f:
        f.write(a_string)

##################################
### STATIC METHODS: formatting ###
def format_filename(root:str, fname:str) -> str:
    ''' Ensures we don't have double slashes in filepaths
    >>> format_filename("/Users/ihowley/Documents/course/staff/grade-o-matic/rubrics/","rubric01.csv")
    '/Users/ihowley/Documents/course/staff/grade-o-matic/rubrics/rubric01.csv'
    >>> format_filename("/Users/ihowley/Documents/course/staff/grade-o-matic/rubrics/","/rubric01.csv")
    '/Users/ihowley/Documents/course/staff/grade-o-matic/rubrics/rubric01.csv'
    >>> format_filename("", "GradeSheet.txt")
    '/GradeSheet.txt'
    '''
    if root.endswith(SLASH): 
        root = root[:-1]
    if fname.startswith(SLASH):
        fname = fname[1:]
    return root+SLASH+fname

def get_filepath(filepath_name:str) -> str:
    ''' Grabs the filepath from the given string
    >>> get_filepath("/Users/ihowley/Documents/course/staff/grade-o-matic/rubrics/rubric01.csv")
    '/Users/ihowley/Documents/course/staff/grade-o-matic/rubrics'
    >>> get_filepath("/Users/ihowley/grading-cs1/lab01")
    '/Users/ihowley/grading-cs1'
    >>> get_filepath("/Users/ihowley/grading-cs1/lab01/")
    '/Users/ihowley/grading-cs1/lab01'
    >>> get_filepath("GradeSheet.txt")
    'GradeSheet.txt'
    '''
    fp = filepath_name
    if fp.endswith(SLASH): 
        fp = fp[:-1]
    elif SLASH in fp:
        fp = fp[:fp.rfind(SLASH)]
    return fp

def get_filename(filepath_name:str) -> str:
    ''' Grabs the filename from the given string
    >>> get_filename("/Users/ihowley/Documents/course/staff/grade-o-matic/rubrics/rubric01.csv")
    'rubric01.csv'
    >>> get_filename("/Users/ihowley/grading-cs1/lab01")
    'lab01'
    >>> get_filename("/Users/ihowley/grading-cs1/lab01/")
    ''
    >>> get_filename("GradeSheet.txt")
    'GradeSheet.txt'
    '''
    fp = filepath_name
    if SLASH in fp:
        fp = fp[fp.rfind(SLASH)+1:]
    return fp

def format_comment(line:str, max_chars=75, indent=3) -> str:
    ''' Returns the given comment as a string with appropriate spacing.
    Will be indented by indent number of spaces, and each line will be
    at most max_chars long (often shorter, as it splits by word not character).

    NOTE: Isn't going to handle max_chars of small sizes (less than 15) well.
    >>> # Making small widths
    >>> format_comment("Really good job on this lab, particularly in-line comments!", 15, 3)
    'Really good job\\n   on this lab,\\n   particularly\\n   in-line\\n   comments!'
    >>> # Don't keep adding newlines when it's already formatted!
    >>> format_comment("~ Too many comments also makes code difficult to navigate/read! Try to\\n   just get at the bare minimum of functionality/explanation.")
    '~ Too many comments also makes code difficult to navigate/read! Try to just\\n   get at the bare minimum of functionality/explanation.'
    '''
    if max_chars < 15:
        print("GOM Utils:: format_comment: max line width is too small to use reliably:", max_chars)

    # standardize whitespace with indent
    start_indent = len(line) - len(line.lstrip())
    line = start_indent*' ' + ' '.join(line.split()) 

    # limit comment text width
    # breaking words by SPACES, not mid-word!
    limited = []
    start_line = 0
    last_spc = 0
    max_chars = max_chars-indent
    for i in range(0, len(line)):
        if line[i].isspace(): # keep track of last seen space
            last_spc = i
        if (i-(start_line+indent)) == max_chars: # we've reached the max num chars
            limited.append(line[start_line: last_spc])
            start_line = last_spc+1
            i = last_spc+1
    # add last line
    limited.append(line[start_line:])

    #limited = [line[i:i+_Comment.COMMENT_CHARS] for i in range(0, len(line), _Comment.COMMENT_CHARS)]

    to_str = str('\n'+indent*' ').join(limited)
    return to_str

def format_function_name(line:str) -> str:
    ''' Returns line as a standardized function name.
    >>> format_function_name("read_names")
    'read_names()'
    >>> format_function_name("frequency()")
    'frequency()'
    >>> format_function_name("deCamelCase")
    'de_camel_case()'
    >>> format_function_name("deCamelCase()")
    'de_camel_case()'
    >>> format_function_name("(probablyNotGreat)")
    'probably_not_great()'
    >>> format_function_name("(not good either)")
    'not_good_either()'
    >>> format_function_name("use_with_caution(arg)")
    'use_with_caution(arg)'
    >>> format_function_name("use case(i dunno)")
    'use_case(i_dunno)'
    >>> format_function_name("AutoComplete.match_words")
    'AutoComplete.match_words()'
    >>> format_function_name("AC.match_words")
    'AC.match_words()'
    '''
    line = line.replace(' ', '_') # replace spaces
    fname = ''
    p_index = line.find('.')
    if p_index >= 0 and line[0].isupper():
        fname = line[:line.find('.')+1]
        line = line[p_index+1:]
    # lowercase caps
    for ch in line:
        if ch.isupper():
            fname += '_' + ch.lower()
        else:
            fname += ch

    # parentheses handling
    if fname[-1] != ')':
        fname += '()'
    elif fname[0]=='(':
        fname = fname[1:-1] + "()"
    return fname

def is_function_name(line:str) -> bool:
    ''' Returns True if line looks like a function name (i.e., has () or _).
    Line should really not have any spaces in it...
    >>> is_function_name("whatever.py")
    False
    >>> is_function_name("read_names")
    True
    >>> is_function_name("frequency()")
    True
    >>> is_function_name("read_names()")
    True
    >>> is_function_name("(probablyNotGreat)")
    True
    >>> is_function_name("(not good either)")
    False
    '''
    if ' ' in line:
        return False
    l_paren = line.find('(')
    r_paren = line.find(')')
    if l_paren >= 0 and l_paren < r_paren:
        return True
    return '_' in line

def get_file_extension(line:str) -> bool:
    ''' Returns the file extension if line looks like a file name.
    Line should really not have any spaces in it...
    >>> get_file_extension("whatever.py")
    '.py'
    >>> get_file_extension("hello.txt")
    '.txt'
    >>> get_file_extension("why.javaDoWeIncludeThis")
    '.java'
    >>> get_file_extension("read_names()")
    ''
    '''
    if ' ' in line:
        print("WARNING::GOMutils.get_f_ext: Term should not have spaces.")
    for ext in EXTENSIONS:
        if ext in line:
            return ext
    return ''


def parse_criteria(line:str) -> list:
    ''' Splits the comment/criteria into its severity, filename, and text
    as a list of three strings. Rubric and GradeSheet both use this.
    >>> parse_criteria("++ intro.py: Great job!")
    ['++', 'intro.py', 'Great job!']
    >>> parse_criteria("  - Close.")
    ['  -', '', 'Close.']
    >>> parse_criteria("~ goodbye.py: Print statement should correctly describe the operation (sum:+, product: *)")
    ['~', 'goodbye.py', 'Print statement should correctly describe the operation (sum:+, product: *)']
    >>> parse_criteria(["---- file.py: Consider using in-line comments"])
    ['---- file.py: Consider using in-line comments']
    >>> parse_criteria(["----", "file.py", "Consider using in-line comments"])
    ['----', 'file.py', 'Consider using in-line comments']
    >>> parse_criteria("-      Good start, but some issues related to repetitive code & negative   days: ")
    ['-', '', 'Good start, but some issues related to repetitive code & negative days:']
    >>> parse_criteria("-- ranked_choice(): This function ends up in an infinite loop (see the timeout errors in TestResults).")
    ['--', 'ranked_choice()', 'This function ends up in an infinite loop (see the timeout errors in TestResults).']
    >>> parse_criteria("++ Should leave this runtests.py without a colon!")
    ['++', '', 'Should leave this runtests.py without a colon!']
    >>> # Need to remember to handle this wonky situation in GradeSheet.parse_comment_section!
    >>> parse_criteria("   (plurality(character_ballots)).")
    GOMutils:: parse_criteria: Comment being interpreted as a header    (plurality(character_ballots)).
    ['   (plurality(character_ballots)).']
    '''
    if type(line) == list: # doesn't need parsing!
        return line
    sline = line.rstrip() 

    if ' ' not in sline.strip(): # will be treated as a header
        print("GOMutils:: parse_criteria: Comment being interpreted as a header", sline)
        return [sline] if len(sline)>3 else None

    start_index = 0
    # Finding Severity
    first_spc = sline.index(' ', len(sline)-len(sline.lstrip()))
    sv = ''
    # first few chars has something that might be a bullet
    if len(set(sline.lstrip()[:3]).intersection(set(COMMENT_BULLETS))): 
        sv = sline[:first_spc].rstrip()
        start_index = first_spc+1

    # Finding filename in first term (if it exists)
    fname = ''
    txt = sline[start_index: ]
    first_term = txt.split()[0] # only look at first word after severity for fname
    file_marker = get_file_extension(first_term)
    if file_marker:
        end_fname = sline.index(file_marker) + len(file_marker)
        fname = sline[start_index: end_fname]
        txt = sline[end_fname:].strip()
    elif is_function_name(first_term):
            end_fname = sline.index(first_term) + len(first_term)
            fname = sline[start_index: end_fname]
            txt = sline[end_fname:].strip()

    if txt and txt[0] == ':': # remove leading colon from text, if it exists
        txt = txt[1:].lstrip()
    elif fname and fname[-1] == ':': # remove trailing colon from fname, if it exists
        fname = fname[:-1]
    
    return [sv, fname, ' '.join(txt.split())] # remove space repeats from txt
    
if __name__ == '__main__':
    print("-=-=- Doctests of basic functions -=-=-")
    import doctest
    doctest.testmod()
