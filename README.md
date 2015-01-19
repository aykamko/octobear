# Git Infrastructure for Berkeley EECS

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

4. Run the git infra.

    If this is your first time, set up accounts by running with the `--init` flag.

        $ python run.py --init

    Otherwise, omit the flag.

        $ python run.py


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
            "group_repo":    Boolean,   # whether or not submission to group repo
            "grader_login":  String,
            "comments":      String,
            "email_content": String,    # email to send student
            "email_plain":   Boolean,   # True => plaintext format, Default/False => Markdown format
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
