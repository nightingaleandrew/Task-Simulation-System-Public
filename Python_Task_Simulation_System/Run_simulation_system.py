# Q2

# The following code has been formatted with the Atom Beautify & Atom Python Autopep8 plug-ins.
# References have been added at the first instant of the referenced code's use. They are not repeated. Referencing is done according to: https://xerte.cardiff.ac.uk/play_4069#topnav

#Q2 imports
import re, sqlite3, queue, itertools, os

# Choices - set variables for the system. Defaults have been set below.
# Choose the number of processors you would like.
choose_processors = 3
# Choose the checks you would like in regular expression form.
choose_checks = [r"[\d]", r"[A-Z]", r"[-@_#*&]", r"[a-z]"]
# Choose out of the checks above, how many you would like to make a task ID valid.
choose_at_least_no_of_checks = 3
# Choose the name of the db filename that you would like the system to use.
choose_data_file = "tasks.db"


# Class for running the system depending on the filename, number of processors, checks, and min number of checks for a valid ID.
# I have created this class as it is a template for the system. Different instances of this class will then depend on the number of processors, filename, the checks used & the number of checks needed for a valid ID.
class RunTaskSimulationSystem:
    # The initialisation function for this class creates the variables needed and calls the functions below in the correct order of the system. It then runs the system.
    def __init__(self, processors, file, checks, checks_no):
        self.filename = file
        if os.path.exists(self.filename): # I have added some error handling here to let the user know if the db file can be located correctly.
            self.processors = processors
            self.checks = checks
            self.at_least_no_of_checks = checks_no
            self.next_task, self.valid_tasks, self.invalid_tasks, self.completed_tasks = [], [], [], []
            self.formatted_checks, self.id_checks, self.matches = [], [], []
            self.clock = 0
            self.p = []

            self.records = self.fetch_records()
            self.tasks_number = len(self.records)
            self.on_hold_tasks = queue.Queue()
            # Source: queue - A synchronised queue class [Online]. Available at: https://docs.python.org/3/library/queue.html [Accessed: 20 November 2019].
            self.tasks_list = queue.Queue()
            self.records.sort(key=lambda x: x[2])
            # Source: Thoma, M. 2015. How to sort (list/tuple) of lists/tuples by the element at a given index? [Online]. Available at: https://stackoverflow.com/questions/3121979/how-to-sort-list-tuple-of-lists-tuples-by-the-element-at-a-given-index [Accessed: 15 November 2019].

            # Below I am calling the methods to setup the system.
            self.add_tasks_to_queue()
            self.choose_number_processors()
            self.create_regular_expression()

            # Below is the while loop for the system.
            while (self.tasks_number != (len(self.completed_tasks) + len(self.invalid_tasks))):
                # First it will loop through the main tasks queue (it will of course look at the on hold queue too if needed).
                while self.tasks_list.empty() == False:
                    self.next_task = self.tasks_list.get() # On every loop it receives a new task.
                    self.p.sort(key=lambda x: x[2]) # The processors are sorted by lowest processor end time (processors are then completed in order if need to be completed).
                    self.p_complete()
                    self.p.sort(key=lambda x: x[0]) # On hold tasks have priority. Tasks also need to be allocated by order of processor number not end time so a re-ordering is needed.
                    self.add_on_hold_tasks()
                    self.p.sort(key=lambda x: x[2]) # Again tasks may need to be completed in this iteration of the loop (again ordered by end time).
                    self.p_complete()
                    self.p.sort(key=lambda x: x[0]) # Now the task can be added from the main queue. It will go through validation. Processor availability will then be determined. It will be added to the on hold queue if no processor is available.
                    self.add_and_validiate_task()
                    self.p.sort(key=lambda x: x[2]) # It may be the end of the loop so processors need to be completed if no more tasks are left.
                    self.p_complete_end()
                # This while loop takes into account if there are on hold tasks still present even if the main queue is empty. Eg. if a 1000 tasks were put through the system.
                while self.on_hold_tasks.empty() == False:
                    self.p.sort(key=lambda x: x[2])
                    self.complete_on_hold()

                self.p.sort(key=lambda x: x[2]) # Again the processors may need to be completed overall.
                self.p_complete_end()

            self.reset_processors() # When the system completes I reset the processors.
            #print("Completed:{} + Inavlid:{} = All:{}".format(len(self.completed_tasks), len(self.invalid_tasks), ((len(self.completed_tasks)) + len(self.invalid_tasks)))) # I have left this in for debugging purposes.
            print("** {} : SIMULATION COMPLETED. **".format(self.clock)) # The system completes when the loop has completed.
        else:
            print("\n** System cannot locate database.**\n")

    # Defining of methods for this class - functions to setup the system.
    # A function to receive the tasks from the database in the chosen filename above. Returns as a list.
    def fetch_records(self):
        db = sqlite3.connect(self.filename)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM tasks_data')
        db.commit()
        self.tasks_list = cursor.fetchall()
        return self.tasks_list

    # A function to add the tasks from the database to a queue (it is a for loop so one task can be extracted at one time using .get() method of queue module)
    def add_tasks_to_queue(self):
        for task in self.records:
            self.tasks_list.put(task)
        return self.tasks_list

    # A function to create the processors for the system. Using the variable inputted above, the user can choose the number of processors.
    def choose_number_processors(self):
        for i in range(self.processors):
            processor = [i + 1, "", 0, 0] # The processor consists of a processor number, id code, processor end time and availability.
            self.p.append(processor)
        return self.p
        # Processor Availability: 0 or 1. 0 is available and 1 is not available.

    # A function to create the regular expression to validate the IDs depending on the conditions placed above by the user.
    def create_regular_expression(self):
        for check in self.checks:
            formatted_check = r"(?=.*{})".format(check) # The check is then added within the string shown to find a match in the ID.
            # Source: Gimenez, D. 2014. Regex to find 3 out of 4 conditions [Online]. Available at: https://stackoverflow.com/questions/22204836/regex-to-find-3-out-of-4-conditions [Accessed: 15 Novmeber 2019].
            self.formatted_checks.append(formatted_check)

        checks = list(itertools.permutations(self.formatted_checks, self.at_least_no_of_checks)) # Done to find the number of permutations for the checks given above.
        # Source: Ulhaq, M. and Bendersky E. 2017 How to generate all permutations of a list in Python [Online]. Available at: https://stackoverflow.com/questions/104420/how-to-generate-all-permutations-of-a-list-in-python [Accessed: 29 November 2019]
        output = list(set(tuple(sorted(t)) for t in checks)) # The permutations are then reduced to the number of unique combinations independent of the order.
        # Source: tdelaney 2016 Delete duplicate tuples independent of order with same elements in generator Python 3.5 [Online]. Available at: https://stackoverflow.com/questions/40850892/delete-duplicate-tuples-independent-of-order-with-same-elements-in-generator-pyt?noredirect=1&lq=1 [Accessed 29 November 2019]

        for item in output: # The unique permutations are then joined together to fulfil the regular expression string.
            self.id_checks.append("".join(item))
        # Source: Ivc 2013 Concatenate elements of a tuple in a list in python [Online]. Available at: https://stackoverflow.com/questions/20736917/concatenate-elements-of-a-tuple-in-a-list-in-python [Accessed: 29 November 2019]


    # Functions to carry out system.

    # A function to assign a task to a processor.
    def assign_task(self, processor, task): # It attaches the ID of the task to the processor, updates the new processor end time, updates the processor availability & prints the statement.
        # I do not update the clock here unlike with complete_task() because the assignment of an on hold task does not change the clock.
        processor[1] = task[1]
        processor[2] = self.clock + task[3]
        print("** {} : Task {} assigned to processor {}.".format(self.clock, task[1], processor[0]))
        processor[3] = 1

    # A function to put a task on hold.
    def put_task_on_hold(self, task): # It prints the on hold statement & adds the task into the on hold queue.
        print("** Task {} on hold.".format(task[1]))
        self.on_hold_tasks.put(task)

    # A function to complete a task on a processor.
    def complete_task(self, processor): # It updates the clock, prints the statement, updates the processor availability & adds the task to a completed list. The completed list is good for debugging purposes.
        self.clock = processor[2]
        print("** {} : Task {} completed.".format(self.clock, processor[1]))
        self.completed_tasks.append(processor[1])
        processor[3] = 0

    # A function to add a validated task to a processor. Otherwise, the task will be added to the on hold queue.
    def add_valid_task(self, task):
        for processor in self.p:
            if processor[3] == 0:
                self.clock = task[2] # This is where I update the clock for the assignment of a new task.
                self.assign_task(processor, task)
                self.valid_tasks.clear() # I use a list to determine if there is need to put the task on hold. See if statement below within the add_valid_task() function.
                break
        if len(self.valid_tasks) == 1:
            self.put_task_on_hold(task)
            self.valid_tasks.clear()

    # A function to validate a task.
    def validate_task(self, task, id_checks):
        for item in self.id_checks:
            if (re.match(r"^{}".format(item), task[1])):
                print("** Task {} accepted.".format(task[1]))
                self.valid_tasks.append(task) # I use the valid tasks list to add the task too. It relates to the self.add_valid_task() function above.
                self.add_valid_task(task) # This is the above function that determines whether a task is added or put on hold.
                self.matches.append("match") # I use this 'match' technique becuase the loop iterates over each regular expression in the id_checks list. Therefore, it may match on one but not other iterations. However, only one match is needed for success.
                break
        if "match" not in self.matches:
            print("** Task {} unfeasible and discarded.".format(task[1]))
            self.invalid_tasks.append(task) # Add task to the invalid list. This is again a good list for debugging.
        self.matches.clear() # Clear the matches list for the next task.

    # A function to see if the next event is adding a new task and validate the task if so.
    def add_and_validiate_task(self):
        for processor in self.p: # Iterate over the processors to find if the next event is adding a new task. Processor[2] is the end time & processor[3] is the availability.
            if (self.next_task[2] <= processor[2]) or (processor[3] == 0 and processor[2] <= self.next_task[2]):
                self.clock = self.next_task[2]
                print("** {} : Task {} with duration {} enters the system.".format(
                    self.clock, self.next_task[1], self.next_task[3]))
                self.validate_task(self.next_task, self.id_checks)
            break

    # A function to add on hold tasks which does not consider a new tasks from the incoming queue.
    def add_on_hold_tasks(self):
        for processor in self.p:
            if (self.on_hold_tasks.empty() == False) and (processor[3] == 0):
            #while ((self.on_hold_tasks.empty() == False) and (processor[3] == 0)): #Pulls a new task if there are on_hold tasks and a processor is available.
                task = self.on_hold_tasks.get()
                self.assign_task(processor, task)
                break

    # A function to complete a processor & then look to assign an on hold task if there is one.
    # The function completes the processors in the order of the earliest processors's completion time. Therefore if a task is added, the for loop is started again.
    def p_complete(self):
        should_restart = True
        # Source: Liquid_Fire. 2010. Python - Way to restart a for loop, similar to "continue" for while loops? [duplicate] [Online]. Available at: https://stackoverflow.com/questions/3704918/python-way-to-restart-a-for-loop-similar-to-continue-for-while-loops [Accessed 16 November 2019].
        while should_restart:
            should_restart = False
            for processor in self.p:
                while ((processor[2] < self.next_task[2]) and (processor[3] != 0)):
                    self.complete_task(processor)
                if ((self.on_hold_tasks.empty() == False) and (processor[2] < self.next_task[2])):
                    task = self.on_hold_tasks.get()
                    self.assign_task(processor, task)
                    self.p.sort(key=lambda x: x[2])
                    should_restart = True
                    break

    # A function to complete an on hold task. This does not take into account whether there is a new task or not.
    def complete_on_hold(self):
        for processor in self.p: # Iterates over each processor.
            if (processor[3] != 0):
                self.complete_task(processor)
                task = self.on_hold_tasks.get() # Assign the next task from the on hold queue.
                if processor[3] == 0:
                    self.assign_task(processor, task)
                    break
                break

    # A function to complete any tasks that remain in the processors when there are no tasks in the incoming queue or the on hold queue.
    def p_complete_end(self):
        for processor in self.p:
            if (self.tasks_list.empty() == True and self.on_hold_tasks.empty() == True): # If both queues are empty.
                if processor[3] == 1:
                    self.complete_task(processor)

    # A function to reset the processors if needed.
    def reset_processors(self):
        self.p.sort(key=lambda x: x[0])
        for processor in self.p:
            processor[1] = "" # It resets the ID to an empty string.
            processor[2] = 0 # It resets the processor end time to 0.


# Calling an instance of the class with the apropiate arguments needed.
system_output = RunTaskSimulationSystem(choose_processors, choose_data_file, choose_checks, choose_at_least_no_of_checks)
