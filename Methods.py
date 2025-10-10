import os
import socket
import shlex
import csv
import base64

vfs = {}
current_path = "/"

def load_vfs_from_csv(csv_path):
    global vfs
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                path = row['path']
                vfs[path] = {'type': row['type'], 'content': row.get('content', '')}
        print("VFS loaded successfully:")
        for path, data in vfs.items():
            print(f"  {path} -> {data}")
    except FileNotFoundError:
        print(f"Error: VFS file '{csv_path}' not found")
        exit(1)
    except Exception as e:
        print(f"Error loading VFS: {str(e)}")
        exit(1)

def handle_ls(args):
    global current_path
    target = current_path
    if args:
        path = args[0]
        if not path.startswith('/'):
            path = os.path.normpath(os.path.join(current_path, path))
        target = path

    items = []
    for p in vfs:
        if p.startswith(target.rstrip('/') + '/') and p != target:
            rel = p[len(target):].strip('/')
            if '/' in rel:
                continue  # это вложенная директория, пропускаем
            items.append(rel)

    if items:
        print(' '.join(items))
    else:
        print("ls: no items found")

def handle_cd(args):
    global current_path
    if not args:
        print("cd: no argument provided")
        return

    path = args[0]
    if not path.startswith('/'):
        path = os.path.normpath(os.path.join(current_path, path))

    if path in vfs and vfs[path]['type'] == 'directory':
        current_path = path
    else:
        print("cd: no such directory")

def handle_echo(args):
    print(' '.join(args))

def handle_uname(args):
    import platform

    # По умолчанию — только имя системы
    system_name = platform.system() or "emulated-uname"
    hostname = platform.node()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor() or "unknown"

    # Парсим аргументы
    if not args:
        print(system_name)
        return

    all_info = False
    for arg in args:
        if arg == "-a":
            all_info = True
            break

    if all_info:
        print(f"{system_name} {hostname} {release} {version} {machine} {processor}")
        return

    for arg in args:
        if arg == "-s":
            print(system_name)
        elif arg == "-n":
            print(hostname)
        elif arg == "-r":
            print(release)
        elif arg == "-v":
            print(version)
        elif arg == "-m":
            print(machine)
        elif arg == "-p":
            print(processor)
        else:
            print(f"uname: invalid option -- '{arg[1:]}'")
            return

def handle_head(args):
    if not args:
        print("head: missing file operand")
        return

    path = args[0]
    if not path.startswith('/'):
        path = os.path.normpath(os.path.join(current_path, path))

    if path in vfs and vfs[path]['type'] == 'file':
        content = vfs[path]['content']
        decoded_content = base64.b64decode(content).decode('utf-8')
        lines = decoded_content.splitlines()
        for line in lines[:10]:
            print(line)
    else:
        print("head: no such file")

def handle_unknown_command(command):
    print(f"Unknown command: {command}")

def get_prompt():
    username = os.environ.get("USERNAME", "user")
    hostname = socket.gethostname()
    return f"{username}@{hostname}:{current_path}$ "

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
                elif command == "echo":
                    handle_echo(args)
                elif command == "uname":
                    handle_uname(args)
                elif command == "head":
                    handle_head(args)
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