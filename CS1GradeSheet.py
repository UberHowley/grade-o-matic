''' 
The GradeSheet Module represents a GradeSheet object, for grading CS1
laboratory assignments. The GradeSheet.txt file is turned into a python
object and fields are modifiable, and can be written back out in appropriate
GradeSheet.txt format.

Note: Not currently being used by the GradeOmatic, as I determined it might be
a little more robust just using whatever is written in the text area, and not
validating against this parser (esp. considering TA comments...)
BUT, GradeSheet is used by the Rubric-O-matic for retroactively replacing comments. 
This may, in fact, cause problems with parsing non-standard things.

Held together by duct tape & if-loops by Iris Howley (2023)
'''
import CS1GradeOmaticUtils as gom_utils

__all__ = ['GradeSheet']

#############################
###    GRADESHEET CLASS   ###
#############################
class GradeSheet:
    ''' Represents a GradeSheet. Parses from file, reads into object, and can write back out to
    file. 
    '''
    __slots__ = ['_num','_desc','_reqs','_grade','_comments']

    # class [constant] variables, imported from GOMutils
    TITLE_TXT1 = gom_utils.TITLE_TXT
    TITLE_TXT2 = 'GRADESHEET FOR CS1 LAB' # same as above, but missing the space
    REQS_TXT = gom_utils.REQS_TXT[: gom_utils.REQS_TXT.rfind(':')]
    GRADE_TXT = gom_utils.GRADE_TXT[: gom_utils.GRADE_TXT.rfind(':')]
    COMMENTS_TXT = gom_utils.COMMENT_TXT[: gom_utils.COMMENT_TXT.rfind(':')]

    #############################
    ###      INITIALIZING     ###
    def __init__(self, lab_number:int, lab_desc:str, requirements:list, grade:str, comments:list):
        ''' Initializes a new GradeSheet object with the given data
        >>> gs = GradeSheet('2', '("Day of the Week")', [], 'B-', [])
        >>> gs._num
        '2'
        >>> gs._desc
        '("Day of the Week")'
        >>> gs.grade
        'B-'
        '''
        self._num = lab_number
        self._desc = lab_desc
        self._reqs = requirements
        self._grade = grade
        self._comments = comments

    def write_file(self, fname='GradeSheet.txt'):
        ''' Writes the GradeSheet to a file (using 'w', does NOT append)
            GradeSheet.txt is the default filename
        '''
        with open(fname, 'w') as f:
            f.write(str(self))
    
    def replace_comment(self, old_cmnt:str, new_cmnt:str) -> bool:
        ''' Replaces old_cmnt with new_cmnt in our list, if it exists.
        Will return true if old_cmnt was replaced, false otherwise.

        First does an 'exact match' search based on severity and text. If
        exact match found, replaces only the found text. 
            i.e. "Nice Job! I like the functions." --> "This is a great job! I like the functions."
        Exact match searches through _every_ comment and replaces all.
        If no exact match found, it does a "loose match" and will replace the entire comment for only
        the first loose match it finds. 
        '''
        success = False
        oc = Comment(old_cmnt, GradeSheet.code_loc(old_cmnt)>=0, GradeSheet.get_indent(old_cmnt)) # _Comment() auto standardizes comment text, not bullets, fname
        nc = Comment(new_cmnt, GradeSheet.code_loc(new_cmnt)>=0, GradeSheet.get_indent(new_cmnt))
        # Find the comment
        for loc in range(len(self._comments)):
            # "Exact match" is currently based on text and severity.
            if oc.severity == self._comments[loc].severity and oc.text in self._comments[loc].text:
                t = self._comments[loc].text.replace(oc.text, nc.text)
                s = nc.severity if nc.severity else ''
                f = nc.filename if nc.filename else ''
                self._comments[loc] = Comment(s + ' ' + f + ' ' + t, GradeSheet.code_loc(t)>=0, GradeSheet.get_indent(t))
                success = True
        if not success: # try a loose equivalence + replace entire comment just once
            loc = 0
            while loc < len(self._comments) and not success:
                if self._comments[loc]._loose_equals(oc): # found a loose match
                    success = True
                    self._comments[loc] = nc
                loc += 1

        return success # return T/F if found/not     

    @staticmethod
    def sort_comments(comments: list) -> list:
        ''' Sorts comments based upon filename/method/function.

        >>> cmnts = [Comment("+ Overall, great job!", False,0), Comment("+ Result._str_(): Nice use of list comprehension & .join!", False,0), Comment("~ AutoComp._init_(): It's better to exit the 'with open() as' block as soon as you're done with the file.", False,0), Comment("- In AC._match_words, both calls to .startswith and .matches_pattern should be called upon 'word'", False,0), Comment("~ In AC.match_words: We could also be more specific here", False,0), Comment("+ AutoComplete._str_(): Nice use of list comprehension!", False,0), Comment("~ FreqWord._init_(): Do not need to cast count to an int", False,0), Comment("+ Awesome job passing all the autotest!!", False,0), Comment("-- Do not call methods on the classes, call them on the instances of the classes.", False,0)]
        >>> c = GradeSheet.sort_comments(cmnts)
        >>> str(c[-2])
        '+ Result._str_(): Nice use of list comprehension & .join!'
        >>> str(c[0])
        '+ Awesome job passing all the autotest!!'
        >>> str(c[-1])
        '+ Overall, great job!'
        '''
        if not comments: # No comments? Nothing to do!
            return     
        # sort based on filename/functioname (if exists)
        cmnts_fnames = []
        cmnts_nofnames = []
        cmnts_final = []
        for cmnt in comments:
            # Catch summary comments intended for the end.
            # remove punctuation, split based on spaces, lowercase, grab first three words:
            first_three = ''.join(ch.lower() for ch in cmnt.text if ch not in set(",.:;!?-")).split()[:3]
            summ = {"summary", "overall", "otherwise", "conclusion"}
            if summ & set(first_three):
                cmnts_final.append(cmnt)
            elif cmnt.filename: # has a filename
                cmnts_fnames.append(cmnt)
            else: # no filename
                cmnts_nofnames.append(cmnt)

        combined = sorted(cmnts_nofnames, key=comments_key) + sorted(cmnts_fnames, key=lambda c: c.filename) + cmnts_final
        #print([str(c) for c in combined])
        return combined
    

    #############################
    ###     STATIC METHODS     ###
    @staticmethod
    def parse_gradesheet_fromfile(fname: str):
        '''Reads in a grade sheet from given filename, returns
        a GradeSheet object.
        '''
        str_gs = ''

        # read in from file
        with open(fname ,'r') as f:
            str_gs = f.readlines()
        return GradeSheet.parse_gradesheet_fromstr(str_gs)

    @staticmethod
    def parse_gradesheet_fromstr(txt_gs: str):
        '''Reads in a grade sheet from given string, returns a GradeSheet object
        '''
        num = 0
        desc = ''
        reqs = []
        grade = ''
        comments = []

        if type(txt_gs) == list: # if it's a list...make it a string
            txt_gs = '\n'.join(txt_gs) 

        # Check for headers, insert if missing
        # GRADE SHEET FOR CS1 LAB
        loc_gstitle = txt_gs.find(GradeSheet.TITLE_TXT1.split()[0])
        end_gstitle = txt_gs.find('\n', loc_gstitle)
        if loc_gstitle < 0:
            print("GradeSheet:: WARNING: No 'GRADE SHEET:' text found!")
            # add header, update start/end location values
            txt_gs = GradeSheet.TITLE_TXT1 + ' :\n' + txt_gs 
            loc_gstitle = loc_gstitle = txt_gs.find(GradeSheet.TITLE_TXT1)
            end_gstitle = txt_gs.find('\n', loc_gstitle) # reset the end
        else: # can only grab lab num/title if it's specified...
            num = GradeSheet.get_lab_num(txt_gs[loc_gstitle: end_gstitle])
            desc = GradeSheet.get_lab_desc(txt_gs[loc_gstitle: end_gstitle])

        # Requirements of this lab:
        loc_reqs = txt_gs.lower().find(GradeSheet.REQS_TXT.lower())
        end_reqs = txt_gs.find('\n', loc_reqs) # reqs line end
        if loc_reqs < 0:
            print("GradeSheet:: WARNING: No 'Requirements:' text found!")
            # add header, update start/end location values
            txt_gs = txt_gs[:end_gstitle] + '\n' + GradeSheet.REQS_TXT + ':' + txt_gs[end_gstitle:]
            loc_reqs = txt_gs.find(GradeSheet.REQS_TXT)
            end_reqs = txt_gs.find('\n', loc_reqs) # reqs line end
        
        # Grade
        loc_grd = txt_gs.lower().find(GradeSheet.GRADE_TXT.lower(), end_reqs)
        end_grd = txt_gs.find('\n', loc_grd) # grade line end
        if loc_grd < 0:
            print("GradeSheet:: ERROR: No 'Grade:' text found!")
            
        # Comments from Graders:
        loc_cmt = txt_gs.lower().find(GradeSheet.COMMENTS_TXT.lower())
        end_cmt = txt_gs.find('\n', loc_cmt) # grade line end
        if loc_cmt < 0:
            print("GradeSheet:: WARNING: No 'Comments:' text found!")
            # add header, update start/end location values
            txt_gs = txt_gs[:end_grd] + '\n' + GradeSheet.COMMENTS_TXT + ':' + txt_gs[end_grd:]
            loc_cmt = txt_gs.find(GradeSheet.COMMENTS_TXT)
            
        # Split into segments
        txt_reqs = txt_gs[end_reqs : loc_grd]   
        txt_reqs = '\n'.join([line.rstrip() for line in txt_reqs.split('\n') if len(line.strip()) > 0]) #excessive newlines
        txt_grd = txt_gs[loc_grd : end_grd].strip()
        txt_cmnts = txt_gs[loc_cmt : ].strip()

        # Grab Grade
        grade = GradeSheet.get_grade(txt_grd)
        # Parse Requirements
        reqs = GradeSheet.parse_rubric_section(txt_reqs)
        # Parse Comments
        comments = GradeSheet.parse_comments_section(txt_cmnts)

        # now create the GradeSheet object
        return GradeSheet(num, desc, reqs, grade, comments)

    ###     Checking line types     ###
    @staticmethod
    def is_reqs_line(line:str) -> bool:
        ''' Returns true if this is a requirements line
        >>> GradeSheet.is_reqs_line('Requirements of this lab')
        True
        >>> GradeSheet.is_reqs_line('Requirements of this lab:')
        True
        >>> GradeSheet.is_reqs_line('Requirement of this lab')
        False
        '''
        return GradeSheet.REQS_TXT in line
    
    @staticmethod
    def is_requirement(line:str) -> bool:
        ''' Returns true if line starts with number, false otherwise
        >>> GradeSheet.is_requirement('1. This is a requirement')
        True
        >>> GradeSheet.is_requirement('    2) This is also a requirement')
        True
        >>> GradeSheet.is_requirement('* Not a requirement')
        False
        '''
        return line.strip()[0].isnumeric()
    
    @staticmethod
    def is_grade_line(line:str) -> bool:
        ''' Returns true if line is the grade text line
        >>> GradeSheet.is_grade_line('Grade:    A')
        True
        >>> GradeSheet.is_grade_line('Grade:    ')
        True
        >>> GradeSheet.is_grade_line('Grade    ')
        True
        >>> GradeSheet.is_grade_line('GRADE SHEET')
        False
        '''
        return line[0:5] == GradeSheet.GRADE_TXT[0:5]
    
    @staticmethod
    def is_comments_line(line:str) -> bool:
        ''' Returns true if line is the comments text line
        >>> GradeSheet.is_comments_line('Comments from Graders: ')
        True
        >>> GradeSheet.is_comments_line('Comments from Graders: With a comment on the same line')
        False
        >>> GradeSheet.is_comments_line('Comments from Graders')
        True
        >>> GradeSheet.is_comments_line('GRADE SHEET')
        False
        '''
        return GradeSheet.COMMENTS_TXT in line and len(line) <= len(GradeSheet.COMMENTS_TXT)+4
    
    @staticmethod
    def starts_with_bullet(line:str) -> bool:
        ''' Returns true if line starts with a bullet.
        Checks the first three characters for a bullet character
        >>> GradeSheet.starts_with_bullet('* This is a bullet')
        True
        >>> GradeSheet.starts_with_bullet('   + Also a bullet')
        True
        >>> GradeSheet.starts_with_bullet('-   Bullet as well')
        True
        >>> GradeSheet.starts_with_bullet('! Not valid bullet')
        False
        '''
        sline = line.strip()
        for c in sline[0:3]:
            if c in gom_utils.COMMENT_BULLETS:
                return True
        return False
    
    @staticmethod
    def code_loc(line:str) -> int:
        ''' Returns index of code denoting character in string.
        -1 if it doesn't exist.
        >>> GradeSheet.code_loc('`')
        0
        >>> GradeSheet.code_loc('Has it at the end`')
        17
        >>> GradeSheet.code_loc('   `Or at the beginning`')
        3
        >>> GradeSheet.code_loc('* Sample bullet')
        -1
        '''
        return line.find(gom_utils.COMMENT_CODE)
    
    ###     Parsing lines    ###
    @staticmethod
    def get_lab_num(line:str) -> str:
        ''' Returns lab num from a grade sheet title
        >>> GradeSheet.get_lab_num('GRADE SHEET FOR CS1 LAB 2 ("Day of the week")')
        '2'
        >>> GradeSheet.get_lab_num('GRADE SHEET FOR CS1 LAB 3 ("Retroshop")')
        '3'
        >>> GradeSheet.get_lab_num('GRADE SHEET FOR CS1')
        ''
        '''
        start_ind = len(GradeSheet.TITLE_TXT1)
        end_ind = len(GradeSheet.TITLE_TXT1)+2 # Not set-up for labs >2 digits!
        return line[start_ind: end_ind].strip()
    
    @staticmethod
    def get_lab_desc(line:str) -> str:
        ''' Returns lab title from a grade sheet title
        >>> GradeSheet.get_lab_desc('GRADE SHEET FOR CS1 LAB 2 ("Day of the week")')
        '("Day of the week")'
        >>> GradeSheet.get_lab_desc('GRADE SHEET FOR CS1 LAB 3 ("Retroshop")')
        '("Retroshop")'
        >>> GradeSheet.get_lab_desc('GRADE SHEET FOR CS1')
        ''
        '''
        return line[len(GradeSheet.TITLE_TXT1)+2:].strip()
      
    @staticmethod
    def get_grade(line:str) -> str:
        ''' Returns grade froma  grade line
        >>> GradeSheet.get_grade('Grade:   A')
        'A'
        >>> GradeSheet.get_grade('Grade:   B+')
        'B+'
        >>> GradeSheet.get_grade('Grade:   ')
        ''
        '''
        return line[line.rfind('e')+1:].replace(':','').strip()
    
    @staticmethod
    def get_indent(line:str) -> int:
        ''' Returns number of spaces before bullet in string, line.
        Returns - 1 if there isn't a bullet or line is small.
        >>> GradeSheet.get_indent('* This is zero')
        0
        >>> GradeSheet.get_indent('   - This is three')
        3
        >>> GradeSheet.get_indent('  ')
        -1
        >>> GradeSheet.get_indent('   Only looks when there is a bullet')
        -1
        '''
        if len(line) > 3 and GradeSheet.starts_with_bullet(line.rstrip()):
            return len(line)-len(line.lstrip()) 
        return -1
    
    @staticmethod
    def parse_rubric_section(rubrics:str) -> list:
        """ Given a string, rubrics, that represents the entire rubric 
        section from a GradeSheet, this method will parse it
        into a list of _Requirements.
        >>> no_subreqs = "   + Correctly implements the function flip_horizontal\\n   * Correctly implements the function transform_image\\n   + Correctly implements the green_screen function\\n   ~ Code makes good use of variable names, and is clear and readable\\n   - Comments are appropriately used to explain hard-to-follow logic"
        >>> crits_no_subreqs = GradeSheet.parse_rubric_section(no_subreqs)
        >>> str(crits_no_subreqs[0])
        '   + Correctly implements the function flip_horizontal'
        >>> str(crits_no_subreqs[1])
        '   * Correctly implements the function transform_image'
        >>> str(crits_no_subreqs[3])
        '   ~ Code makes good use of variable names, and is clear and readable'
        >>> str(crits_no_subreqs[4])
        '   - Comments are appropriately used to explain hard-to-follow logic'
        >>> mix_subreqs = "   ~ Correctly implements the function flip_horizontal\\n   + Correctly implements the function flip_vertical\\n   +/~ Correctly implements the function invert   \\n   1. day_of_week(day)\\n     * Computes correctly\\n     + Makes appropriate use of conditionals \\n   +/~ Comments are appropriately used to explain hard-to-follow logic\\n   + Passes our tests"
        >>> crits_mix_subreqs = GradeSheet.parse_rubric_section(mix_subreqs)
        >>> str(crits_mix_subreqs[0])
        '   ~ Correctly implements the function flip_horizontal'
        >>> str(crits_mix_subreqs[1])
        '   + Correctly implements the function flip_vertical'
        >>> str(crits_mix_subreqs[2])
        '   +/~ Correctly implements the function invert'
        >>> str(crits_mix_subreqs[3])
        '   1. day_of_week(day)\\n     * Computes correctly\\n     + Makes appropriate use of conditionals'
        >>> str(crits_mix_subreqs[4])
        '   +/~ Comments are appropriately used to explain hard-to-follow logic'
        >>> str(crits_mix_subreqs[5])
        '   + Passes our tests'
        """
        reqs = []
        curr_req = None
        # find num indentations
        indents = sorted(set([len(line)-len(line.lstrip()) for line in rubrics.split('\n')]))
        for line in rubrics.split('\n'):
            indent_level = len(line)-len(line.lstrip())
            line = line.strip()
            if len(line) < 3:
                pass # skip short lines
            elif indent_level == indents[0]: # it's a requirement
                if curr_req: #existing current requirement is finished
                    reqs.append(curr_req) 
                    curr_req = None
                curr_req = _Requirement(line)
            elif curr_req is None: 
                print("GradeSheet:: WARNING: Current Req is None in parsing.")
            else: # it's a subreq
                curr_req.add_subreq(line)

        if curr_req : reqs.append(curr_req) # Add the last requirement that may not have been added

        return reqs
    

    @staticmethod
    def parse_comments_section(comments:str) -> list:
        ''' Given a string, comments, that represents the entire comments 
        section from a GradeSheet, this method will parse it
        into a list of Comment objects.
        
        >>> comment_sec = " No bullets here. Goodluck.\\nshould this have a bullet? Who knows.\\n-      Good start, but some issues related to repetitive code & negative\\n   days: \\n~      Too much comments also makes code difficult to navigate/read! Try\\n   to just get at the Bare minimum of functionality/explanation.\\n-       Good start, but some minor issues: \\n   --      dayOfWeek doesn’t return all days of the week\\nppp write whatever here.\\n"
        >>> crits = GradeSheet.parse_comments_section(comment_sec)
        >>> str(crits[0])
        '- No bullets here.'
        >>> str(crits[2])
        '- should this have a bullet?'
        >>> str(crits[4]) # str(_Comment) injects newlines & indentations for GradeSheet line width
        '- Good start, but some issues related to repetitive code & negative\\n   days:'
        >>> str(crits[5]) # str(_Comment) injects newlines & indentations for GradeSheet line width
        '~ Too much comments also makes code difficult to navigate/read! Try to\\n   just get at the Bare minimum of functionality/explanation.'
        >>> str(crits[6]) # str(_Comment) injects newlines & indentations for GradeSheet line width
        '- Good start, but some minor issues:'
        >>> str(crits[7]) # str(_Comment) injects newlines & indentations for GradeSheet line width
        '   -- dayOfWeek doesn’t return all days of the week ppp write\\n      whatever here.'
        >>> lida_mid = "Comments from Graders: Good job! Code passes all tests\\n* general\\n   ~ the list comprehensions used to initialize the new_images are a complex\\ntechnique that have not been taught in this class - it's a good idea to\\ndemonstrate a solid understanding of the concepts that have been presented \\nin class rather than using other approaches that have not yet been covered\\n         `\\n def flip_horizontal(image):\\n    new_image = []\\n    for row in image:\\n       new_image = new_image + [row[::-1]]\\n    return new_image\\n \\n def flip_vertical(image):\\n    return image[::-1]\\n`\\n   ~ In python there are two approaches to for loops --> \\n  (1) use range and iterate over indices (which is necessary in green_screen\\nbecause knowing the index makes it possible to loop through two images\\nsimultaneously)\\n  (2) directly iterate over the elements if index location is not relevant \\n * this is the more efficient approach for all the other retroshop functions\\n and would eliminate the need for the for loop that initializes each\\n element in the new_image with empty lists"
        >>> lida_crits = GradeSheet.parse_comments_section(lida_mid)
        >>> str(lida_crits[0])
        '+ Good job!'
        >>> str(lida_crits[1])
        '- Code passes all tests'
        >>> str(lida_crits[3])
        ' * this is the more efficient approach for all the other retroshop\\n    functions and would eliminate the need for the for loop that\\n    initializes each element in the new_image with empty lists'
        >>> just_code = "         `        \\n def flip_horizontal(image):        \\n    new_image = []        \\n    for row in image:        \\n       new_image = new_image + [row[::-1]]        \\n    return new_image        \\n    \\n def flip_vertical(image):        \\n    return image[::-1]\\n`"
        >>> code_crits = GradeSheet.parse_comments_section(just_code)
        >>> str(code_crits[0])
        '         `\\n def flip_horizontal(image):\\n    new_image = []\\n    for row in image:\\n       new_image = new_image + [row[::-1]]\\n    return new_image\\n\\n def flip_vertical(image):\\n    return image[::-1]\\n`'
        '''
        lines = comments.split('\n')
        # Empty Check
        if len(lines) < 1 or (len(lines)==1 and GradeSheet.is_comments_line(lines[0])):
            print("!::GradeSheet.parse_comments_section: Has no items.", comments)
            return []
        
        # Header Handling
        if GradeSheet.is_comments_line(lines[0]): # don't need to parse the header
            lines = lines[1:]
        elif GradeSheet.COMMENTS_TXT in lines[0]: # if comment is on same line as header
            lines[0] = lines[0].removeprefix(GradeSheet.COMMENTS_TXT+':').strip()
        
        # check to see if this comments section uses sub-comments
        indents = sorted(list(set([GradeSheet.get_indent(i) for i in lines if GradeSheet.get_indent(i) >= 0])))
        # [], [0], [0, 3], [0,2,3],[0,3,6,9]
        is_indented =  indents and len(indents) > 1 # these are indented comments...
        if not is_indented:
            indents = [0]
        
        cmnts = []
        curr_cmnt_txt = ''
        found_bullet = False
        in_code = False
        un_bulleted = ''
        for line in lines:
            #print("line", line)
            if GradeSheet.code_loc(line) < 0 and len(line) < 4: # skip short lines, but not code denotes
                pass
            # it's a new bulleted comment or new piece of code
            elif GradeSheet.starts_with_bullet(line) or (not in_code and GradeSheet.code_loc(line) >= 0): 
                # save existing comment, if it exists
                if len(curr_cmnt_txt): 
                    prev_indent = GradeSheet.get_indent(curr_cmnt_txt) #+ gom_utils.COMMENT_INDENT
                    is_code = GradeSheet.code_loc(curr_cmnt_txt) >= 0
                    if  cmnts and (prev_indent > 0 or is_code): # prev comment was sub-comment w. existing comment...or code
                        cmnts[-1].add_subcomment(Comment(curr_cmnt_txt, is_code, prev_indent+ gom_utils.COMMENT_INDENT))
                    else: # prev comment was top-level comment
                        cmnts.append(Comment(curr_cmnt_txt, is_code, prev_indent+ gom_utils.COMMENT_INDENT)) 
                # START: a code comment
                if not in_code and GradeSheet.code_loc(line) >= 0: 
                    in_code = True
                # START: a bulleted comment
                else: 
                    found_bullet = True
                curr_cmnt_txt = line.rstrip()
            elif in_code: # continuing a code comment
                curr_cmnt_txt += '\n' + line.rstrip()
                if GradeSheet.code_loc(line)>=0: # ending a code comment
                    in_code = False
            elif found_bullet and len(curr_cmnt_txt): # it's part of the existing comment
                curr_cmnt_txt += ' ' + line.strip()
            elif not found_bullet: # it's an un-bulleted comment
                un_bulleted += line.strip() + ' '
            else:
                print("WARNING::GradeSheet.parse_comments_section: Can't parse this comments line", line) 
        # add the last captured comment
        is_code = GradeSheet.code_loc(curr_cmnt_txt) >= 0
        indent = GradeSheet.get_indent(curr_cmnt_txt)+gom_utils.COMMENT_INDENT
        if len(curr_cmnt_txt): cmnts.append(Comment(curr_cmnt_txt, is_code, indent)) 

        fixed = []
        for line in GradeSheet.split_by_chars(un_bulleted, '.?!;'): # split by sentence
            if len(line) > 3: # don't add bullets to empty strings
                bullet = '-' # if it's a comment, it's probably negative...
                lowered = line.lower()
                set_lowered = set(lowered.split())
                # slight customization of bullets
                neg = {'should', "don't", 'not', 'better'}
                pos = {"good", "great", "nice", "neat", "awesome", "wonderful", "correct"}
                if 'but ' in lowered:
                    bullet = '~'
                elif pos & set(set_lowered) and 'not' not in lowered:
                    bullet = '+'
                elif neg & set(set_lowered):
                    bullet = '-'
                fixed.append(Comment(bullet + ' ' + line, False, gom_utils.COMMENT_INDENT)) # add bullet
        
        return fixed + cmnts
    
    @staticmethod
    def split_by_chars(line:str, chars='.;!?') -> list:
        ''' Works like .split() for given string, except it splits
        upon multiple delimiters (chars), and KEEPS those chars in the 
        list of strings it produces.
        >>> GradeSheet.split_by_chars('This is the first sentence. This is the second! And the third!')
        ['This is the first sentence.', ' This is the second!', ' And the third!']
        >>> GradeSheet.split_by_chars('No punctuation')
        ['No punctuation']
        >>> GradeSheet.split_by_chars('One punctuation.')
        ['One punctuation.']
        >>> GradeSheet.split_by_chars("Try not to split on TestResults.txt!")
        ['Try not to split on TestResults.txt!']
        >>> GradeSheet.split_by_chars("Do not split python.py in two.")
        ['Do not split python.py in two.']
        >>> GradeSheet.split_by_chars("How should .remove() be split?")
        ['How should .remove() be split?']
        >>> GradeSheet.split_by_chars("What about AutoComplete._init_()?")
        ['What about AutoComplete._init_()?']
        >>> GradeSheet.split_by_chars('')
        []
        '''
        to_list = []
        start_split = 0
        for index in range(len(line)):
            next_word = line[index:line.find(' ', index)]
            if gom_utils.is_function_name(next_word) or gom_utils.get_file_extension(next_word):
                # ignore functions and filenames!
                continue
            elif line[index] in chars:
                to_list.append(line[start_split: index+1])
                start_split = index+1
        if line[start_split: ]:
            to_list.append(line[start_split: ]) # add the last item
        return to_list
    
    #############################
    ###       PROPERTIES      ###
    @property
    def filename(self) -> str:
        return self._filename
    @filename.setter
    def filename(self, f):
        self._filename = f

    @property
    def grade(self) -> str:
        ''' Returns the grade for this Gradesheet as a string
        >>> gs = GradeSheet(' 2', '("Day of the Week")', [], 'B-', [])
        >>> gs.grade
        'B-'
        '''
        return self._grade
    @grade.setter
    def grade(self, g):
        ''' Sets the grade for this GradeSheet to string, g.
        >>> gs = GradeSheet(' 2', '("Day of the Week")', [], 'B-', [])
        >>> gs.grade = 'D'
        'D'
        '''
        self._grade = g

    #############################
    ###     STRING METHODS    ###
    def str_title(self) -> str:
        ''' Converts the title data to a string
        >>> gs = GradeSheet(' 2', '("Day of the Week")', [], 'B-', [])
        >>> gs.str_title()
        'GRADE SHEET FOR CS1 LAB 2 ("Day of the Week")'
        '''
        return GradeSheet.TITLE_TXT1 + str(self._num) + ' ' + self._desc

    def str_reqs(self) -> str:
        ''' Converts the list of requirements and subreqs to a string with
        appropriate indendations'''
        to_str = ''
        print("in str_reqs")
        for rq in self._reqs:
            to_str += str(rq) + '\n'
        return to_str
    
    def str_comments(self) -> str:
        ''' Converts the list of comments to a string with
        appropriate indendation'''
        return '\n'.join([str(cm) for cm in self._comments])
    
    def str_grade(self) -> str:
        ''' Converts the letter grade to a string
        >>> gs1 = GradeSheet('2', '("Day of the Week")', [], 'B-', [])
        >>> gs1.str_grade()
        'Grade:   B-'
        >>> gs2 = GradeSheet('3', '("Retroshop")', [], '', [])
        >>> gs2.str_grade()
        'Grade:   '
        '''
        return gom_utils.GRADE_TXT + self._grade # use utils grade_txt for spacing + :
    
    def __str__(self):
        ''' String representation of the GradeSheet.
        Should be replica of original read-in.'''
        print("in__str__")
        to_str = [self.str_title()+'\n', GradeSheet.REQS_TXT+": ", self.str_reqs()]
        to_str.extend([self.str_grade()+'\n', GradeSheet.COMMENTS_TXT+': \n', self.str_comments()])
        return '\n'.join(to_str)
    
