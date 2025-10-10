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
    home_dir = os.environ.get('USERPROFILE', 'C:\\Users\\User')
    command = command.replace('$USERPROFILE', repr(home_dir).replace("\\\\", "\\"))
    return command


def execute_script(script_path):
    error_messages = []

    try:
        with open(script_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                print(get_prompt() + line)

                expanded_line = expand_variables(line)
                tokens = shlex.split(expanded_line)
                if not tokens:
                    continue

                command = tokens[0]
                args = tokens[1:]

                if command == "exit":
                    print(error_messages)
                    return False
                elif command == "ls":
                    handle_ls(args)
                elif command == "cd":
                    handle_cd(args)
                else:
                    error_messages.append(f"Line {line_num}: Unknown command '{command}'")

    except FileNotFoundError:
        print(f"Error: Script file '{script_path}' not found")
        return False
    except Exception as e:
        print(f"Error executing script: {str(e)}")
        return False

    if error_messages:
        print("\nScript execution completed with errors:")
        for error in error_messages:
            print(f"  {error}")


    return True