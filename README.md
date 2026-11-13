# DSA103

Repository for the course DSA103 Advanced Chemical Data Science. All course material will be shared here, wheras OLAT will only be used for all course-related communication.

Instructors and persons responsible for the course: Prof. Meredith C. Schuman (meredithchristine.schuman@uzh.ch), Dr. Johannes Schörgenhumer (johannes.schoergenhumer@chem.uzh.ch)

Teaching assistant: Dimitrios Xynos (dimitrios.xynos@chem.uzh.ch)


## Prerequisites
Throughout this course, you will need your personal computer, please bring it to every session. You will use several tools, which have to be installed on your PC (if you have done the DSA101, you might already know some of them). We highly recommend to have your computer set up appropriately before the first lecture:

1) Git/Github: Make sure you have Git installed and a GitHub account. 
2) We will use the package manager uv and its virtual environment (https://docs.astral.sh/uv/). Follow the instructions on the website to install uv. In some cases (on Windows), you will get an error about an ExecutionPolicy. In order to remedy that, open a Power Shell Terminal as administrator and `Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope LocalMachine`. Find out more here: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.5.
3) IDE: For running code and Jupyter notebooks and for facilitating version control, we will be using an IDE. All demonstration will be done in Visual Studio Code, but other development environments, such as Pycharm, work as well. Whatever IDE you are using, make sure that you keep it and its extensions (e.g. for Jupyter and Python) up to date and that you are familiar with the working environment. **In VSCode, you will need extensions for Jupyter and Python installed!**

If anything else is going to be required, you will be notified in due course.

## How to work with this repository
The initial steps:
1) Fork the repository using the Fork button on GitHub.
2) Clone your fork. Please note that folders linked to cloud storage (e.g. OneDrive) can potentially cause issues with the paths. If you experience any warnings or errors in this direction, we recommend moving the files outside of the cloud environment.
3) Create a virtual environment, by running `uv venv` in the terminal (in the IDE).
4) Activate the virtual environment via the terminal (on Windows: `.venv\Scripts\activate`, on Linux/Mac: `source .venv/bin/activate`).
5) Run the command `uv sync` to synchronize the environment with the provided lock file. Any missing dependencies will be thereby installed.
6) Select the Python interpreter from the DSA103 environment (in VSC: click in the Search bar, hit Ctrl+P, then type "Python: Select Interpreter" - or use the button in the lower right corner of the window). Likewise you can can set the Interpreter for Jupyter notebooks.

This repository will be updated regularly throughout the course. Make sure to keep up to date by synchronizing your fork via GitHub. Should the virtual environment change as well (new dependencies to install), we will notify you - you can update the environment running the `uv sync` command again after starting the environment.

**Important: In order to avoid merge conflicts, always copy any files you work on (notebooks, scripts, data, etc.) to a user folder in each lecture or assignment folder, or create a new file under a different name.** This way you can always accept incoming changes, without altering your personal file versions. 

We do recommend to practice the git workflow throughout this course and to commit to your fork after significant changes. **If there are any problems with your IDE, uv, git or your repo, that prevent you from using the environment as intended, please notify us via mail immediately and don't wait until the next Q&A session.** 

## Course structure
Every week comprises two lecture slots on Wednesdays (odd numbers) and Fridays (even numbers).

**Homework assignments** will be introduced and reviewed on **Fridays (even slots)** and there will be the opportunity to discuss and get input on homework assignments on Wednesdays (odd slots). Homework assigned each Friday is due by 7:59 am on the following Friday to Dimitrios by email, with the subject "DSA103_26_Ex1_LastName_FirstName". Your homework will be checked and you will receive feedback; it will not be graded, but you must submit the homework assignments to be admitted to the exam. Please note that one of these homework assignments will be replaced by a small project introduced in session 17 that you have three weeks instead of one week to work on.

Lecture slot:
1) Intro to course and to computational thinking (in class exercise, informal homework as a warm up for the course)
2) Computational thinking with Python (homework assignment session02)
3) Python review, homework Q&A
4) Homework recap session02, Q&A, and practice (homework session02 due by 7:59 am; homework assignment session04)
5) Version control, homework Q&A
6) Applying version control for collaboration, homework recap session04 (homework session04 due by 7:59 am; homework assignment session06)
7) Exploratory data analysis, homework Q&A
8) Finding and evaluating data, homework recap session06 (homework session06 due by 7:59 am; homework assignment session08)
9) Generating data for specific purposes, homework Q&A
10) Homework recap session08, Q&A, and intro to FAIR and CARE frameworks (homework session08 due by 7:59 am; homework assignment session10)
11) Exploring life science data 1: Data types, homework Q&A
12) Exploring life science data 2: Data structures, homework recap session10 (homework session10 due by 7:59 am; homework assignment session12)
13) Exploring life science data 3: Data analytics, homework Q&A
14) Overall recap, Q&A, homework recap session12 (homework session12 due by 7:59 am; homework assignment session14)
15) Data wrangling without loss, homework Q&A
16) Data wrangling with selective changes (outliers and other issues), homework recap session14 (homework session14 due by 7:59 am; homework assignment session16)
17) Putting it together: Small project introduction, homework Q&A
18) Putting it together: Small project work, homework recap session16 (homework session16 due by 7:59 am; homework assignment small projects DUE SESSION 24)
19) Lies, damn lies, and statistics, in class exercises
20) Data visualization: Honest vs. dishonest, useful vs. obfuscating (homework assignment session20)
21) Data visualization continued, homework Q&A
22) Homework recap session18, Q&A, intro to HPC (homework session20 due by 7:59 am; homework assignment session22)
23) Outlook: Machine learning, homework Q&A
24) Homework recap session20, putting it together: Small project finalization and submission (homework session22 due by 7:59 am; small projects due by 23:59)
25) Outlook: Vibe coding and agentic coding, preparation for mock exam
26) Mock exam
27) Mock exam recap and Q&A, bidirectional feedback round
28) Exam

## Authors
This repository was created and is maintained by Johannes Schörgenhumer and Meredith C. (Merry) Schuman.

## Acknowledgements

Many thanks to Marvin Alberts and Alexander Steppke for writing exercises and helping with solutions!

## License
CC BY-NC-SA 4.0 

You are free to share and adapt, as long as attribution to the authors is appropriately given, the material is not used for any commercial purposes and any material built on the content of the DSA104 repository is shared under the same license.

Full license information are found here: https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