#############################
###    COMMENT CLASS   ###
#############################
class Comment:
    ''' This class represents a single Comment in the GradeSheet.
    Basically, a mapping from comment to its severity and filenames
    '''
    __slots__ = ['_severity', '_filename', '_text', '_subcomments', '_indent', '_is_code']

    # class [constant] variables, pulled from gom_utils
    SEVERITY = gom_utils.COMMENT_SEVERITY

    def __init__(self,cm_line:str, is_code:bool, indent:int):
        ''' Takes string line from file (concatenated to include entire comment), 
        and parses into Comment object
        >>> c = Comment("++ A single comment.", False, 3)
        >>> c._indent
        '   '
        >>> c._is_code
        False
        >>> c = Comment("`def something()`", True, 2)
        >>> c._indent
        '  '
        >>> c._is_code
        True
        '''
        self._indent = indent*' '
        self._is_code = is_code
        self.severity = ''
        self.filename = ''
        self.text = ''    
        self._subcomments = []  

        if self._is_code:
            self.text = cm_line 
        else: # it's not a code comment, parse it!
            [sv, fname, txt] = Comment.split_comment(cm_line)
            self.severity = sv
            self.filename = fname
            self.text = txt    
            self._subcomments = []    

    def add_subcomment(self, cmnt):
        ''' Takes a comment, cmnt, and adds it to our
        list of sub-comments
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c1.add_subcomment("   ~ Testing subcomment")
        >>> c1._subcomments[0]
        '   ~ Testing subcomment'
        '''
        self._subcomments.append(cmnt)

    def pop(self, index=-1):
        ''' Returns and removes the subcomment at the specified location, index.
        Defaults to the last item if no index given.
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c1.add_subcomment("   ~ One subcomment")
        >>> c1.add_subcomment("   -- Two subcomment")
        >>> c1.add_subcomment("   * Three subcomment")
        >>> c1.pop(1)
        '   -- Two subcomment'
        >>> c1.pop()
        '   * Three subcomment'
        '''
        if index < len(self._subcomments): # only remove if valid!
            return self._subcomments.pop(index)
        return -1


    @staticmethod
    def split_comment(line:str) -> list:
        ''' Splits the comment into its severity, filename, and text
        as a list of three strings
        >>> Comment.split_comment('+ filename.py: All three items')
        ['+', 'filename.py', 'All three items']
        >>> Comment.split_comment('   ++ filename.py: All three with indent.')
        ['   ++', 'filename.py', 'All three with indent.']
        >>> Comment.split_comment('- Two items')
        ['-', '', 'Two items']
        >>> Comment.split_comment('   -- Indented by 3.')
        ['   --', '', 'Indented by 3.']
        >>> Comment.split_comment('` Code Comment`')
        ['` Code Comment`']
        >>> Comment.split_comment("-      Good start, but some issues related to repetitive code & negative   days: ")
        ['-', '', 'Good start, but some issues related to repetitive code & negative days:']
        >>> Comment.split_comment("-- ranked_choice(): This function ends up in an infinite loop (see the timeout errors in TestResults).")
        ['--', 'ranked_choice()', 'This function ends up in an infinite loop (see the timeout errors in TestResults).']
        >>> Comment.split_comment("   (plurality(character_ballots)).")
        GOMutils:: parse_criteria: Comment being interpreted as a header    (plurality(character_ballots)).
        ['', '', '   (plurality(character_ballots)).']
        >>> Comment.split_comment("** Try out a header")
        ['\\n**', '', 'Try out a header']
        >>> # TRYING OUT AUTO-FILENAME FOR FUNCTIONS/FNAMES
        >>> Comment.split_comment("+ First three() function")
        ['+', 'three()', 'First three() function']
        '''
        if gom_utils.COMMENT_CODE in line:
            return [line]
        # Special handling if line didn't have any spaces
        # Rubric treats as header...Comment needs to add severity & fname
        parsed = gom_utils.parse_criteria(line) 
        s = parsed[0] if len(parsed)>1 else ''
        f = parsed[1] if len(parsed)>2 else ''
        t = parsed[-1]

        
        if gom_utils.COMMENT_HEADER in s: # handle newline before comment header
            s = '\n' + s

        if s and not f: # if filename is empty, but there's a severity (i.e., not a CSV header)
            # look at first three terms, use one as filename if it's a file/function name
            for term in t.split()[:3]:
                if gom_utils.get_file_extension(term):
                    f = term
                elif gom_utils.is_function_name(term):
                    f = gom_utils.format_function_name(term) 
                    
        return [s, f, t]

    @property
    def severity(self) -> str:
        ''' Returns the severity rating of this Comment, as a string
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c1.severity
        '++'
        >>> c2 = Comment("   --- A single comment.", False, 2)
        >>> c2.severity
        '   ---'
        '''
        return self._severity
    @severity.setter
    def severity(self, s:str):
        ''' Sets the severity rating of this Comment to string s
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c1.severity = '  -'
        >>> c1.severity
        '  -'
        '''
        self._severity = s
        
    @property
    def filename(self) -> str:
        ''' Returns the filename of this Comment as a string. If filename
        has more than one word in it, it checks each word for filename or function name
        and returns the appropriate term.

        >>> c = Comment("++ python.py: A single comment.", False, 3)
        >>> c.filename
        'python.py'
        >>> c = Comment("- Another comment!", False, 3)
        >>> c.filename
        ''
        >>> c = Comment("~ match(): Function, not filename", False, 3)
        >>> c.filename
        'match()'
        '''
        return self._filename 

    @filename.setter
    def filename(self, f:str):
        ''' Sets the filename of this Comment to string f
        >>> c = Comment("++ python.py: A single comment.", False, 3)
        >>> c.filename = 'different.py'
        >>> c.filename
        'different.py'
        >>> c = Comment("- function something()", False, 2)
        >>> c._filename
        'something()'
        >>> c = Comment("- filename whatever.py this is a comment. figure it out.", False, 2)
        >>> c._filename
        'whatever.py'
        >>> c = Comment("~ function match_words", False, 2)
        >>> c._filename
        'match_words()'
        '''
        if gom_utils.is_function_name(f): # standardizing formatting for functionnames
            self._filename = gom_utils.format_function_name(f) 
        else:
            self._filename = f

    @property
    def text(self) -> str:
        ''' Returns the Comment text, as a string
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c1.text
        'A single comment.'
        >>> c2 = Comment("   --- Another, comment.", False, 2)
        >>> c2.text
        'Another, comment.'
        '''
        return self._text
    @text.setter
    def text(self, t:str):
        ''' Sets the text of this Comment to string t
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c1.text = 'Make it different!'
        >>> c1.text
        'Make it different!'
        '''
        if self._is_code: # keep formatting for code subcomment
            self._text = t
        else:
            self._text = standardize(t)

    @property
    def subcomments(self) -> list:
        ''' Returns this Comments subcomments, as a list of comments
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c1.add_subcomment("   ~ One subcomment")
        >>> c1.add_subcomment("   -- Two subcomment")
        >>> c1.add_subcomment("   * Three subcomment")
        >>> len(c1.subcomments)
        3
        >>> c1.subcomments[1]
        '   -- Two subcomment'
        '''
        return self._subcomments
    @subcomments.setter
    def subcomments(self, l:list):
        ''' Replaces this comments subcomments list with the given list, l
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c1.add_subcomment("   ~ One subcomment")
        >>> c1.add_subcomment("   -- Two subcomment")
        >>> c1.add_subcomment("   * Three subcomment")
        >>> c1.subcomments = [Comment("--- A new subcomment.", False, 3), Comment("   * Another sub subcomment", False, 6)]
        >>> c1.subcomments[1]
        '   * Another sub subcomment'
        '''
        self._subcomments = l

    @property
    def comment(self) -> str:
        ''' Returns the Comment's data. 
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c1.comment
        '++ A single comment.'
        >>> c2 = Comment(" - file.py: A different comment.", False, 2)
        >>> c2.comment
        ' - file.py: A different comment.'
        '''
        return str(self)
    @comment.setter
    def comment(self, c:str):
        ''' Takes a string file line, c, and parses it into
        a comment's parts, overwriting whatever is already in this comment 
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c1.comment = '  - file.py: Make it different!'
        >>> [c1.severity, c1.filename, c1.text]
        ['  -', 'file.py', 'Make it different!']
        >>> c1.comment = '~ Something else'
        >>> [c1.severity, c1.filename, c1.text]
        ['~', '', 'Something else']
        >>> c1.comment = '   (plurality(character_ballots)).'
        ['', '', '   (plurality(character_ballots)).']
        '''
        parsed = Comment.split_comment(c)
        self.severity = parsed[0] 
        self.filename = parsed[1] 
        self.text = parsed[2]

    def __str__(self):
        ''' Turn given comment to a string with appropriate spacing
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> str(c1)
        '++ A single comment.'
        >>> c2 = Comment("   ~ Leading spaces preserved?", False, 3)
        >>> str(c2)
        '   ~ Leading spaces preserved?'
        >>> c3 = Comment("   *     Leading spaces after bullet removed?", False, 3)
        >>> str(c3)
        '   * Leading spaces after bullet removed?'
        >>> c4 = Comment("`\\nThis is example code.`", True, 3)
        >>> str(c4)
        '`\\nThis is example code.`'
        >>> c5 = Comment("** Try out a header", False, 3)
        >>> str(c5)
        '\\n** Try out a header'
        '''
        if self._is_code: # special formatting if this is a code block
            return self.text

        s = self.severity+' ' if self.severity else ''
        f = self.filename+': ' if self.filename else ''
        cmt = s + f + self.text
        cmt_str = gom_utils.format_comment(cmt, gom_utils.MAX_CHARS_GRADESHEET-len(self._indent), len(self._indent))
        # headers have newline before them
        #print("Look for **", s)
        if gom_utils.COMMENT_HEADER in s: 
            cmt_str = '\n' + cmt_str.lstrip() # not sure where the extra space _before_ severity is coming from...
        # print all subcomments
        for sc in self._subcomments:
            cmt_str += '\n' + str(sc)
        return cmt_str
    
    def __len__(self):
        ''' Returns the length of this comment, including severity, indent, etc.
        >>> len(Comment("++ A single comment.", False, 0))
        20
        >>> len(Comment("   ~ Leading spaces preserved?", False, 3))
        30
        '''
        return len(self.comment)
    
    def _loose_equals(self, other_cmnt) -> bool:
        ''' Compares this comment's text to the other comment's text *loosely*, looking
        at a set of the words in the text. Ignores whitespace, severity/bullets, and filenames.
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c2 = Comment("++ A single comment.", False, 3)
        >>> c1._loose_equals(c2) # exact match
        True
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c2 = Comment("-- This very different thing to say.", False, 3)
        >>> c1._loose_equals(c2) # not a match
        False
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c2 = Comment("-- A different comment.", False, 3)
        >>> c1._loose_equals(c2) # Close, but not quite - short
        False
        >>> c1 = Comment("++ This is a longer comment about code and what you should and should not do.", False, 3)
        >>> c2 = Comment("-- Here's a longer comment about what you should not do.", False, 3)
        >>> c1._loose_equals(c2) # Close, but not quite - longer
        False
        '''
        # Grab the text to compare
        other_txt = ''
        if type(other_cmnt) == list and len(other_cmnt) > 0 and len(other_cmnt) <= 3:
            other_txt = other_cmnt[-1]
        elif type(other_cmnt) == Comment:
            other_txt = other_cmnt.text
        else: # we're not going to be able to compare
            return False    

        # around the same length of shared words?
        return get_match_percent(other_txt, self.text) > 0.8
   
    def __eq__(self, o):
        ''' Compares this comment to either another _Comment object, 
        or a list of len(3) or len(2) (assuming filename is empty) or
        len(1) (assuming severity is also empty).
        >>> c1 = Comment("++ A single comment.", False, 3)
        >>> c2 = Comment("++ A single comment.", False, 3)
        >>> c1 == c2 # exact match
        True
        >>> c2 = Comment("-- This very different thing to say.", False, 3)
        >>> c1 == c2  # not a match
        False
        >>> c2 = Comment("-- A different comment.", False, 3)
        >>> c1 == c2 # Close, but not quite
        False
        >>> c2 = ['++', '', 'A single comment.']
        >>> c1 == c2 # Compare to list(3)
        True
        >>> c2 = ['++', 'file.py', 'A single comment.']
        >>> c1 == c2 # Compare to list(3) / different filename
        False
        >>> c2 = ['++', 'A single comment.']
        >>> c1 == c2 # Compare to list(2)
        True
        >>> c2 = [' -', 'A single comment.']
        >>> c1 == c2 # Compare to list(2) / diff severity
        False
        >>> c2 = ['A single comment.']
        >>> c1 == c2 # Compare to list(1)
        False
        '''
        if type(o) == list and len(o) == 3:
            return o[0] == self.severity and o[1] == self.filename and o[2] == self.text
        elif type(o) == list and len(o) == 2:
            return o[0] == self.severity and '' == self.filename and o[-1] == self.text
        elif type(o) == list and len(o) == 1:
            return '' == self.severity and '' == self.filename and o[0] == self.text
        elif type(o) == Comment:
            return o.severity == self.severity and o.filename == self.filename and o.text == self.text
        else:
            return False

