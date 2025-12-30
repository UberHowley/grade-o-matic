''' 
The CS1GradeOmatic module is the top module for grading CS1 Laboratory
Assignments using this software.

Held together by duct tape & if-loops by Iris Howley (2023)
'''

import tkinter as tk # abbrev
from tkinter import filedialog as fd
import os, re
from CS1Rubric import *
from CS1GradeSheet import GradeSheet, Comment
from CS1RubricOmatic import RubricOmatic
import CS1GradeOmaticUtils as gom_utils
from VerticalScrollWheel import VerticalScrolledFrame

class GradeOmatic(tk.Frame):
    # ALL SHARED/CHANGEABLE CONSTANT VALUES NOW STORED IN CS1GRADEOMATICUTILS.PY

    # constants
    EMPTY = 'No Directory Loaded'
    SW_TITLE = 'CS1 GRADE-O-MATIC 1999'

    __slots__ = ['entry_dir', 'entry_rubpath', 'entry_start', 'btn_loadfiles', 'btn_modrubric']  
    __slots__ = ['open_cmt_entries']               
    __slots__ += ['lbl_error', 'lbl_currentgrading']
    __slots__ += ['rubric', 'rubgridframe', 'rubric_btns', 'btn_saverub']
    __slots__ += ['chk_py', 'chk_txt', 'chk_img', 'chk_jva', 'chk_prettify']
    __slots__ += ['text_gradesheet', 'stk_redocomments']
    __slots__ += ['current_subdir', 'all_subdirs']

    def __init__(self, parent=None):
        # Not entirely sure what this code does
        # src: https://pythonbasics.org/tkinter-button/
        tk.Frame.__init__(self, parent)        
        self.parent = parent

        # scrolling: https://stackoverflow.com/a/16198198/4730538
        self.frame = VerticalScrolledFrame(parent)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE)

        #############################
        ###   KEYBOARD SHORCUTS   ###
        self.parent.bind('<Control-x>', self.nosave_exit) # exit
        self.parent.bind('<Control-s>', self.save_overwrite) # save
        self.parent.bind('<Control-w>', self.nosave_next) # skip
        self.parent.bind('<Control-p>', self.nosave_prev) # previous
        self.parent.bind('<Control-o>', self.select_directory) # search for file name for the directory
        self.parent.bind('<Control-z>', self.undo_comment) # undo adding comment to gradesheet
        self.parent.bind('<Control-f>', self.prettify) # prettify / format
        self.parent.bind('<Control-Shift-Z>', self.redo_comment) # redo adding comment to gradesheet
        self.parent.bind('<Control-Shift-G>', lambda event: self.insert_section(gom_utils.GRADE_TXT)) # place cursor at Grade: location
        self.parent.bind('<Control-Shift-C>', lambda event: self.insert_section(gom_utils.COMMENT_TXT)) # place cursor at Comments... location
        self.parent.bind('<Control-Shift-E>', lambda event: self.insert_section(tk.END)) # place cursor at end

        #############################
        ###    GUI POSITIONING    ###
        # shouldn't have to modify this
        titleframe = tk.Frame(self.frame.interior)
        titleframe.pack(side=tk.TOP)
        subtitleframe = tk.Frame(self.frame.interior)
        subtitleframe.pack(side=tk.TOP)
        rubricdirframe = tk.Frame(self.frame.interior)
        rubricdirframe.pack(side=tk.TOP)
        directoryframe = tk.Frame(self.frame.interior)
        directoryframe.pack(side=tk.TOP)
        filetypeframe = tk.Frame(self.frame.interior)
        filetypeframe.pack(side=tk.TOP)
        gradingframe = tk.Frame(self.frame.interior)
        gradingframe.pack(side=tk.TOP)
        navbtnframe = tk.Frame(self.frame.interior)
        navbtnframe.pack(side=tk.TOP)        

        #############################
        ###      GUI CONTENT      ###

        ###     Title     ###
        lbl_title = tk.Label(titleframe, text=GradeOmatic.SW_TITLE, font=gom_utils.FONT_TITLE)  
        lbl_title.pack(side=tk.TOP)

        ###     Subtitle     ###
        lbl_subtitle = tk.Label(subtitleframe, text="What can possibly go wrong?!", anchor=tk.N, font=gom_utils.FONT_H2)  
        lbl_subtitle.pack(side=tk.TOP)

        ###     Top Error Message     ###
        self.lbl_error = tk.Label(titleframe, text='', fg=gom_utils.RED, font=gom_utils.FONT_H1, anchor='w')  
        self.lbl_error.pack(side=tk.BOTTOM)

        ###     Rubric Directory     ###
        lbl_rubdir_title = tk.Label(rubricdirframe, text="Rubric Directory", font = gom_utils.FONT_H1, anchor='w')
        lbl_rubdir_title.pack(side=tk.TOP)

        lbl_rubdir = tk.Label(rubricdirframe, text='Filepath to Rubric: ', anchor='w')
        lbl_rubdir.pack(side=tk.LEFT)
        self.entry_rubpath = tk.Entry(rubricdirframe, width=gom_utils.ENTRY_LG)
        # Find default rubric directory
        rub_dir_custom = os.path.abspath(gom_utils.DEFAULT_RUBRICDIR)
        self.entry_rubpath.insert(0, rub_dir_custom)
        self.entry_rubpath.bind('<Return>', self.load_rubric) # 'Enter' keyboard shortcut
        self.entry_rubpath.pack(side=tk.LEFT)
        self.entry_rubpath.xview_moveto(1) # right-aligned view
        btn_searchrub = tk.Button(rubricdirframe, text='Search', command=self.select_rubric)
        btn_searchrub.pack(side=tk.LEFT) 
        btn_rubdir = tk.Button(rubricdirframe, text='Load Rubric', command=self.load_rubric)
        btn_rubdir.pack(side=tk.LEFT) 
        self.btn_saverub = tk.Button(rubricdirframe, text='Save Rubric', command=self.save_rubric, state=tk.DISABLED)
        self.btn_saverub.pack(side=tk.LEFT) 

        ###     Directory     ###
        lbl_dir_title = tk.Label(directoryframe, text="Grading/Lab Directory", font = gom_utils.FONT_H1, anchor='w')
        lbl_dir_title.pack(side=tk.TOP)

        originframe = tk.Frame(directoryframe)
        originframe.pack(side=tk.LEFT)
        lbl_dir = tk.Label(originframe, text="Lab Directory to open student dirs: ", anchor='w')
        lbl_dir.pack(side=tk.LEFT)
        self.entry_dir = tk.Entry(originframe, width=gom_utils.ENTRY_LG)
        # Default grading directory, found programmatically
        username = rub_dir_custom[:rub_dir_custom.find('/', len('/Users/')+1)]
        self.entry_dir.insert(0, username+gom_utils.DEFAULT_DIR)
        self.entry_dir.bind('<Return>', self.choose_directory) # 'Enter' keyboard shortcut
        self.entry_dir.pack(side=tk.LEFT)
        self.entry_dir.xview_moveto(1) # right-aligned view
        btn_searchdir = tk.Button(originframe, text='Search Labdir', command=self.select_directory)
        btn_searchdir.pack(side=tk.LEFT) 

        ###     File types     ###
        lbl_filetypes = tk.Label(filetypeframe, text="File types to open: ", anchor='w')
        lbl_filetypes.pack(side=tk.LEFT)
        self.chk_py = tk.IntVar()
        ck_py = tk.Checkbutton(filetypeframe, text='.py',variable=self.chk_py)
        ck_py.select() # .py is default selected
        ck_py.pack(side=tk.LEFT)
        self.chk_txt = tk.IntVar()
        ck_txt = tk.Checkbutton(filetypeframe, text='.txt',variable=self.chk_txt)
        ck_txt.select() # txt is default selected
        ck_txt.pack(side=tk.LEFT)
        self.chk_img = tk.IntVar()
        ck_img = tk.Checkbutton(filetypeframe, text='img',variable=self.chk_img)
        ck_img.pack(side=tk.LEFT)
        self.chk_jva = tk.IntVar()
        ck_jva = tk.Checkbutton(filetypeframe, text='.java',variable=self.chk_jva)
        ck_jva.pack(side=tk.LEFT)
        
        self.chk_prettify = tk.IntVar()
        ck_prettify = tk.Checkbutton(filetypeframe, text='pre-prettify',variable=self.chk_prettify)
        ck_prettify.select() # prettify is default selected
        ck_prettify.pack(side=tk.LEFT)

        ###     Start With     ###
        startframe = tk.Frame(directoryframe)
        startframe.pack(side=tk.RIGHT)
        lbl_start = tk.Label(startframe, text="Student Dir to start with: ", anchor='w')
        lbl_start.pack(side=tk.LEFT)
        self.entry_start = tk.Entry(startframe, width=gom_utils.ENTRY_SM)
        self.entry_start.bind('<Return>', self.choose_directory) # 'Enter' keyboard shortcut
        self.entry_start.pack(side=tk.LEFT)
        btn_searchsubdir = tk.Button(startframe, text='Search Studir', command=self.select_subdirectory)
        btn_searchsubdir.pack(side=tk.LEFT) 

        self.btn_loadfiles = tk.Button(startframe, text='Load Files', state=tk.DISABLED, command=self.choose_directory)
        self.btn_loadfiles.pack(side=tk.LEFT) 

        ###     Current Student     ###
        currentframe = tk.Frame(gradingframe)
        currentframe.pack(side=tk.TOP)
        lbl_grade_title = tk.Label(currentframe, text="Currently Grading: ", font = gom_utils.FONT_H1, anchor='w')
        lbl_grade_title.pack(side=tk.LEFT)
        self.lbl_currentgrading = tk.Label(currentframe, text=self.EMPTY, font = gom_utils.FONT_H1, anchor='w')
        self.lbl_currentgrading.pack(side=tk.LEFT)

        ###     GradeSheet     ###
        # https://realpython.com/python-gui-tkinter/#getting-multiline-user-input-with-text-widgets
        gsframe = tk.Frame(gradingframe)
        gsframe.pack(side=tk.LEFT)
        gsareaframe = tk.Frame(gsframe)
        gsareaframe.pack(side=tk.TOP)
        self.text_gradesheet = tk.Text(gsareaframe, width=gom_utils.TEXT_GRADESHEET, height=40)
        self.text_gradesheet.configure(font=gom_utils.FONT_GRADESHEET, state=tk.NORMAL)
        self.text_gradesheet.insert(tk.INSERT, self.EMPTY)
        self.text_gradesheet.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE)
        # GradeSheet: Replacement buttons
        gsbtnsframe = tk.Frame(gsframe)
        gsbtnsframe.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.TRUE)
        btn_rplc_minus = tk.Button(gsbtnsframe, text='* > -', command=lambda : self.replace_bullet('-', '*'))
        btn_rplc_minus.pack(side=tk.LEFT) 
        btn_rplc_plus = tk.Button(gsbtnsframe, text='* > +', command=lambda : self.replace_bullet('+', '*'))
        btn_rplc_plus.pack(side=tk.LEFT) 
        # Rarely ever use these buttons for converting Rubric bullets.
        #btn_rplc_plus = tk.Button(gsbtnsframe, text='~ > +', command=lambda : self.replace_bullet('+', '~'))
        #btn_rplc_plus.pack(side=tk.LEFT) 
        #btn_rplc_tilde = tk.Button(gsbtnsframe, text='* > ~', command=lambda : self.replace_bullet('~', '*'))
        #btn_rplc_tilde.pack(side=tk.LEFT) 
        btn_ret_ast = tk.Button(gsbtnsframe, text='+-~? > *', command=lambda : self.return_asterisk('+-~?'))
        btn_ret_ast.pack(side=tk.LEFT) 

        # Comment buttons               
        btn_grade = tk.Button(gsbtnsframe, text='Grade:', command=lambda : self.insert_section(gom_utils.GRADE_TXT))
        btn_grade.pack(side=tk.RIGHT) 
        btn_prettify = tk.Button(gsbtnsframe, text='Prettify', command=self.prettify)
        btn_prettify.pack(side=tk.RIGHT) 
        btn_cmnt_bullets = tk.Button(gsbtnsframe, text='+-* > ~', command=lambda : self.replace_cmnt_bullet('~', '+-*'))
        btn_cmnt_bullets.pack(side=tk.RIGHT) 
        btn_cmnt_sort = tk.Button(gsbtnsframe, text='Sort', command=self.sort_comments)
        btn_cmnt_sort.pack(side=tk.RIGHT) 
        lbl_commen_btns = tk.Label(gsbtnsframe, text="Comments: ", anchor='w')
        lbl_commen_btns.pack(side=tk.RIGHT)

        ###     Rubric     ###
        rubricframe = tk.Frame(gradingframe)
        rubricframe.pack(side=tk.RIGHT, expand=tk.TRUE)
        header_txt = 'Severity' + gom_utils.RUBRIC_SPACING + 'Filename' + gom_utils.RUBRIC_SPACING + 'Comment'
        lbl_rub_sev = tk.Label(rubricframe, text=header_txt, font = gom_utils.FONT_H2)
        lbl_rub_sev.pack(side=tk.TOP, expand=tk.TRUE)
        self.rubgridframe = tk.Frame(rubricframe)
        self.rubgridframe.pack(side=tk.TOP)        

        ###     Nav Buttons    ###
        btn_save_prev = tk.Button(navbtnframe, text='Save & Prev', command=self.save_prev)
        btn_save_prev.pack(side=tk.LEFT) 
        btn_nosave_prev = tk.Button(navbtnframe, text='Prev', command=self.nosave_prev)
        btn_nosave_prev.pack(side=tk.LEFT) 
        btn_nosave_next = tk.Button(navbtnframe, text='Skip',  command=self.nosave_next)
        btn_nosave_next.pack(side=tk.LEFT) 
        btn_save_next = tk.Button(navbtnframe, text='Save & Next', command=self.save_next)
        btn_save_next.pack(side=tk.LEFT) 
        btn_save_overwrite = tk.Button(navbtnframe, text='Save (Overwrite)', command=self.save_overwrite)
        btn_save_overwrite.pack(side=tk.LEFT) 
        btn_save_exit = tk.Button(navbtnframe, text='Save & Exit', command=self.save_exit)
        btn_save_exit.pack(side=tk.LEFT) 
        btn_nosave_exit = tk.Button(navbtnframe, text='Exit', command=self.nosave_exit)
        btn_nosave_exit.pack(side=tk.LEFT) 

    #############################
    ###   BTN EVENT HANDLERS  ###
    def append_comment(self, cmnt, event=None):
        ''' Appends a comment (Comment) to the gradesheet text entry
        '''
        self.status_clear()
        # Add formatted comment to end of GradeSheet display
        cmnt_str = str(cmnt)
        if GradeSheet.code_loc(cmnt_str) < 0: # not code, format
            cmnt_str = gom_utils.format_comment(cmnt_str)
        
        self.text_gradesheet.insert(tk.END, '\n'+cmnt_str)
        self.text_gradesheet.see(tk.END)  # scroll to bottom of text area
    
    def undo_comment(self, event=None):
        ''' Removes the last added comment from the gradesheet text, if there is one.
        '''
        self.status_clear()

        # indexing isn't really easy with multiline Text objects:
        # https://realpython.com/python-gui-tkinter/#getting-multiline-user-input-with-text-widgets

        # Adding existing comments to the undo comments list
        curr_gs_txt = self.text_gradesheet.get(gom_utils.TEXT_0, tk.END+'-1c')
        comments_line = curr_gs_txt.rfind(gom_utils.COMMENT_TXT)
        start_pos = comments_line + len(gom_utils.COMMENT_TXT+':')
        stk_comments = [] # current comments
        if comments_line >= 0 and start_pos < len(curr_gs_txt) - 5: # at least 5 characters for a meaningful comment 
            crits = GradeSheet.parse_comments_section(curr_gs_txt[start_pos:].rstrip()) # list of Comments (with subcomments)
            stk_comments.extend(crits)

        if len(stk_comments) > 0:
            last_comment = stk_comments[-1]
            if last_comment.subcomments:
                last_comment = last_comment.pop() # last comment is actually a subcomment
            else:
                last_comment = stk_comments.pop()
            
            # remove last comment
            location = curr_gs_txt.rfind(last_comment.comment[:20]) # location of last comment
            location = curr_gs_txt.rfind('\n', 0, location) # newline before last comment
            self.text_gradesheet.delete(gom_utils.TEXT_0, tk.END) # clear gradesheet
            self.text_gradesheet.insert(gom_utils.TEXT_0, curr_gs_txt[: location]) # refill gradesheet
            self.text_gradesheet.see(tk.END)  # scroll to bottom of text area
            # place last comment onto redocomments
            self.stk_redocomments.append(last_comment) # will lose subcomment structure, but shouldn't matter
        else:
            self.status('!', "There aren't any comments from this session to undo!")

    def redo_comment(self, event=None):
        ''' Puts back the last 'undid' comment, if it exists.
        '''
        self.status_clear()

        if len(self.stk_redocomments) > 0:       
            # append_comment will add it back to the appended comments list
            self.append_comment(self.stk_redocomments.pop())     
        else:
            self.status('!', "There aren't any comments from this session to redo!")

    def insert_section(self, section:str, event=None):
        ''' Places cursor in the GradeSheet at the end of where given str (section) appears
        '''
        section = section.rstrip() # more robust space handling
        idx = ''
        if section != tk.END:
            #searches for desired string from index 1
            idx = self.text_gradesheet.search(section, gom_utils.TEXT_0, nocase=1, stopindex=tk.END)
        if idx:              
            #lastidx = '%s+%dc' % (idx, len(section))  #last index sum of current index and length of text        

            if idx.replace(".", "").isnumeric(): #idx is a float
                lastidx = str(int(float(idx))) + '.' + tk.END # place it at end of line
            else:
                lastidx = tk.END+'-1c' # default to placing cursor at the end

            # Special handling for Grade: making sure it has trailing spaces
            if gom_utils.GRADE_TXT.strip() in section:
                # if cursor immediately following a colon, add 3 spaces
                if self.text_gradesheet.get(lastidx+'-1c', lastidx)==gom_utils.GRADE_TXT.strip()[-1]:
                    num_spaces = len(gom_utils.GRADE_TXT)-len(gom_utils.GRADE_TXT.rstrip())
                    self.text_gradesheet.insert(lastidx, num_spaces*' ')
                    lastidx = lastidx.split('.')[0] + '.' + tk.END # place it at [new] end of line

            # place cursor at end of line
            self.text_gradesheet.mark_set(tk.INSERT, lastidx)
            self.text_gradesheet.focus_set() # sets focus to the text area so you can type
         
    def prettify(self, event=None):
        ''' Goes through GradeSheet (after comments section) 
        and attempts to prettify existing comments therein
        '''
        gs_txt = self.text_gradesheet.get(gom_utils.TEXT_0, tk.END+'-1c')
        comment_line = gs_txt.find(gom_utils.COMMENT_TXT)
        # If someone deleted Comments line, put it back in, after Grade:
        if comment_line < 0:
            end_grade_ind = gs_txt.find(gom_utils.GRADE_TXT.strip())
            newline_grade_ind = gs_txt.find('\n', end_grade_ind)
            gs_txt = gs_txt[:newline_grade_ind] + '\n\n' + gom_utils.COMMENT_TXT + '\n' + gs_txt[newline_grade_ind:]
            comment_line = gs_txt.find(gom_utils.COMMENT_TXT)

        new_gs = gs_txt[:comment_line+len(gom_utils.COMMENT_TXT)] # just the gradesheet
        if new_gs[-1] != '\n': # add newline after comment title, if needed
            new_gs += '\n'
        comments_gs = gs_txt[comment_line+len(gom_utils.COMMENT_TXT): ] # just the comments
        comments = GradeSheet.parse_comments_section(comments_gs)
        new_gs = new_gs + '\n'.join([str(c) for c in comments]) 
        self.text_gradesheet.delete(gom_utils.TEXT_0, tk.END)
        self.text_gradesheet.insert(gom_utils.TEXT_0, new_gs)
        self.text_gradesheet.see(tk.END)  # scroll to bottom of text area

    def sort_comments(self, event=None):
        ''' Goes through comments section and sorts based upon filename/functionname
        or comment itself. No fname? Goes first.
        '''
        gs_txt = self.text_gradesheet.get(gom_utils.TEXT_0, tk.END+'-1c')
        comment_line = gs_txt.rfind(gom_utils.COMMENT_TXT)
        just_gs = gs_txt[:comment_line+len(gom_utils.COMMENT_TXT)] # just the gradesheet
        comments_gs = gs_txt[comment_line+len(gom_utils.COMMENT_TXT): ] # just the comments
        comments = GradeSheet.parse_comments_section(comments_gs)
    
        sorted_cmnts = [str(c) for c in GradeSheet.sort_comments(comments)]

        new_gs = just_gs + '\n' + '\n'.join(sorted_cmnts)
        self.text_gradesheet.delete(gom_utils.TEXT_0, tk.END)
        self.text_gradesheet.insert(gom_utils.TEXT_0, new_gs)
        self.text_gradesheet.focus_set() # sets focus to the text area so you can type

        self.text_gradesheet.see(tk.END)  # scroll to bottom of text area

    def replace_cmnt_bullet(self, ch:str, bullets:str):
        ''' Goes through GradeSheet (after comments section) 
        and replaces leading bullet, any of bullets, to character ch.
        '''
        gs_txt = self.text_gradesheet.get(gom_utils.TEXT_0, tk.END+'-1c')
        comment_line = gs_txt.rfind(gom_utils.COMMENT_TXT)
        just_gs = gs_txt[:comment_line] # just the gradesheet
        comments_gs = gs_txt[comment_line: ] # just the comments
    
        replaced = []
        for line in comments_gs.split('\n'):
            if gom_utils.COMMENT_HEADER not in line and len(line.lstrip()) and line.lstrip()[0] in bullets:
                replaced.append(line.replace(line.lstrip()[0], ch, 1))
            else:
                replaced.append(line)

        new_gs = just_gs + '\n'.join(replaced)
        self.text_gradesheet.delete(gom_utils.TEXT_0, tk.END)
        self.text_gradesheet.insert(gom_utils.TEXT_0, new_gs)
        self.text_gradesheet.focus_set() # sets focus to the text area so you can type

    def replace_bullet(self, ch:str, bullet:str):
        ''' Goes through GradeSheet (prior to comments section) 
        and replaces leading asterisk with given char, ch
        '''
        gs_txt = self.text_gradesheet.get(gom_utils.TEXT_0, tk.END+'-1c')
        comment_line = gs_txt.rfind(gom_utils.COMMENT_TXT)
        just_gs = gs_txt[:comment_line] # just the gradesheet
        comments_gs = gs_txt[comment_line: ] # just the comments
    
        replaced = []
        for line in just_gs.split('\n'):
            if bullet in line and line.lstrip()[0] == bullet:
                replaced.append(line.replace(bullet, ch, 1))
            else:
                replaced.append(line)

        new_gs = '\n'.join(replaced) + comments_gs
        self.text_gradesheet.delete(gom_utils.TEXT_0, tk.END)
        self.text_gradesheet.insert(gom_utils.TEXT_0, new_gs)
        
    def return_asterisk(self, chrs:str):
        ''' Goes through GradeSheet (prior to comments section) 
        and replaces leading bullet (in chrs) with asterisk
        '''
        gs_txt = self.text_gradesheet.get(gom_utils.TEXT_0, tk.END+'-1c')
        comment_line = gs_txt.rfind(gom_utils.COMMENT_TXT)
        just_gs = gs_txt[:comment_line] # just the gradesheet
        comments_gs = gs_txt[comment_line: ] # just the comments
    
        replaced = []
        for line in just_gs.split('\n'):
            if len(line.lstrip()) and line.lstrip()[0] in chrs:
                replaced.append(line.replace(line.lstrip()[0], '*', 1))
            else:
                replaced.append(line)

        new_gs = '\n'.join(replaced) + comments_gs
        self.text_gradesheet.delete(gom_utils.TEXT_0, tk.END)
        self.text_gradesheet.insert(gom_utils.TEXT_0, new_gs)
        

    def choose_directory(self, event=None): 
        ''' Sets up the state of the Grade-O-Matic to be ready to load
        necessary files.
        '''
        self.status_clear()
        directory = self.entry_dir.get()

        # Error handling in directory name
        self.lbl_error.configure(text='') # Clear the error label, in case it has something       
        if '~' in directory: # catch some os.walk nonsense
            self.status('ERROR', "os.walk doesn't like ~ in directory paths: "+directory)
            return

        # Loading new directory, throw out old subdirs!
        self.all_subdirs = []

        for (roots, subdirs, f) in os.walk(directory, topdown=True):
            subdirs.sort()
            for subdir in subdirs:
                if subdir not in gom_utils.IGNORE_DIRS: #ignore some subdirectories
                    # give student subdirs full file path name
                    self.all_subdirs.append(os.path.join(roots, subdir))
            break # only go one level deep into subdirectories

        if len(self.all_subdirs) < 1:
            # Error for empty subdirs      
            self.status('ERROR',"No student subdirectories: "+directory)
            return

        start_subdir = gom_utils.format_filename(directory,self.entry_start.get())
        if len(self.entry_start.get()) > 0 and start_subdir not in self.all_subdirs:
            # Error for starting subdir not in our directories               
            self.status('ERROR', "Specified Student subdir not in dir: "+directory)
            return
        elif len(self.entry_start.get()) > 0:
            # if we've specified a subdir to start at in GUI, use it
            self.current_subdir = start_subdir
        else:
            # just start with the first subdir in the list
            self.current_subdir = self.all_subdirs[0]

        self.load_subdir()

    def load_subdir(self):
        ''' Loads the relevant files from the current subdirectory.
        This typically means opening all .py files for a student, putting
        GradeSheet into GUI, and updating the GUI to reflect current status
        '''
        self.status_clear()  
        self.btn_modrubric['state'] = tk.NORMAL # enable modify rubric button

        # display current student subdir
        if self.current_subdir.endswith(gom_utils.SLASH): # don't want it to end with slash
            self.current_subdir = self.current_subdir[:-1]
        just_subdir = self.current_subdir[self.current_subdir.rfind(gom_utils.SLASH)+1:]
        self.lbl_currentgrading.config(text=just_subdir) # change to current subdir
        # Have 'start with' match 'currently grading'
        self.entry_start.delete(0, tk.END)
        self.entry_start.insert(0, self.lbl_currentgrading.cget('text'))

        # clear out previous GradeSheet
        self.text_gradesheet.delete(gom_utils.TEXT_0, tk.END)

        # clear out previous undo list
        self.stk_comments = []
        self.stk_redocomments = []

        # iterate over files
        for (r2, d2, files) in os.walk(self.current_subdir, topdown=True):
            for fle in files:
                # only file-explorer open specified filetypes
                if (self.chk_py.get() and fle.endswith('.py')) \
                    or (self.chk_jva.get()  and fle.endswith('.java')) \
                    or (self.chk_txt.get()  and fle.endswith('.txt') and not fle.endswith(gom_utils.FILENAME_GS)) \
                    or (self.chk_img.get()  and (fle.endswith('.jpg') or fle.endswith('.png') or fle.endswith('.gif'))) : 
                            
                    # Uses system command to open python files
                    currfile = gom_utils.format_filename(self.current_subdir, fle) 
                    os.system('open '+currfile)

                    # User must manually close each file!!
                    #os.close(currfile)

                # It's the GradeSheet file, let's load it!
                elif fle == gom_utils.FILENAME_GS:
                    gradesheet = gom_utils.read_str_file(gom_utils.format_filename(self.current_subdir, gom_utils.FILENAME_GS))
                    self.text_gradesheet.delete(gom_utils.TEXT_0, tk.END)
                    #self.text_gradesheet.insert(tk.INSERT, self.quick_fix_lab6(str(gradesheet)))
                    self.text_gradesheet.insert(tk.INSERT, str(gradesheet))
                    if self.chk_prettify.get(): # pre-prettify if selected
                        self.prettify() 


    def quick_fix_lab6(self, whole_gs:str) -> str:
        """
        Temporary method for handling GradeSheet formatting that's too wordy
        """
        loc_reqs = whole_gs.lower().find(GradeSheet.REQS_TXT.lower())
        end_reqs = whole_gs.find('\n', loc_reqs) # reqs line end
        loc_grd = whole_gs.lower().find(GradeSheet.GRADE_TXT.lower(), end_reqs)

        txt_reqs = whole_gs[end_reqs : loc_grd]   
        #txt_reqs = '\n'.join([line.rstrip() for line in txt_reqs.split('\n') if len(line.strip()) > 0]) #excessive newlines
        begin = whole_gs[:end_reqs]
        ending = whole_gs[loc_grd:]

        rem = "The function "
        funcs = ["_frequency", "_names"]
        if rem in txt_reqs:
            txt_reqs = txt_reqs.replace(rem,'')
            for f in funcs:
                if f in txt_reqs:
                    txt_reqs = txt_reqs.replace(f, f+"():")
        if "the" in txt_reqs:
            txt_reqs = txt_reqs.replace("the ",'')
        if "our unit tests and" in txt_reqs:
            txt_reqs = txt_reqs.replace("our unit tests and", "unit tests,")
        if "initial letters" in txt_reqs:
            txt_reqs = txt_reqs.replace("initial letters", "initials") 
        return begin + txt_reqs + ending

    def select_directory(self):
        ''' Opens a file dialog for selecting a grading directory
        '''
        self.status_clear()

        # Grab the directory entry text to see where to start the search
        init_dir = '.'
        if len(self.entry_dir.get()) > 3:
            init_dir = self.entry_dir.get()

        # FYI: depending on user settings, initialdir is often ignored!
        dir_fname = fd.askdirectory(title='Open a Grading Directory', initialdir=init_dir)
        # Use original fname if nothing was selected
        if dir_fname and len(dir_fname) > 3:
            self.entry_dir.delete(0, tk.END)
            self.entry_dir.insert(0, dir_fname)

    def select_subdirectory(self):
        ''' Opens a file dialog for selecting a student subdirectory
        (default location is in the main grading directory)
        '''
        self.status_clear()

        # Grab the directory entry text to see where to start the search
        init_dir = '.'
        if len(self.entry_dir.get()) > 3:
            init_dir = self.entry_dir.get()

        # FYI: depending on user settings, initialdir is often ignored!
        subdir_fname = fd.askdirectory(title='Open a Student Directory', initialdir=init_dir)
        if subdir_fname.endswith(gom_utils.SLASH): # don't want it to end with a slash
            subdir_fname = subdir_fname[:-1]
        slash_loc = subdir_fname.rfind(gom_utils.SLASH)
        self.entry_start.delete(0, tk.END)
        self.entry_start.insert(0, subdir_fname[slash_loc+1:])

    def select_rubric(self):
        ''' Opens a file dialog to select a rubric file to parse.
        '''
        self.status_clear()

        # Grab the directory entry text to see where to start the search
        init_dir = '.'
        if len(self.entry_rubpath.get()) > 3:
            init_dir = self.entry_rubpath.get()

        # FYI: depending on user settings, initialdir is often ignored!
        rubric_fname = fd.askopenfilename(title='Open a Rubric File', initialdir=init_dir)
        # Use original fname if nothing was selected
        if len(rubric_fname) > 3:
            self.entry_rubpath.delete(0, tk.END)
            self.entry_rubpath.insert(0, rubric_fname)

        self.entry_rubpath.xview_moveto(1) # right-aligned view

    def load_rubric(self, event=None):
        ''' Loads a rubric, using the filename collected from the GUI.
        Turns each rubric criterion into a button for appending to the gradesheet.
        '''
        self.status_clear()

        if '.csv' not in self.entry_rubpath.get(): # needs to be a CSV
            self.status('ERROR', "Rubric needs to be a ; delimited CSV.")
            return
        
        # update lab directory based on rubric name
        if any(char.isdigit() for char in self.entry_rubpath.get()): # only do this if there's a num in rubric name
            lab_num = re.findall('\d+', self.entry_rubpath.get())[-1] # find the last set of numbers in rubric name
            if lab_num:
                if '/lab' in self.entry_dir.get():
                    self.entry_dir.delete(self.entry_dir.get().rfind('/lab'), tk.END)
                self.entry_dir.insert(len(self.entry_dir.get()), '/lab'+lab_num)


        # clear out previous Rubric
        for widgets in self.rubgridframe.winfo_children():
            widgets.destroy()     

        # add the rubric buttons
        try:            
            self.rubric = Rubric(Rubric.parse_rubric_from_file(self.entry_rubpath.get()))
        except FileNotFoundError:
            self.status('WARNING', "FileNotFoundError: "+str(self.entry_rubpath.get()))
            return
        self.rubric_btns = []
        self.stk_comments = []

        count_crits = 0 # used to generate SHIFT+# keyboard shortcuts
        for crit in self.rubric.criteria: 
            if len(crit) == 3: # it's a criteria
                crit[1] = crit[1]+':' if crit[1] else crit[1]
                crit_txt = crit[0] + gom_utils.RUBRIC_SPACING + crit[1] + gom_utils.RUBRIC_SPACING + crit[2]
                btn_criteria = tk.Button(self.rubgridframe, text=crit_txt, command=lambda crit_txt=crit_txt: self.append_comment(crit_txt), justify=tk.LEFT, wraplength=gom_utils.ENTRY_LG*20, anchor='w', font=gom_utils.FONT_RUBRIC)
                btn_criteria.pack(side=tk.TOP,fill=tk.BOTH, expand=tk.TRUE) 

                # Keyboard SHIFT+# shortcuts
                if count_crits < len(gom_utils.SHIFT_KEYBD_SHORTCUTS): 
                    key_binding = '<'+ gom_utils.RUBRIC_KEYBD + '-Key-'+ str(count_crits)+'>' # use number instead of symbol
                    self.parent.bind(key_binding, lambda event, crit_txt=crit_txt: self.append_comment(crit_txt))
                    count_crits+=1
            elif len(crit) == 1: # it's a header
                lbl_rub_header = tk.Label(self.rubgridframe, text=crit[0], fg='#666', font = gom_utils.FONT_H2)
                lbl_rub_header.pack(side=tk.TOP,fill=tk.BOTH, expand=tk.TRUE) 

        # header for custom comments
        lbl_custom_header = tk.Label(self.rubgridframe, text='Custom', fg='#666', font = gom_utils.FONT_H2)
        lbl_custom_header.pack(side=tk.TOP,fill=tk.BOTH, expand=tk.TRUE) 

        
        # add open/custom comments
        self.open_cmt_entries = []
        comment_btns = []
        openrubframe = tk.Frame(self.rubgridframe)
        openrubframe.pack(side=tk.TOP,fill=tk.BOTH, expand=tk.TRUE)
        count_crits = 1 # used to generate CONTROL+# keyboard shortcuts
        for i in range(gom_utils.NUM_CUSTOM_COMMENTS):
            entry_frame = tk.Frame(openrubframe)
            entry_frame.pack(side=tk.TOP,fill=tk.BOTH, expand=tk.TRUE)
            self.open_cmt_entries.append(tk.Entry(entry_frame))
            self.open_cmt_entries[i].bind('<Return>', lambda event, i=i: self.append_comment(self.open_cmt_entries[i].get())) # 'Enter' keyboard shortcut
            self.open_cmt_entries[i].pack(side=tk.LEFT,fill=tk.BOTH, expand=tk.TRUE)

            # Keyboard CONTROL+# shortcuts
            if count_crits < len(gom_utils.SHIFT_KEYBD_SHORTCUTS): 
                key_binding = '<'+ gom_utils.CMNT_KEYBD + '-'+ gom_utils.SHIFT_KEYBD_SHORTCUTS[count_crits]+'>'
                self.parent.bind(key_binding, lambda event, i=i: self.append_comment(self.open_cmt_entries[i].get()))
                count_crits+=1

            comment_btns.append(tk.Button(entry_frame, text='Add', command=lambda i=i: self.append_comment(self.open_cmt_entries[i].get())))
            comment_btns[i].pack(side=tk.RIGHT) 

        # add an undo button
        rubbtnframe = tk.Frame(self.rubgridframe)
        rubbtnframe.pack(side=tk.TOP,fill=tk.BOTH, expand=tk.TRUE)
        btn_undo = tk.Button(rubbtnframe, text='Undo last comment', command=self.undo_comment)
        btn_undo.pack(side=tk.LEFT)
        btn_redo = tk.Button(rubbtnframe, text='Redo last comment', command=self.redo_comment)
        btn_redo.pack(side=tk.LEFT)
        self.btn_modrubric = tk.Button(rubbtnframe, text='Modify Rubric', command=self.modify_rubric, state=tk.DISABLED)
        self.btn_modrubric.pack(side=tk.RIGHT)
        # If rubric loaded, re-enable 'Load Files' button
        self.btn_loadfiles['state'] = tk.NORMAL
        self.btn_saverub['state'] = tk.NORMAL

    def save_rubric(self):
        ''' Will add the custom/open comments to the rubric file.
        Will need to close and re-open file to see them as buttons rather than entries.
        '''
        self.status_clear()

        if self.rubric:
            for cmt_entry in self.open_cmt_entries:
                if len(cmt_entry.get()) > 3: # don't save empty comments
                    self.rubric.add_criteria(gom_utils.parse_criteria(cmt_entry.get()))
            self.rubric.overwrite(self.entry_rubpath.get())
        else:
            self.status('ERROR', "No rubric loaded, can't save the file!")
        
    def modify_rubric(self):
        # store the current filename, 'cos we need to refresh after
        fname = self.entry_rubpath.get()

        # Get list of strings of comments
        open_crits = []
        for cmnt_entry in self.open_cmt_entries:
            open_crits.append(cmnt_entry.get())

        root = tk.Tk()
        app = RubricOmatic(self.rubric, open_crits, self.all_subdirs, fname, root)
        # TODO: Once you figure out how to pass variables between GUIS::
        # new_filename = ?? # grab new filename from RubricOmatic GUI?
        # Set current rubric filename to the RubricOmatic one: 
        # self.entry_rubpath.delete(0, tk.END)
        # self.entry_rubpath.insert(0, new_filename)
        # Reload/refresh the rubric:

        self.load_rubric()

    ##################################
    ### BOTTOM NAVBAR BTN HANDLERS ###
    def save_overwrite(self, event=None): 
        ''' Saves the current GradeSheet shown in the text entry to file,
        overwrites.
        '''
        self.status_clear()

        gs_txt = self.text_gradesheet.get(gom_utils.TEXT_0, tk.END+'-1c')
        format_root = gom_utils.format_filename(self.entry_dir.get(), self.lbl_currentgrading.cget('text'))
        format_fname = gom_utils.format_filename(format_root,gom_utils.FILENAME_GS)
        gom_utils.write_str_file(gs_txt, format_fname)

    def save_next(self):
        ''' Saves current modifications to GradeSheet and then moves to next student
        directory, loading specified files and new GradeSheet
        '''
        self.status_clear()
        self.save_overwrite()
        self.next()
    def save_prev(self):
        ''' Saves current modifications to GradeSheet and then moves to previous student
        directory, loading specified files and new GradeSheet
        '''
        self.save_overwrite()
        self.nosave_prev()
    def nosave_next(self, event=None):
        ''' Moves to next student directory without saving current changes to GradeSheet
        '''
        self.status_clear()
        self.next()
    def nosave_exit(self, event=None):
        ''' Exits the CS1 Grader without saving the current GradeSheet.
        '''
        self.parent.destroy() 

    def save_exit(self):
        ''' Saves current modifications to GradeSheet and then closes the CS1 Grader
        '''
        self.save_overwrite()
        self.nosave_exit()

    def nosave_prev(self, event=None):
        ''' Goes back to the previous student directory for grading, and opens up *.py files
        as well as loads-in the GradeSheet.txt

        User will have to manually close all *.py files from previous student.
        '''        
        self.status_clear()

        ind_curr_subdir = self.all_subdirs.index(self.current_subdir)
        if  ind_curr_subdir < 1 :
            # Error for being at beginning of student directories!
            self.status('ERROR', "Likely at the beginning of student subdirectories: "+self.current_subdir)
            return
        
        self.current_subdir = self.all_subdirs[ind_curr_subdir-1] # update to the previous subdirectory in our list        
        self.load_subdir() # do the actual setting up of files

    def next(self):
        ''' Moves to next student directory for grading, and opens up *.py files
        as well as loads-in the GradeSheet.txt

        User will have to manually close all *.py files from previous student.
        '''        
        self.status_clear()
        if not self.all_subdirs :
            # Error for not having any subdirectories to load
            self.status('ERROR', "No subdirectories in: "+self.current_subdir)
            return
        ind_curr_subdir = self.all_subdirs.index(self.current_subdir)
        if  ind_curr_subdir>= len(self.all_subdirs)-1 :
            # Error for being at end of student directories!
            self.status('ERROR', "Likely at the end of student subdirectories: "+self.current_subdir)
            return
        
        self.current_subdir = self.all_subdirs[ind_curr_subdir+1] # update to the next subdirectory in our list        
        self.load_subdir() # do the actual setting up of files
    
    #############################
    ###    INSTANCE METHODS   ###

    def status(self, level:str, txt:str):
        ''' Prints an error message to the error status in the GUI
        as well as the terminal
        '''
        if 'ERROR' in level:
            self.lbl_error.configure(fg=gom_utils.RED)
        elif 'WARNING' in level:
            self.lbl_error.configure(fg=gom_utils.ORANGE)
        elif '!' in level:
            self.lbl_error.configure(fg=gom_utils.YELLOW)
        elif '0' in level:
            self.lbl_error.configure(fg=gom_utils.BLACK)
        else:
            self.lbl_error.configure(fg=gom_utils.BLUE)
        msg = level+': '+txt
        self.lbl_error.configure(text=msg)
        print('GradeOmatic::', msg)

    def status_clear(self):
        ''' Clears out whatever text is in the error label.
        '''
        self.lbl_error.configure(text='')   

#############################
###         main()        ###
#############################
if __name__ == '__main__':
    # Setting up scrollbar
    root = tk.Tk()
    root.title(GradeOmatic.SW_TITLE)
    root.geometry(str(gom_utils.WINDOW_WIDTH)+'x'+str(gom_utils.WINDOW_HEIGHT))

    app = GradeOmatic(root)  # probably need to comment this out if scrolling ever works
    
    root.mainloop() # runs the GUI code!