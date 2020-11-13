##Read Me file for the Python Task Simulation System

##Summary
#Breif
- The purpose of this system is to generate a random set of 100 tasks and if the task is valid, run them through a simulation system that consists of a number of processors.
- The tasks consist of an id, start time and duration

#Running the system
- Please run both files. There is need to only run file 1 once and then to run file 2 once. The task simulation occurs in the CMD.
#What YOU can change
FILE 1 - You can change how many tasks you would like to have generated in file 1 and therefore run in the system. (Default is 100)
       - DB filename can be altered (Default is tasks.db but remember to change it in file 2)
       - You can choose to view the tasks in the CMD within a table if desired (Default is false)
FILE 2 - You can alter how many validity checks an ID needs for a task to be valid. (Default is 3 out of 4) The checks can be viewed within the file.
       - You can change how many processors in the system exist. (Default is 3)


##In-depth
#File 1 - Creation and Storage of the Tasks
- 100 tasks are created that consist of an ID, duration and entry time.
- These tasks are stored in an SQLite3 db that will download within the same dir


#File 2 - Simulation System
- The tasks that you created and that are stored within the db are then fed into a simulation system that consist of a number of processors.
- Depending on validity, they will be allowed in or rejected. The system will complete not on the basis of natural time but when all the tasks are complete.
- Only one processor can hold one task at any one time. If all processors are full then tasks will be put on hold. 
