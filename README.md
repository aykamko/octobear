# Octobear: A git Infrastructure for Berkeley EECS

### Initial Setup

1. Set up a python virtual environment. (Optional, but highly recommended)

    Using a virtual environemnt is helpful for when you need to install
    frameworks and packages specifically for a project but don't want them
    installed globally. This is particularly necessary if you want
    to use different versions of things simultaneously for different
    projects.
    Like Rails 4.1.6 versus 4.2.0.

        $ pip install virtualenv          // This installs virtualenv.
        $ virtualenv git-infra            // This creates a new virtual env.
        $ source git-infra/bin/activate   // This activates the virtual env.

    Important Note: Do not place your virtual env within directories being
    tracked by Git. Every developer's virtual env should be unique, and
    you don't want to commit it. (It's really large.) I personally put my
    virtual envs in `~`, but you can do whatever floats your boat.

    Suggestion: Check out [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/). Very 
    useful for organizing virtual envs.

2. Install necessary dependencies.

    (If you are using a virtualenv, this needs to be afer you activate the
    env. Otherwise, you'll be installing regularly.)

        $ pip install -r requirements.txt

    requirements.txt should be found in the root folder. It contains a list of
    all of the packages required a project.

3. [Install MongoDB](http://docs.mongodb.org/manual/installation/), then spin up a MongoDB instance.

        $ mkdir -p data/db
        $ mongod --dbpath data/db

    This will create a new databse in data/db and start a MongoDB instance. This
    needs to run perpetually in the background as a deamon.

4. [Install Redis](http://redis.io/download), then start a server.

        $ brew install redis        # Homebrew on OSX
        $ redis-server /usr/local/etc/redis.conf

5. Run the git infra.

    If this is your first time, you have a few options. If you don't have any
    account forms, you can run the infra with spoof accounts like so:

        $ ./start --test-init

    If this is production and you *do* have a folder full of bulk account form
    pdfs, then you should put all of the student bulk account forms into one
    folder and run the infra like so:

        $ ./start --bulk-account-dir <account-dir> --min-login-len <2, 3>

    Otherwise, if running the infra after initialization, simply use:

        $ ./start


### API

1. Registration

    To register a student, send a POST request to the RegistrationHandler in
    the following format:

        HTTP Header: 
          { 
            'Content-Type': 'application/json' 
          }

        Content:
          {
            "sid": Number,
            "name": String,
            "email": String,
            "github": String
          }

2. Autograder Results

    To record results from a run of an autograder, send a POST requst to the
    AutograderResultHandler in the following format:

        HTTP Header: 
          { 
            'Content-Type': 'application/json' 
          }

        Content:
          {
            ------ Required Fields ------
            "score":         Number,
            "assignment":    String,
            "repo":          String,    # name of graded repo (e.g. 'ds' or 'group24')
            "submit":        Boolean,   # switch to record grade in database (or not)

            ------ Optional Fields ------
            "group_repo":    Boolean,   # whether or not submission is from group repo
            "grader_login":  String,
            "comments":      String,
            "email_content": String,    # email to send student
            "email_plain":   Boolean,   # True => plaintext, Default/False => Markdown
            "raw_output":    String     # raw output of autograder, for logging
          }

    Emails will be compiled as Markdown unless otherwise specified by the
    `email_plain` Boolean field. HTML in the Markdown will not be compiled.

### Things working so far:

1. Registration

    Running the infra will start up a RegistrationHandler that listens on port 8000. 
    Read the above API section to see how to use it.

    You can test this out registration by running the example Flask app. Just
    make sure you "enroll" an SID in the class first. To enroll an SID:

        $ python -i -m src.db.schema    # Connect to MongoDB via Python shell
        >>> new = connection.Member()
        >>> new['sid'] = 1234           
        >>> new.save()                  # Create the student

### Commands and one-time processes

1. Importing account forms

    Account forms come in bulk PDFs that look like `cs162.class-1.pdf`,
    `cs162.class-2.pdf`. There are also more PDFs for TA, reader, and LA accounts,
    but we're only concerned with normal student accounts.

    The code in Octobear can split, identify, and import account forms. First,
    make a directory to contain your work, since this process creates a lot of
    files, and you will want to contain them. Then, grab a copy of
    [Apache PDFBox](https://pdfbox.apache.org/download.cgi) and save it as
    `pdfbox.jar` in your working directory. Copy the identify_account_forms
    script into your working directory, as well as your `cs162.class-*.pdf` files.

    The process can be summarized like:

    ```
    mkdir work/
    cd work/
    wget -o pdfbox.jar "http://apache.cs.utah.edu/pdfbox/1.8.8/pdfbox-app-1.8.8.jar"
    cp ../identify_account_forms identify_account_forms
    cp ~/Downloads/cs162.class-*.pdf ./
    ```

    Then, you should split up your account forms:

    ```
    ./identify_account_forms split cs162.class-*.pdf
    ```

    The new files will be named in the form of `cs162.class-1-123.pdf`, where
    123 is the zero-indexed page number. You should test the identification code
    on a few of these PDFs, just to make sure it works. (You will probably need
    to edit the `keyword` variable that is used to look for account logins, inside
    the identify_account_forms script.)

    ```
    ./identify_account_forms identify cs162.class-1-*.pdf
    ```

    Once you're satisfied with the identification accuracy, perform the rename
    command, which is the same as identify, except it actually renames the PDF
    files into filenames such as `aa.pdf`.

    ```
    ./identify_account_forms rename cs162.class-1-*.pdf
    ./identify_account_forms rename cs162.class-2-*.pdf
    
    ... ETC ...
    ```

    Finally, the system expects account forms to live in the `account_forms/`
    directory in the root of the web application. Move your account forms there,
    and wipe your work directory.

    Once your account forms are in place, you should start the web application
    with the `--account-init` option, which tells the application to list the
    PDFs in `account_forms/` and add each account name to the list of available
    accounts. The application will remove the `.pdf` extension and use the file
    name as the login.

    ```
    ./start --account-init
    ```
