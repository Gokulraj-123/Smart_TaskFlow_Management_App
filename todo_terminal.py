#todo_terminal.py

tasks = []

while True:
    print("/n--- My To-Do List ---")
    print("1. Add Task")
    print("2. View Task")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        task = input("Enter your task name: ")
        tasks.append(task)
        print("Your Task Added Sucessfully!")

    elif choice == "2":
        print("/nYour Tasks: ")

        for number, task in enumerate(tasks, start=1):
            print(number, task)

    elif choice == "3":
        print("Thank You! See you later...")

    else:
        print("Invalid Choice")

