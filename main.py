import argparse
import shlex
import Methods

def main():
    parser = argparse.ArgumentParser(description='Emulator CLI')
    parser.add_argument('--vfs', type=str, help='Path to VFS location')
    parser.add_argument('--script', type=str, help='Path to startup script')

    args = parser.parse_args()

    print(f"Debug: VFS path = {args.vfs}")
    print(f"Debug: Script path = {args.script}")

    if args.vfs:
        Methods.load_vfs_from_csv(args.vfs)

    if args.script:
        if not Methods.execute_script(args.script):
            return

    while True:
        try:
            prompt = Methods.get_prompt()
            user_input = input(prompt)

            if not user_input:
                continue

            expanded_input = Methods.expand_variables(user_input)
            tokens = shlex.split(expanded_input)
            command = tokens[0]
            args = tokens[1:]

            if command == "exit":
                break
            elif command == "ls":
                Methods.handle_ls(args)
            elif command == "cd":
                Methods.handle_cd(args)
            elif command == "echo":
                Methods.handle_echo(args)
            elif command == "uname":
                Methods.handle_uname(args)
            elif command == "head":
                Methods.handle_head(args)
            else:
                Methods.handle_unknown_command(command)

        except KeyboardInterrupt:
            print("\nUse 'exit' command to quit")
        except EOFError:
            break

main()