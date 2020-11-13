# Q1

# The following code has been formatted with the Atom Beautify & Atom Python Autopep8 plug-ins.
# References have been added at the first instant of the referenced code's use. They are not repeated. Referencing is done according to: https://xerte.cardiff.ac.uk/play_4069#topnav

# Q1 imports
import random, string, math, sqlite3, os

# Hi, choose the number of tasks, the filename for the database and whether you would like to view the tasks in a formatted table in the console. Default values have been set below.
choose_tasks = 100
choose_filename = 'tasks.db'
choose_to_view_tasks_in_table = False

# Class for creating the table with tasks.
# This class creates the tasks & adds them into a table. Instances of this class depend on the number of tasks, the filename & table view.
class CreateTableWithTasks:
    # The initialisation method for this class.
    def __init__(self, num_tasks, filename, table_view):
        self.num_tasks = num_tasks
        self.filename = filename

        self.connect()
        if self.fetch_records() == []: # Only creates the table if tasks are not present in one that has already been created. Will then create and add the tasks.
            tasks_list = self.create_tasks()
            self.add_tasks_to_db(tasks_list)
        else: # Will let user know if the table has been created. If tasks are already in the table then it will let the user know in the console.
            print("\n** A Table with {} tasks has already been created. **\n".format(len(self.fetch_records()))) # This is not self.num_tasks but self.fetchall() as the user may want to create a table with a different number of tasks.
            print("** Delete {} to create a new table with {} tasks.**".format(self.filename, self.num_tasks)) # Used the line breaks to make it clearer in the console. I add self.num_tasks in here as the desired number of tasks may be different to the current number of tasks in the table.
        if table_view == True: # Boolean to allow the user to see the formatted table in the console if requested.
            self.view_table()

    # Function below to create the tasks.
    def create_tasks(self):
        tasks = []
        size_of_id = 6 # Length of task ID.
        special_characters = "@_#*-&" # Special chars allowed for task ID.
        i = 0
        while i < self.num_tasks:
            task_id = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase + special_characters) for _ in range(size_of_id)) #Creating the task ID.
            # Source: string -  common string operations [Online]. Available at: https://docs.python.org/3/library/string.html [Accessed: 10 November 2019].
            arrival = random.uniform(0, 100) # Creating the random real number for arrival.
            # Source: 9.6. random — Generate pseudo-random numbers [Online]. Available at: https://docs.python.org/2/library/random.html [Accessed: 10 November 2019].
            duration = math.ceil(random.expovariate(1)) # Creating the random exponential of parameter 1 for duration.
            # Source: 9.6. random — Generate pseudo-random numbers [Online]. Available at: https://docs.python.org/2/library/random.html [Accessed: 10 November 2019].
            # Source: 9.2. math — Mathematical functions [Online]. Available at: https://docs.python.org/2/library/math.html [Accessed: 10 November 2019].
            task = (task_id, arrival, duration)
            b = tasks.append(task)
            i += 1
        return tasks

    # A function to create the table. It will only create one table with the following columns.
    def connect(self):
        needcreate = not os.path.exists(self.filename)
        self.db = sqlite3.connect(self.filename)
        if needcreate:
            cursor = self.db.cursor()
            cursor.execute("CREATE TABLE tasks_data ("
                           "id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                           "task_id TEXT NOT NULL, "
                           "arrival REAL NOT NULL, "
                           "duration INTEGER NOT NULL )")
            self.db.commit()
            cursor.close()

    # A function to fetch the records if needed. The records could be printed for debugging purposes. The function is also used above to see if tasks exist in the table.
    def fetch_records(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM tasks_data')
        self.db.commit()
        records = cursor.fetchall()
        return records

    # A function to add the tasks to the database table that has already been created.
    def add_tasks_to_db(self, tasks_list):
        cursor = self.db.cursor()
        print(tasks_list)
        cursor.executemany("INSERT INTO tasks_data (task_id, arrival, duration) VALUES (?, ?, ?)", (tasks_list))
        self.db.commit()
        cursor.close()

    # A function to view the records as a formatted table in your console. This can be requested when an object of the class is called.
    def view_table(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM tasks_data')
        self.db.commit()
        records = cursor.fetchall()

        template = "| {:>4} | {:>10} | {:>20} | {:>8} |"
        print("\n** Table for tasks in {} is as follows:\n".format(self.filename)) # Information in the console to alert them if a table has been created and which file it is.
        print(template.format("ID", "Task ID", "Arrival", "Duration"))
        print("| {0:->4} | {0:->10} | {0:->20} | {0:->8} |".format(''))
        for item in records:
            print(template.format(item[0], item[1], item[2], item[3]))

        cursor.close()


# Calling an instance of the class with the apropiate arguments needed.
tasks_creation = CreateTableWithTasks(choose_tasks, choose_filename, choose_to_view_tasks_in_table)
