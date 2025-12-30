''' 
The Rubric Module represents a Rubric object, for grading CS1
laboratory assignments. The Rubric.csv file is turned into a python
object and fields are modifiable, and can be written back out in appropriate
Rubric.csv format.

Held together by duct tape & if-loops by Iris Howley (2023)
'''
import csv
import CS1GradeOmaticUtils as gom_utils

__all__ = ['Rubric']

#############################
###      RUBRIC CLASS     ###
#############################
class Rubric:
    __slots__ = ['_criteria']

    # constants
    DELIMITER = gom_utils.RUBRIC_DELIMITER

    def __init__(self, rows:list):
        ''' Creates a new Rubric object with a list of rows (str)
        to be parsed into criteria.
        >>> r1 = Rubric(["1. Criteria 1.", "  + file.py: An indented criteria"])
        >>> r1._criteria[0]
        ['1.', '', 'Criteria 1.']
        >>> r1._criteria[1]
        ['  +', 'file.py', 'An indented criteria']
        '''
        self._criteria = [gom_utils.parse_criteria(r) for r in rows]

    def add_criteria(self, criteria:list):
        ''' Adds a single criteria to this rubric. Criteria is a 3-item list:
        severity, filename (optional), and comment
        >>> r1 = Rubric(["1. Criteria 1."]) 
        >>> r1.add_criteria(['  +', 'file.py', 'An indented criteria'])
        >>> r1._criteria[1]
        ['  +', 'file.py', 'An indented criteria']
        >>> r1.add_criteria(['~', 'Missing the filename.'])
        >>> r1._criteria[2]
        ['~', '', 'Missing the filename.']
        '''
        if len(criteria) == 3 or len(criteria)==1:
            self._criteria.append(criteria)
        elif len(criteria) == 2: # handles the optional filename
            self._criteria.append([criteria[0], '', criteria[-1]])
        else:
            print('WARNING::Rubric.add_criteria: criteria not correct length:', criteria)

    def extend_criteria(self, criterias:list):
        ''' Adds multiple criteria/comments to this rubric.
        criteries is a list of 3-item (or 2-item) (or 1-item, for headers) lists
        >>> r1 = Rubric(["1. Criteria 1."]) 
        >>> r1.extend_criteria([['  +', 'file.py', 'An indented criteria'], ['~', 'Missing the filename.']])
        >>> r1._criteria[1]
        ['  +', 'file.py', 'An indented criteria']
        >>> r1._criteria[2]
        ['~', '', 'Missing the filename.']
        '''
        [self.add_criteria(crit) for crit in criterias]

    def overwrite(self, filename:str):
        ''' Writes current rubric to a file, overwriting whatever
        exists at the given filename
        '''
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=Rubric.DELIMITER, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for c in self._criteria:
                if len(c) == 3 or len(c) == 1: # ignores wonky format rows!
                    csvwriter.writerow(c)

    #############################
    ###      PROPERTIES      ###
    @property
    def criteria(self) -> list:
        ''' Returns the criteria represented by this Rubric as a list.
        >>> r1 = Rubric(["1. Criteria 1.", "  + file.py: An indented criteria"])
        >>> r1.criteria
        [['1.', '', 'Criteria 1.'], ['  +', 'file.py', 'An indented criteria']]
        '''
        return self._criteria

    #############################
    ###     STATIC METHODS    ###
    @staticmethod
    def parse_rubric_from_file(filename:str) -> list:
        ''' Parses the string text at a given filename CSV into
        a list of (1 or 3 part) lists, that can be used by the initializer
        to create a rubric
        >>> r1 = Rubric.parse_rubric_from_file('test/rubric-newlines.csv')
        >>> r1[0]
        ['Ranked_Choice()']
        >>> r1[1]
        ['  --', 'ranked_choice()', "This function should return a _new_ list, don't modify the original list!"]
        >>> r1[2]
        ['  ++', '', 'Testing a newline in here\\n  ']
        >>> r1[3]
        ['General']
        >>> r1[4]
        ['*', '', 'general']
        >>> r1[5]
        ['  ++', '', 'Code example could be like this.\\n  `\\n  def code(a):\\n  \\treturn 2+2*a\\n  \\t`\\n  ']
        >>> r1[6]
        ['  --', 'runtests.py', 'In this lab, we required additional tests to be added. Testing code is an important computer science skill!']
        '''
        with open(filename, newline='') as csvfile:
            lines = list(csv.reader(csvfile, delimiter=Rubric.DELIMITER, quotechar=gom_utils.RUBRIC_QUOTE))

        crits = []
        curr_crit = []
        for row in lines:
            if not row or len(row) <= 0: # likely an empty newline somewhere...
                pass  
            elif len(row) == 3 and gom_utils.RUBRIC_QUOTE in row[2]:
                if gom_utils.COMMENT_CODE not in row[2]:
                    row[2] = row[2].lstrip()
                curr_crit = [row[0].rstrip(), row[1].lstrip(), row[2]] # start a curr_crit
            elif curr_crit: # still working on adding to our current criteria
                line = ' '.join(row)
                curr_crit[2] = curr_crit[2] + '\n' + line
                if gom_utils.RUBRIC_QUOTE in line: # end of curr_crit
                    curr_crit[2] = curr_crit[2].replace('"', '') # remove the quotes
                    crits.append(curr_crit)
                    curr_crit = []
            elif len(row) == 3: # not a quoted line
                crits.append([row[0].rstrip(), row[1].lstrip(), row[2].strip()])
            elif len(row) == 2: # not a quoted line
                crits.append([row[0].rstrip(), '', row[1].strip()])
            elif len(row) == 1: # it's a header
                crits.append(row)
            else:
                print("WARNING::Rubric.parse_rub_from_file: Wonky formatting, ignoring:", row)
        return crits

    
    #############################
    ###     STRING METHODS    ###
    @staticmethod
    def crit_to_string(line:list, delim=';') -> str:
        ''' Converts a single criteria into a string, using the 
        delim variable as a delimiter
        >>> Rubric.crit_to_string(["Major"])
        'Major'
        >>> Rubric.crit_to_string(['1.', '', 'Criteria 1.'])
        '1.;;Criteria 1.'
        >>> Rubric.crit_to_string(['  +', 'file.py', 'An indented criteria'], ':')
        '  +:file.py:An indented criteria'
        '''
        to_str = ''
        if line and len(line) == 3: # ignores wonky format rows!
            to_str += line[0] + delim + line[1] + delim + line[2]
        elif line and len(line) == 1: # it's a header
            to_str += line[0]
        elif len(line) < 3: # ignore empty lists, lines, etc.
            return 
        else:
            print("WARNING::Rubric.crit_to_String: Wonky formatting, ignoring:", line)
        return to_str

    def to_string(self, delim=';') -> str:
        ''' Converts all the criteria in this rubric into
        a string, using the delim variable as a delimiter
        >>> r1 = Rubric(["1. Criteria 1.", "  + file.py: An indented criteria"])
        >>> r1.to_string()
        '1.;;Criteria 1.\\n  +;file.py;An indented criteria'
        '''
        to_str = ''
        for c in self._criteria:
            
            formatted = Rubric.crit_to_string(c, delim)
            if formatted:
                to_str += formatted + '\n'
        return to_str[:-1] if to_str[-1]=='\n' else to_str # remove final newline
    
    def __str__(self) -> str:
        ''' Converts all the comments in this rubric into
        a string, using tab to delimit between cells
        >>> r1 = Rubric(["1. Criteria 1.", "  + file.py: An indented criteria"])
        >>> str(r1)
        '1.\\t\\tCriteria 1.\\n  +\\tfile.py\\tAn indented criteria'
        '''
        return self.to_string('\t')


#############################
###         main()        ###
#############################
if __name__ == '__main__':
    ''' Testing our Rubric object read-in from file
    '''

    print("-=-=- RUBRIC 2 -=-=-")
    test2 = Rubric(Rubric.parse_rubric_from_file('test/rubric-newlines.csv'))
    print(test2)

    print("-=-=- Doctests of basic functions -=-=-")
    import doctest
    doctest.testmod()