#############################
###    REQUIREMENT CLASS   ###
#############################
class _Requirement:
    ''' This class represents a single Requirement in the GradeSheet.
    Basically, a mapping from requirement to its (str) subrequirements, so
    we can keep the order of requirements (otherwise, this is a dictionary...)
    '''
    __slots__ = ['_req','_subreqs']

    # class [constant] variables
    INDENT_REQ = ' '*gom_utils.REQUIREMENT_INDENT
    INDENT_SUBREQ = INDENT_REQ+2*' '
    SUBREQ = '* '
    SUBREQ_GRADES = ['+', '+-', '-', '?']

    def __init__(self,rq:str):
        ''' Creates a new _Requirement object, representing the bullets
        at the top of the GradeSheet with string requirement, rq. Initializes
        sub-requirements to empty list.
        >>> r1 = _Requirement("1. Write efficient code.")
        >>> r1._req
        '1. Write efficient code.'
        >>> r1._subreqs
        []
        '''
        self._subreqs = []
        self._req = rq

    def add_subreq(self, sr:str):
        ''' Adds the given (str) subrequirement
        >>> r1 = _Requirement("1. Write efficient code.")
        >>> r1.add_subreq("Use only what is necessary.")
        >>> r1._subreqs[0]
        'Use only what is necessary.'
        '''
        self._subreqs.append(sr)
    def rm_subreq(self, sr:str) -> bool:
        ''' Removes the first instance of the given (str) subrequirement, sr.
        If it doesn't exist in the list, doesn't remove anything and returns False.
        >>> r1 = _Requirement("1. Write efficient code.")
        >>> r1.add_subreq("Use only what is necessary.")
        >>> r1.add_subreq("Use only what is necessary.") # double add
        >>> r1.rm_subreq("Use only what is necessary.") # only remove the first
        True
        >>> len(r1._subreqs)
        1
        >>> r1.rm_subreq("Does not exist.")
        False
        '''
        if sr in self._subreqs:
            self._subreqs.remove(sr)
            return True
        return False

    @staticmethod
    def split_req(rq:str) -> list:
        ''' Splits the number/status demarker from given requirement,
        and returns both as a paired list
        >>> rs1 = _Requirement.split_req("2. localDay(timeval, offset).")
        >>> rs1
        ['2.', 'localDay(timeval, offset).']
        >>> rs2 = _Requirement.split_req("+ Computes correctly")
        >>> rs2
        ['+', 'Computes correctly']
        '''
        sline = rq.strip() # likely not needed...
        first_spc = sline.find(' ')
        dm = sline[:first_spc].strip()
        txt = sline[first_spc+1 : ].strip()
        return [dm, txt]

    @property
    def req(self) -> str:
        ''' Returns this requirement as a string.
        >>> r1 = _Requirement("1. Write efficient code.")
        >>> r1.req
        '1. Write efficient code.'
        '''
        return self._req
    @req.setter
    def req(self, rq:str):
        ''' Changes this requirement's text to string, rq.
        >>> r1 = _Requirement("1. Write efficient code.")
        >>> r1.req = "+ Now something else"
        >>> r1.req
        '+ Now something else'
        '''
        self._req = rq

    @property
    def subreqs(self) -> list:
        ''' Returns this requirement's subrequirements as a list.
        >>> r1 = _Requirement("1. Write efficient code.")
        >>> r1.add_subreq("  + Use only what is necessary.")
        >>> r1.subreqs
        ['  + Use only what is necessary.']
        '''
        return self._subreqs
    @subreqs.setter
    def subreqs(self, srs:list):
        ''' Sets this requirement's subrequirements to the given list, srs.
        >>> r1 = _Requirement("1. Write efficient code.")
        >>> r1.add_subreq("  + Use only what is necessary.")
        >>> r1.subreqs = [' - A change in subrequirement.']
        >>> r1.subreqs
        [' - A change in subrequirement.']
        '''
        self._subreqs = srs

    def __str__(self):
        ''' Converts this Requirement, and all its subrequirements
        into a string
        >>> r1 = _Requirement("1. Write efficient code.")
        >>> r1.add_subreq("  + Use only what is necessary.")
        >>> r1.add_subreq("    - An additional subreq.")
        >>> str(r1)
        '   1. Write efficient code.\\n       + Use only what is necessary.\\n         - An additional subreq.'
        '''
        to_str = [_Requirement.INDENT_REQ + self._req]
        for sr in self._subreqs:
            to_str.append(_Requirement.INDENT_SUBREQ + sr)
        return '\n'.join(to_str)    
    
