# Problem #

Folder synchronization across multiple locations is a fundamental requirement for modern computational workflows. Even a single person using a notebook in multiple locations (a local machine and a JupyterHub, for example) needs to set up an external synchronization mechanism (git, commonly) to synchronize work across these locations easily. People who are not comfortable with git and other command-line-tools find this even more difficult, yet they are often familiar with other synchronization tools like Dropbox. We are particularly motivated by users of Jupyter notebooks who are not comfortable using git. That said, the problem of synchronizing notebooks overlaps with the problem of synchronizing folders: executing a notebook may depend on and create other files, and synchronizing folders is a more general problem than synchronizing notebooks. We hypothesize that a compromise between git and Dropbox would help an important and growing class of users.

## Motivating use case ##

Interest in data science is exploding.  As a result, many individuals across disciplines and with diverse computational backgrounds are discovering data science tools.  At schools like UC Berkeley (Cal), these individuals include students and instructors at all levels:  from incoming freshman to students across the college, masters, PhD, and MBA students, postdocs, lecturers, junior and senior faculty.  Instructors across the campus are developing data-centric classes, from freshman seminars to advanced special topics courses in areas such as history, literature, ecology, neuroscience, and health.  For example, here is a list of 11 data science seminars, aimed at freshmen, being taught this spring (2016) at Cal: https://data-8.appspot.com/sp16/modules/extra_tabs/render?index=3
Many of these instructors do not have traditional training in computer science or statistics, and are learning data science skills on the fly, as they develop and teach their courses.

Jupyter notebooks are widely employed in classes at Cal because they provide a natural environment for introducing data science skills to students.  Critically, they enable a browser-based interface to computation in the cloud, meaning that students only need a browser to start programming and interacting with data.  

However, the tools currently available for instructors require considerably more experience with computational and programming tools. In order to include and support this multidisciplinary group of instructors who are developing a rich ensemble of classes, particularly from disciplines currently underrepresented in data science, the tools available must be designed to facilitate the work of instructors whose research and educational backgrounds do not include, for instance, tools for version control. We focus here on a particular problem that they encounter early in developing and teaching the courses: managing the notebooks, data, and other files they develop and distribute to students.

For the instructors' current workflow, see https://github.com/data-8/connector-instructors#workflow 

# Summary of Solution #

Implement Dropbox-like synchronization of specific folders, accessible via the Jupyter Notebook interface. We will initially provide a GitHub backed implementation, but in the future other backends could be made available (e.g. Dropbox, generic git). We will explicitly avoid making a true Git GUI client - the user's mental model should be 'this is similar to Dropbox.'

# Implementation details #

This would be implemented as a Jupyter notebook backend extension. We'd use a very small subset of git commands, tied specifically into GitHub, to provide this synchronizing functionality.

## Synchronization ##

The actual synchronization would be handled by the python part of the nbextension, via logic similar to https://gist.github.com/yuvipanda/6cdeab86ccaa15687b25. 

1. Every 30s (or other configurable interval)...
2. We perform an automatic commit of everything in the Synchronized Folder (with a not very useful commit message)
3. Do a git pull with an automerge that's guaranteed to never conflict, by simply opinionatedly choosing one side of the conflict (by default, the most recent version based on timestamp)
4. Push to master

This would happen for all 'synchronized folders'.

It would have to figure out a way of listing all the folders that need syncing - this could be info kept in a central location somewhere standard. Since this will be presently implemented as a jupyter extension, we would store this where jupyter stores other config.

## Authentication ##

Initially, we will just use GitHub personal access tokens - to simplify deployment and usage locally. Directly using OAuth requires that all users of notebooks create, register and configure OAuth credentials, which is not feasible for the target audience in this case. Personal access tokens can be revoked in the GitHub interface in case of security issues, and allow us to push / pull appropriately.

New personal access tokens can be created via https://github.com/settings/tokens/new. You can think of personal access tokens as similar to ssh keys - you create one per machine. They are just easier to create, revoke and use than actual ssh keys.

## UI ##

The entry point would be under the 'New' button in the notebook UI - in addition to 'File', 'Folder' and 'Terminal', it would have 'Synchronized Folder' as an option, which sets off a simple UI that allows people to authenticate (if necessary), and setup the appropriate GitHub repository to sync.
    
(WARNING: Vague flow only, will consult with an actual UX person before developing!)

![Initiate creating a new Synchronized Folder](http://i.imgur.com/x18vqRm.png)
*Initiate creating a new Synchronized Folder*

![Initial authentication request](http://i.imgur.com/hOdsLvW.png)
*Initial authentication request (happens first time, and then every time there's an authentication issue requiring re-authentication)*

![Select which GitHub repository to sync.](http://i.imgur.com/RJVwPQB.png)
*Select which GitHub repository to sync. Should do an JS based check to see if it is something the user can push to / pull from or not, and provide appropriate information.*

![show a little bit of extra information](http://i.imgur.com/6D1Brhl.png)
*(When browsing Synchronized Folders show a little bit of extra information somewhere with metadata about what is going on - including info on when it was last updated, status, etc). Copy dropbox's design as much as possible.*

User should also be able to turn off / on synchronization and easily see which repositories are under synchronization. This can be implemented as an additional tab that has info on all synchronized folders.

The synchronization will only happen when a jupyter process is open and running.

## Implementation Structure ##

The backend python part will be structured into two parts:
    
1. A simple tornado coroutine that runs forever, doing the actual synchronization for all the repositories
2. A bunch of HTTP endpoints that the clientside JS uses to perform various actions, such as:
a. Creating a new Synchronized Repository
b. Validating and setting authentication information
c. Getting and setting metadata about each synchronized repository
d. Anything else, really :D

These two might need to share some state (such as locations of the repositories and authentication information), tbd what is the best way to do this. The state should persist across restarts, so somewhere on the FS seems appropriate. 
   
The frontend JS will be fairly simple, just hooks on to the backend implementation.

## Requirements ##

1. Python 3.4+
2. Git installed
3. A recentish version of Jupyter
4. Windows / OS X / Linux
5. GitHub Account

# Pros #

1. Access control is outsourced to GitHub
2. People normally using git can still collaborate without needing to use this system (albeit it might be slightly more annoying because git log is unusable)
3. Super simplified mental model that solves a good chunk of the problem without requiring a lot of work

# Cons #

1. Not 'true' collaboration (etherpad/google docs style)
2. The merging might lead to confusing effects in edge cases

# Considerations of further work #

1. Allow adding manual commit messages (Will just be empty commits solely to provide manual checkpoints)
2. Helper scripts that provide a sanitized public view of this repository - squash all the autocommits to the latest manual commit and push to a different repository
3. Consider alternate synchronization behavior

# People interested #

@yuvipanda
@elaine84
@fhocutt
