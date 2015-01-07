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

        $ python run.py

### Things working so far:

1. Registration

    Running the infra will start up a RegistrationHandler that listens on port 8000.
    If you send a POST to that port with the following JSON format, you can "register" a
    student:

        {
          "sid": xxx,
          "name": xxx,
          "email": xxx,
          "github": xxx
        }

    You can test this out by running the example Flask app. Just make sure you "enroll" an
    SID in the class first, by adding a new Member document to the MongoDB. (See db/schema.py)

    To enroll an SID:

        $ python -i -m src.db.schema    # Connect to MongoDB via Python shell
        >>> new = connection.Member()
        >>> new['sid'] = 1234           # Create the student
        >>> new.save()
