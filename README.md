# Autograder for Berkeley EECS

### Steps to setup registration server

1. Set up a virtual environment. (Optional but recommended)

    Using a virtual environemnt is helpful for when you need to install
    frameworks and packages specifically for a project but don't want
    them on your computer. This is particularly necessary if you want
    to use different versions of things simultaneously for different
    projects.
    Like Rails 4.1.6 versus 4.2.0.

    `pip install virtualenv`          // This installs virtualenv.

    `virtualenv ag-flask`             // This creates a new virtual env.

    `source ag-flask/bin/activate`    // This activates the virtual env.

    Important Note: Do not place your virtual env within directories being
    tracked by Git. Every developer's virtual env should be unique, and
    you don't want to commit it. (It's really large.) I personally put my
    virtual envs in `~`, but you can do whatever floats your boat.

2. Install necessary dependencies.

    (If you are using a virtualenv, this needs to be afer you activate the
    env. Otherwise, you'll be installing regularly.)

    You can use `pip freeze` to determine which of these packages are
    already installed.

    `pip install flask`               // Installs flask

    `pip install mongokit`            // Installs mongokit and pymongo


