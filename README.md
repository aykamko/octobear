# Git Infrastructure for Berkeley EECS

### Initial Setup

1. Set up a python virtual environment. (Optional, but highly recommended)

    Using a virtual environemnt is helpful for when you need to install
    frameworks and packages specifically for a project but don't want them
    installed globally. This is particularly necessary if you want
    to use different versions of things simultaneously for different
    projects.
    Like Rails 4.1.6 versus 4.2.0.

    `pip install virtualenv`          // This installs virtualenv.

    `virtualenv git-infra`            // This creates a new virtual env.

    `source git-infra/bin/activate`   // This activates the virtual env.

    Important Note: Do not place your virtual env within directories being
    tracked by Git. Every developer's virtual env should be unique, and
    you don't want to commit it. (It's really large.) I personally put my
    virtual envs in `~`, but you can do whatever floats your boat.

    Suggestion: Check out [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/). Very 
    useful for organizing virtual envs.

2. Install necessary dependencies.

    (If you are using a virtualenv, this needs to be afer you activate the
    env. Otherwise, you'll be installing regularly.)

    `pip install -r requirements.txt`

    requirements.txt should be found in the root folder. It contains a list of
    all of the packages required a project.

