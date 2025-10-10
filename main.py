import os
import socket
import shlex

def handle_ls(args):
    print("Command: ls ", args)

def handle_cd(args):
    print("Command: cd ", args)

def handle_unknown_command(command):
    print("Unknown_command:", command)

def get_prompt():
    username = os.environ.get("USERNAME", "user")
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$ "

def expand_variables(command):
    return os.path.expandvars(command)

def main():
    while True:
        prompt = get_prompt()
        user_input = input(prompt)

        if not user_input: continue

        expanded_input = expand_variables(user_input)
        tokens = shlex.split(expanded_input)
        command = tokens[0]
        args = tokens[1:]

        if command == "exit":
            print("EXIT")
            break
        elif command == "ls": handle_ls(args)
        elif command == "cd": handle_cd(args)
        else: handle_unknown_command(command)

main()