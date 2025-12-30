# Grade-O-Matic 1999

The Grade-O-Matic 1999 enables grading CS1 assignments with keyboard shortcuts and clicks of buttons. 

## Data Model

While the code package may include various classes for parsing and creating objects to represent the GradeSheet or Rubric, the current design does not default to using objects to represent these, instead relying on the text files. You must save the GradeSheet or Rubric to keep any changes! You can edit the GradeSheet text area, and it will be saved as-is to file (if you choose to save). 

When you choose to `prettify` the GradeSheet it does go through the comments and parse them according to some rules: looks for bullets or code denotations, indents subsequent lines appropriately, looks at first 3 terms of comment for file/function name if one isn't specified, etc.

A **large** exception to this is when you want to retroactively change a comment through previously graded GradeSheets in the Rubric-O-Matic : this feature goes through all GradeSheets and parses them with the GradeSheet parser, pretty-formatting all GradeSheets it modifies.

## Running the Grade-O-Matic 1999

The main file you'll need to run is `CS1GradeOmatic.py`. All constant values that you're likely to edit (such as default directories, etc.) are located in `CS1GradeOmaticUtils.py`. 

> **Note**
> Any error or status messages will appear at the top of the window, right under the CS1 Grade-O-Matic 1999 title, and will also be printed to Terminal.

### Basic Set-up
The basic steps for using the Grade-O-Matic 1999 are as follows:

1. The default grading directory specified in `CS1GradeOmaticUtils.py` expects a 'grading-CS1' directory in your home directory. Your life will be better if you set-up a grading folder (or symlink) to grading-CS1 in that location. It's best to be in the same directory as the `CS1GradeOmatic.py` file (i.e., the `gradeomatic/` directory) for default directory set-up.
1. `python3 CS1GradeOmatic.py`
1. Select a filepath for the rubric, either by typing it into the `Filepath to Rubric` text entry, or using the `Search` to select one. Then `Load the Rubric.` The default rubric filepath is currently set-up so you only need change the filename with the appropriate number. The Rubric should load on the right.
1. Select a filepath for the Lab Directory, either by typing it into the `Lab Directory to open student dirs` text entry, or using the `Search Labdir` to select one. This should be a Lab-level directory, not a student-level directory. If you wish to start in the middle of a set of student subdirectories, you can specify that in the `Student Dir` text entry. 
1. Be sure to check the file types you'd like your system to open (in most cases, this is just `.py` and `.txt`). The `pre-prettify` check-box will auto-format the comments section upon loading.
1. Then `Load Files`. You should now have both a GradeSheet.txt on the left, and a Rubric with buttons on the right.

### Grading

> **Note**
> The `Undo last comment` feature is not super robust to wonky formatting, but you can always modify the GradeSheet through its text area in the Grade-O-Matic.

