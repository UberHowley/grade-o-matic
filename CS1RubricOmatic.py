''' 
The CS1RubricOmatic allows for light, retro-active modification of
a CS1 Rubric mid-grading while using the CS1 Grade-O-Matic

Held together by duct tape & if-loops by Iris Howley (2023)
'''

import tkinter as tk # abbrev
from tkinter import messagebox as mb
from tkinter import filedialog as fd
import os
from CS1Rubric import Rubric
import CS1GradeOmaticUtils as gom_utils
from CS1GradeSheet import GradeSheet as gs

class RubricOmatic(tk.Frame):
    # constants
    SW_TITLE = 'CS1 RUBRIC-O-MATIC 1999'
    WINDOW_WIDTH = int(gom_utils.WINDOW_WIDTH*(2/3))
    WINDOW_HEIGHT = gom_utils.WINDOW_HEIGHT

    __slots__ = ['rubric', 'custom_cmts', 'loaded_cmts', 'entriesframe', 'rubric_entries']
    __slots__ += ['entry_rubpath', 'btn_saverub']
    __slots__ += ['all_subdirs', 'entry_subdir_start', 'entry_subdir_end']

    def __init__(self, rubric, custom_comments, all_subdirectories, save_as:str, parent=None):
        # Not entirely sure what this code does
        # src: https://pythonbasics.org/tkinter-button/
        tk.Frame.__init__(self, parent)        
        self.parent = parent
        # widget can take all window
        self.pack(fill=tk.BOTH, expand=1)

        self.all_subdirs = all_subdirectories # need to know filepath for retroactive replacement

        #############################
        ###   KEYBOARD SHORCUTS   ###
        parent.bind('<Control-x>', self.nosave_exit) # exit
        parent.bind('<Control-s>', self.save_overwrite) # save
        parent.bind('<Control-o>', self.select_rubric) # search for file name

        #############################
        ###    GUI POSITIONING    ###
        # shouldn't have to modify this
        titleframe = tk.Frame(self)
        titleframe.pack(side=tk.TOP)
        subtitleframe = tk.Frame(self)
        subtitleframe.pack(side=tk.TOP)
        rubtitlesframe = tk.Frame(self)
        rubtitlesframe.pack(side=tk.TOP, fill=tk.X)
        self.entriesframe = tk.Frame(self)
        self.entriesframe.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        bottomframe = tk.Frame(self)
        bottomframe.pack(side=tk.TOP, fill=tk.X, expand=1)        

        #############################
        ###      GUI CONTENT      ###

        ###     Title     ###
        lbl_title = tk.Label(titleframe, text=RubricOmatic.SW_TITLE, font=gom_utils.FONT_TITLE)  
        lbl_title.pack(side=tk.TOP)

        ###     Subtitle     ###
        lbl_subtitle = tk.Label(subtitleframe, text="You'll need to manually Re-Load the rubric file in the Grade-O-Matic after editing here.", anchor=tk.N, font=gom_utils.FONT_H2)  
        lbl_subtitle.pack(side=tk.TOP)

        ###     Top Error Message     ###
        self.lbl_error = tk.Label(titleframe, text='', fg=gom_utils.RED, font=gom_utils.FONT_H1, anchor='w')  
        self.lbl_error.pack(side=tk.TOP)

        ###     Rubric Entries Titles   ###
        lbl_rub_cmt = tk.Label(rubtitlesframe, text='Comment', font = gom_utils.FONT_H2)
        lbl_rub_cmt.pack(side=tk.LEFT, expand=1, fill=tk.BOTH) 
        lbl_rub_retro = tk.Label(rubtitlesframe, text='Retro-activate', font = gom_utils.FONT_H2)
        lbl_rub_retro.pack(side=tk.RIGHT) 
        lbl_rub_rev = tk.Label(rubtitlesframe, text='Revert', font = gom_utils.FONT_H2)
        lbl_rub_rev.pack(side=tk.RIGHT) 
        lbl_rub_rm = tk.Label(rubtitlesframe, text='Clear', font = gom_utils.FONT_H2)
        lbl_rub_rm.pack(side=tk.RIGHT) 

        rubentrframe = tk.Frame(self.entriesframe)
        rubentrframe.pack(side=tk.TOP) 

        # Nav Button Frame
        nav_btn_frame = tk.Frame(bottomframe)
        nav_btn_frame.pack(side=tk.LEFT) 
        subdir_frame = tk.Frame(bottomframe)
        subdir_frame.pack(side=tk.RIGHT)

        ###     Rubric Directory     ###
        rubricdirframe = tk.Frame(nav_btn_frame)
        rubricdirframe.pack(side=tk.LEFT)
        
        lbl_rubdir = tk.Label(rubricdirframe, text='Save As: ', anchor='w')
        lbl_rubdir.pack(side=tk.LEFT)
        self.entry_rubpath = tk.Entry(rubricdirframe, width=gom_utils.ENTRY_LG)
        self.entry_rubpath.insert(0, save_as)
        # Find a better way to pass the directory name back and forth?
        #self.entry_rubpath.configure(state= tk.DISABLED)
        self.entry_rubpath.pack(side=tk.LEFT)
        # Find a better way to pass the directory name back and forth?
        btn_searchrub = tk.Button(rubricdirframe, text='Search', command=self.select_rubric)
        btn_searchrub.pack(side=tk.LEFT) 

        ###     Nav Buttons    ###        
        btn_save_exit = tk.Button(nav_btn_frame, text='Save & Exit', command=self.save_exit)
        btn_save_exit.pack(side=tk.LEFT) 
        btn_nosave_exit = tk.Button(nav_btn_frame, text='Cancel', command=self.nosave_exit)
        btn_nosave_exit.pack(side=tk.LEFT) 

        ###   Sub Dir Select   ###
        lbl_stardir = tk.Label(subdir_frame, text='Start: ', anchor='w')
        lbl_stardir.pack(side=tk.LEFT)
        self.entry_subdir_start = tk.Entry(subdir_frame, width=gom_utils.ENTRY_SM)
        self.entry_subdir_start.pack(side=tk.LEFT) 
        self.entry_subdir_start.insert(0, gom_utils.get_filename(self.all_subdirs[0])) # default start subdir

        lbl_enddir = tk.Label(subdir_frame, text='End: ', anchor='w')
        lbl_enddir.pack(side=tk.LEFT)
        self.entry_subdir_end = tk.Entry(subdir_frame, width=gom_utils.ENTRY_SM)
        self.entry_subdir_end.pack(side=tk.RIGHT) 
        self.entry_subdir_end.insert(0, gom_utils.get_filename(self.all_subdirs[-1])) # default end subdir

        ###     Rubric     ### 
        self.rubric = rubric
        self.custom_cmts = custom_comments
        self.load_rubric()
        
    #############################
    ###    INSTANCE METHODS   ###
    def load_rubric(self):
        ''' Loads a rubric, using the filename passed to initializer
        Turns each rubric criterion into an editable text entry, with a button for retroactively
        modifying previously graded assignments with the update.
        '''
        self.status_clear()
  
        # clear out previous Rubric
        for widgets in self.entriesframe.winfo_children():
            widgets.destroy()

        # add the saved rubric comments
        self.rubric_entries = [] # stores the strings for each rubric entry at load time
        self.loaded_cmts = [] # stores history of all comments
        rm_btns = [] # remove this comment when we save the rubric
        retro_btns = [] # retroactively change previous graded assignments
        rvrt_btns = [] # button to revert to original status


        for i in range(len(self.rubric.criteria)): 
            crit = self.rubric.criteria[i]
            
            critframe = tk.Frame(self.entriesframe)
            critframe.pack(side=tk.TOP,fill=tk.BOTH, expand=1)

            crit_txt = crit[0]
            if len(crit) == 3:
                crit_txt = crit[0] + gom_utils.RUBRIC_SPACING + crit[1] + gom_utils.RUBRIC_SPACING + crit[2]
            self.loaded_cmts.append(crit_txt) # store what text we loaded
            self.rubric_entries.append(tk.Entry(critframe, justify=tk.LEFT, font=gom_utils.FONT_RUBRIC))
            self.rubric_entries[-1].insert(0, crit_txt)
            self.rubric_entries[-1].pack(side=tk.LEFT,fill=tk.BOTH, expand=1) 

            # rm, revert, replace
            rm_btns.append(tk.Button(critframe, text='Clr', command=lambda i=i: self.remove_comment(i)))
            rm_btns[-1].pack(side=tk.LEFT)
            rvrt_btns.append(tk.Button(critframe, text='Revert', command=lambda i=i: self.revert_comment(i)))
            rvrt_btns[-1].pack(side=tk.LEFT)
            #state=tk.DISABLED, 
            retro_btns.append(tk.Button(critframe, text='Replace', command=lambda i=i: self.replace_comment(i)))
            retro_btns[-1].pack(side=tk.LEFT)      

        # header for new comments
        lbl_custom_header = tk.Label(self.entriesframe, text='Add New', fg='#666', font = gom_utils.FONT_H2)
        lbl_custom_header.pack(side=tk.TOP,fill=tk.BOTH, expand=1) 

        # add open/custom comments
        newrubframe = tk.Frame(self.entriesframe)
        newrubframe.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        for i in range(gom_utils.NUM_CUSTOM_COMMENTS):
            newcmtframe = tk.Frame(newrubframe)
            newcmtframe.pack(side=tk.TOP,fill=tk.BOTH, expand=1)
            self.rubric_entries.append(tk.Entry(newcmtframe, font=gom_utils.FONT_RUBRIC))
            # text from previous new comments, if it exists
            if i < len(self.custom_cmts) and self.custom_cmts[i]: # stay in range and ignore empties
                self.loaded_cmts.append(self.custom_cmts[i])
                self.rubric_entries[-1].insert(0, self.custom_cmts[i])
            self.rubric_entries[-1].pack(side=tk.LEFT,fill=tk.BOTH, expand=1)

            # rm, revert, replace
            rm_btns.append(tk.Button(newcmtframe, text='Clr', command=lambda i=i: self.remove_comment(i+len(self.rubric.criteria))))
            rm_btns[-1].pack(side=tk.LEFT)
            rvrt_btns.append(tk.Button(newcmtframe, text='Revert', command=lambda i=i: self.revert_comment(i+len(self.rubric.criteria))))
            rvrt_btns[-1].pack(side=tk.LEFT)
            # state=tk.DISABLED, 
            retro_btns.append(tk.Button(newcmtframe, text='Replace', command=lambda i=i: self.replace_comment(i+len(self.rubric.criteria))))
            retro_btns[-1].pack(side=tk.LEFT) 

    #############################
    ###   BTN EVENT HANDLERS  ###
    def replace_comment(self, ind:int): 
        ''' Goes back through all prev graded students and
        updates their GradeSheet to have this version of the comment
        rather than the originally loaded one.
        '''
        self.status_clear() # clear status messages 

        # ERROR CHECKING - basic
        if not len(self.all_subdirs):
            self.status('!', "No student subdirectories to retroactively replace!")
            return 
        elif ind >= len(self.loaded_cmts):
            self.status('ERROR', "Index for reverting comment did not exist at load time.")

        # ERROR CHECKING - start/end sub directories
        # set some defaults in case they're empty
        if not self.entry_subdir_start.get(): # empty start dir
            self.entry_subdir_start.insert(0, gom_utils.get_filename(self.all_subdirs[0])) # default start subdir
        if not self.entry_subdir_end.get(): # empty end dir
            self.entry_subdir_end.insert(0, gom_utils.get_filename(self.all_subdirs[-1])) # default end subdir
        startdir = self.entry_subdir_start.get()
        enddir = self.entry_subdir_end.get()
        # Checking that these subdirs exist in our list from Grade O Matic
        valid_start_subdir = False
        valid_end_subdir = False
        selected_subdirs = []
        for sd in self.all_subdirs:
            if not valid_start_subdir  and startdir == gom_utils.get_filename(sd): # catch only first stardir
                valid_start_subdir = True
            if valid_start_subdir and enddir == gom_utils.get_filename(sd): # enddir comes after startdir
                valid_end_subdir = True
                selected_subdirs.append(sd) # catch the last one
            elif not valid_start_subdir and enddir == gom_utils.get_filename(sd):
                self.status('WARNING', "Ending subdirectory needs to come after startdir:", startdir, '-', enddir)
                return
            if valid_start_subdir and not valid_end_subdir: # keep track of subdirs we want to use
                selected_subdirs.append(sd)
        if not valid_start_subdir:
            self.status('WARNING', "Starting subdirectory not in our current subdirs:", startdir)
            return
        elif not valid_end_subdir:
            self.status('WARNING', "Ending subdirectory not in our current subdirs:", enddir)
            return

        # Capture replacements
        former_cmnt = self.loaded_cmts[ind]
        new_cmnt = self.rubric_entries[ind].get()

        # Confirm retroactive replacement
        fp = gom_utils.get_filepath(selected_subdirs[0])
        msg = "Are you sure you want to RETROACTIVELY REPLACE "
        msg += "\n'" + former_cmnt + "'\nwith\n'" + new_cmnt + "'\n" 
        msg += "in the following GradeSheets? " + '\n'
        msg += fp + ' :: ' + startdir + ' - ' + enddir
        msg += "\n(This isn't the most robust feature...)"
        do_replace = mb.askyesno("Confirm Retroactive Replacement", msg) 
        if not do_replace:
            return
        
        # Do the retroactive replacement
        for filepath in selected_subdirs:
            # iterate over files
            print("RubricOmatic:: replace_comment: Retroactivating:", gom_utils.get_filename(filepath))
            fname  = gom_utils.format_filename(filepath, gom_utils.FILENAME_GS)
            try:                    
                # Convert gs_str to GradeSheet object
                gradesheet = gs.parse_gradesheet_fromfile(fname)
                len_gs_orig = len(str(gradesheet))
                '''
                if('10' in filepath): # selective debug printing 
                    print('*'*25, "AFTER PARSING", '*'*25)
                    print(gradesheet)
                '''
                found = gradesheet.replace_comment(former_cmnt, new_cmnt) # find former_cmnt, replace with new_cmnt
                len_gs_mod = len(str(gradesheet))
                '''
                if('10' in filepath):  # selective debug printing 
                    print('*'*25, "AFTER REPLACING", '*'*25) 
                    print(gradesheet)
                '''
                # only write file if we actually modified it
                # and don't have *significant* data loss
                # currently operationalized as more than 50% character loss
                if found and len_gs_orig//2 < len_gs_mod: 
                    gradesheet.write_file(fname) 

            except FileNotFoundError:
                self.status('!', filepath+ " does not have a " + gom_utils.FILENAME_GS )

        mb.showinfo("Retroactive Replacement Complete", "Retroactive replacement for criteria " + str(ind) + " is complete.")                       


    def remove_comment(self, ind:int): 
        ''' Clears the comment at the given location in the rubric o matic.
        '''
        self.status_clear() # clear status messages 

        #orig_num_rubcmts = self.rubric.criteria
        self.rubric_entries[ind].delete(0,tk.END)            

    def revert_comment(self, ind:int): 
        ''' Returns the comment at the given index (ind) to its
        original text when it was loaded.
        '''
        self.status_clear() # clear status messages 

        self.rubric_entries[ind].delete(0,tk.END)

        if ind < len(self.loaded_cmts): 
            self.rubric_entries[ind].insert(0, self.loaded_cmts[ind])
        else:     # just revert it to blank
            self.rubric_entries[ind].insert(0, '')            

    def select_rubric(self, event=None):
        ''' Opens a file dialog to select a rubric file to parse.
        '''
        self.status_clear() # clear status messages 

        # Grab the directory entry text to see where to start the search
        init_dir = '.'
        if len(self.entry_rubpath.get()) > 3:
            init_dir = self.entry_rubpath.get()

        rubric_fname = fd.askopenfilename(title='Open a Rubric File', initialdir=init_dir)
        # Use original fname if nothing was selected
        if rubric_fname and len(rubric_fname > 3):
            self.entry_rubpath.delete(0, tk.END)
            self.entry_rubpath.insert(0, rubric_fname)

    ##################################
    ### BOTTOM NAVBAR BTN HANDLERS ###
    def save_overwrite(self, event=None):
        ''' Will overwrite existing rubric at the given location with whatever is in
        the Rubric-O-Matic.
        '''
        self.status_clear() # clear status messages 

        entries = [cmt_entry.get() for cmt_entry in self.rubric_entries if len(cmt_entry.get())>3]
        new_rubric = self.rubric
        try:
            new_rubric = Rubric(entries)
        except:
            self.status('ERROR', "Cannot save rubric.")
            return
        self.rubric= new_rubric
        self.rubric.overwrite(self.entry_rubpath.get())
        

    def nosave_exit(self, event=None):
        ''' Exits the RubricOmatic without saving the current rubric.
        '''
        self.parent.destroy()

    def save_exit(self):
        ''' Saves current modifications to Rubric and then closes the RubricOmatic
        '''
        self.save_overwrite()
        self.nosave_exit()
    
    #############################
    ###     ERROR METHODS     ###
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
        print('RubricOmatic::', msg)

    def status_clear(self):
        ''' Clears out whatever text is in the error label.
        '''
        self.lbl_error.configure(text='')   

#############################
###         main()        ###
#############################
if __name__ == '__main__':
    f1 = 'test/rubric02.csv'
    #f1 = 'test_rubricomatic2.csv'    
    r1 = Rubric(Rubric.parse_rubric_from_file(f1))

    root = tk.Tk()
    app = RubricOmatic(r1, ['custom1', '++ trying something'], [gom_utils.DEFAULT_DIR+'/dir1', gom_utils.DEFAULT_DIR+'/dir2'], f1, root)
    root.title(RubricOmatic.SW_TITLE)
    root.geometry(str(RubricOmatic.WINDOW_WIDTH)+'x'+str(RubricOmatic.WINDOW_HEIGHT))
    root.mainloop()