#############################
###    Useful Functions   ###
#############################  
def standardize(s:str) -> str:
    ''' Removes all whitespace from string, s, and replaces it with 
    a single space.
    >>> # Note: if you want a newline in a docstring, you must escape the backslash...
    >>> standardize("   Here is \t a lot\\nof   random       whitespace.   ")
    'Here is a lot of random whitespace.'
    '''
    return ' '.join(s.split())  

def get_match_percent(s1:str, s2:str) -> float:
    ''' Compares string s1 to s2. If there's spaces, compares based upon words.
    No spaces, compares based upon letters. Returns percentage of unique letter
    overlap (set.intersection): 0-1.

    >>> get_match_percent("A single comment.", "A single comment.") # exact match
    1.0
    >>> get_match_percent("A single comment.", "This very different thing to say.") # not a match
    0.0
    >>> round(get_match_percent("A single comment.", "A different comment."), 2) # Close, but not quite - short
    0.67
    >>> s1 = "This is a longer comment about code and what you should and should not do."
    >>> s2 = "Here's a longer comment about what you should not do."
    >>> round(get_match_percent(s1, s2), 2) # Close, but not quite - longer
    0.78
    >>> # TESTING FOR FUNCTION/FILE NAMES
    >>> get_match_percent("AC._match_words", "AutoComplete._match_words()")
    0.8
    >>> get_match_percent("ABCDEFG", "abcdefg")
    1.0
    >>> round(get_match_percent("AC._match_words", "AC._match_words()"), 2)
    0.92
    '''
    # Default:  compare appearance of words
    s1_tkns = set(s1.lower().split()) #lowercase and remove whitespaces
    s2_tkns = set(s2.lower().split())

    if ' ' not in s1 or ' ' not in s2: # No spaces? use letters not words
        s1_tkns = set(list(''.join(s1.split()).lower())) 
        s2_tkns = set(list(''.join(s2.split()).lower()))
    
    percent_common = (len(s2_tkns.intersection(s1_tkns))*2) / (len(s1_tkns) + len(s2_tkns))
    # around the same length of shared tokens?
    return percent_common   