1. Press rubric buttons (or use keyboard shortcuts) to append that comment to the end of the GradeSheet. 
1. If you don't like spacing or wording, you can directly edit the GradeSheet.txt as displayed in the Grade-O-Matic 1999. 
1. You may also add open text to the bottom of the rubric, and clicking the `Add` button will append that open text to the bottom of the GradeSheet. If you'd like to make the open text part of the official rubric, you can `Save Rubric` and then `Load Rubric` for it to display appropriately as buttons.
1. The GradeSheet text area has its own set of buttons for convenience. Underneath the text area to the left are buttons that will modify bullets of the Requirements section: one to convert all asterisks to minuses or plus signs, and another to convert all grade indicators to asterisks. Underneath the text area to the right are buttons that modify the grader comments: 
   2. `Sort` will prettify and sort the comments based upon the filename followed by text.
   2. `+-*>~` converts all comment bullets to a tilde.
   2. The `Prettify` button will go through the comments section and apply consistent formatting. If you have pre-formatted code comments, you can keep your original formatting by placing a ` left apostrophe at the beginning/end of the code block.
   2. There is also a `Grade:` button, which will move your cursor to the `Grade:` line in the GradeSheet. There is a keyboard shortcut for this, as well as for moving the cursor to the Comments section. 

> **Warning**
> Rubric buttons will only ever *append* to the end of the GradeSheet. It always ignores cursor location!

### Completion
When the GradeSheet is edited to your satisfaction, you should `Save & Prev` to save edits and have the Grade-O-Matic move to the previous student directory (this lets you begin with the TA's best grading, and move backwards). This will require you to start your grading at the _last_ directory and move backwards. Alternatively, if you start at the _beginning_ of your Labs to grade, you can opt for `Save & Next`. 

## Keyboard Shortcuts

A number of keyboard shortcuts are available for use in the Grade-O-Matic 1999:

<table>
<tr><td><em>Shortcut</em></td><td><em>Behavior</em></td></tr>
<tr><td>Ctrl-x</td><td>Exit without saving the loaded GradeSheet.txt</td></tr>
<tr><td>Ctrl-s</td><td>Save the loaded GradeSheet.txt</td></tr>
<tr><td>Ctrl-w</td><td>Move to _next_ student subdirectory without saving the loaded GradeSheet.txt</td></tr>
<tr><td>Ctrl-p</td><td>Move to _previous_ student subdirectory without saving the loaded GradeSheet.txt</td></tr>
<tr><td>Ctrl-f</td><td>Prettify format the comments in the loaded GradeSheet.txt</td></tr>
<tr><td>Ctrl-z</td><td>Remove the last comment added to the GradeSheet</td></tr>
<tr><td>Ctrl-Shift-Z</td><td>Re-add the last removed comment</td></tr>
<tr><td>Ctrl-Shift-G</td><td>Place the cursor on the Grade: line in the GradeSheet</td></tr>
<tr><td>Ctrl-Shift-C</td><td>Place the cursor on the Comments... line in the GradeSheet</td></tr>
<tr><td>Ctrl-Shift-E</td><td>Place the cursor at the end of the GradeSheet</td></tr>
<tr><td>Enter while in a directory text entry</td><td>Will Load the directory, or the rubric depending on context</td></tr>
<tr><td>Ctrl-#</td><td>Number is 1, 2, ...0 representing each of the first 10 rubric comments to append to the end of the GradeSheet</td></tr>
<tr><td>Ctrl-Shift-#</td><td>Number is 1, 2, ...0 representing each of the first 10 open comments to append to the end of the GradeSheet</td></tr>
<tr><td>Mousewheel</td><td>Scrolls up and down</td></tr>
</table>

## Rubric-O-Matic 1999
From the Grade-O-Matic 1999, once you've loaded a Rubric, you can modify that Rubric using the Rubric-O-Matic 1999 accessible via the `Modify Rubric` button. This will open a new window with all existing items in the loaded rubric as editable text entries. You can remove (`Clr`) or `Revert` any changes you made back to the initially loaded original. You can also add new comments. Be sure to save the rubric, if you want to use those edits. To load your edited Rubric, you'll need to select its filepath and `Load Rubric` in the Grade-O-Matic 1999 just as you did at initial start-up of the program.

> **Warning**
> Keep track of the filename you've saved your Rubric to! If you change it in the Rubric-O-Matic 1999, you'll want the rubric filepath to match in the Grade-O-Matic 1999 so that you can load your changes.

### Retro-activate
The Retro-activate feature in the Rubric-O-Matic 1999 allows you to change a previous rubric comment through a specified a range of GradeSheets. It parses every GradeSheet it encounters, and so it will _prettify_ every GradeSheet it _modifies_. It first does an _exact match_ search, replacing every exact match with the updated comment. If it did not find an exact match in the current GradeSheet, it'll proceed to look for a _loose match_ and replace the entire comment if it finds one, but once a single loose match is found, it moves to the next GradeSheet. GradeSheets are only updated through the parser and written to file if a match (either exact or loose) is found, and if the "edits" don't result in more than fifty percent character loss (crude error catching). 

This feature is the only feature that modifies more than a single GradeSheet at a time, making it the only "dangerous" feature where you might lost significant work! `git commit` before you try this! 

## Parsing

### Suggested GradeSheet.txt Format

Below is an example of a rather complex `GradeSheet.txt` that the Grade-o-matic should be able to parse. This includes an upper rubric that has requirements and optional sub-requirements; a grade with a + or -; bulleted, [optional] nested comments; and [optional] pre-formatted code segments. Grade-O-matic is robust to some differences in GradeSheet comment styles, but cannot handle far-off examples.

```   
GRADE SHEET FOR CS1 LAB ("Retroshop"):
     
Requirements of this lab:
   ~ Correctly implements the function flip_horizontal
   + Correctly implements the function flip_vertical
   +/~ Correctly implements the function invert
   + Correctly implements the function transform_image 
   ~ Correctly implements the green_screen function     
   1. day_of_week(day)
     + Computes correctly
     + Makes appropriate use of conditionals 
   +/~ Comments are appropriately used to explain hard-to-follow logic
   + Passes our tests

Grade:   A-

Comments from Graders: 
+ Good job! 
+ Code passes all tests
* general
   ~ the list comprehensions used to initialize the new_images are a complex
   technique that have not been taught in this class - it's a good idea to
   demonstrate a solid understanding of the concepts that have been presented 
   in class rather than using other approaches that have not yet been covered
   - docstrings (inside the """/""") should not be removed and should always be 
   sandwiched between the function header and the code
   ~ add brief, succinct comments preceding each logical block of code; these are
   denoted with the # sign
         `
         def flip_horizontal(image):
            new_image = []
            for row in image:
               new_image = new_image + [row[::-1]]
            return new_image
         
         def flip_vertical(image):
            return image[::-1]
`

   ~ In python there are two approaches to for loops --> 
      (1) use range and iterate over indices (which is necessary in green_screen
         because knowing the index makes it possible to loop through two images
         simultaneously)
      (2) directly iterate over the elements if index location is not relevant 
         * this is the more efficient approach for all the other retroshop functions
         and would eliminate the need for the for loop that initializes each
         element in the new_image with empty lists
* flip_horizontal & flip_vertical
   ~ fewer loops are needed if list slicing is used
```