def comments_key(cmnt) -> str:
    """ Key for sorting Comments by filename/function name, if it has one.
    If it doesn't, searches through Comment for one.
    Still can't find one, it returns the Comment's text.

    >>> c = Comment("-- Function name comes later in comment, frequency()", False, 0)
    >>> comments_key(c)
    'frequency()'
    >>> c = Comment("   ~ match_words(): something something", False, 3)
    >>> comments_key(c)
    'match_words()'
    >>> c = Comment("++ Filename appears at end AutoComplete.py", False, 0)
    >>> comments_key(c)
    'AutoComplete.py'
    >>> c = Comment("  - FreqWord.py: filename first", False, 2)
    >>> comments_key(c)
    'FreqWord.py'
    """
    if cmnt.filename:
        return cmnt.filename
    else:
        for term in cmnt.text.split():
            if gom_utils.get_file_extension(term) or gom_utils.is_function_name(term):
                return term
        return cmnt.text 

    

#############################
###         main()        ###
#############################
if __name__ == '__main__':
    ''' Testing our GradeSheet object read-in from file
    '''
    """
    print("-=-=- EMPTY -=-=-")
    test1 = GradeSheet.parse_gradesheet_fromfile('test/GradeSheet-new.txt')
    print(test1)

    print("-=-=- COMPLETED -=-=-")
    test2 = GradeSheet.parse_gradesheet_fromfile('test/GradeSheet-filled.txt')
    print(test2)

    print("-=-=- FILENAMES -=-=-")
    test3 = GradeSheet.parse_gradesheet_fromfile('test/GradeSheet-filenames.txt')
    print(test3)

    print("-=-=- FORMAT FILENAMES -=-=-")
    test2 = GradeSheet.parse_gradesheet_fromfile('test/GradeSheet-fixprettify.txt')
    print(test2)

    print("-=-=- MIX OF NO SUB REQUIREMENTS -=-=-")
    test2 = GradeSheet.parse_gradesheet_fromfile('test/GradeSheet-mixsubreqs.txt')
    print(test2)

    print("-=-=- NO SUB REQUIREMENTS -=-=-")
    test2 = GradeSheet.parse_gradesheet_fromfile('test/GradeSheet-nosubreq.txt')
    print(test2)

    print("-=-=- LIDA STYLE COMMENTS -=-=-")
    test2 = GradeSheet.parse_gradesheet_fromfile('test/GradeSheet-lida.txt')
    print(test2)
    """
    print("-=-=- LIDA STYLE MID COMMENTS -=-=-")
    test2 = GradeSheet.parse_gradesheet_fromfile('test/GradeSheet-lidamid.txt')
    print(test2)

    

    print("-=-=- Doctests of basic functions -=-=-")
    import doctest
    doctest.testmod()

    # TODO: look a this example: 'Good work! Very neat and readable code. Slight error in utc_day function; returns negative values'

