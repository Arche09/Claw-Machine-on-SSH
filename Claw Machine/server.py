import asyncio
import asyncssh
import os
import pty
import signal
import sys
import fcntl
import termios
import struct
import errno
from pathlib import Path

BASE_DIR = Path (__file__).resolve().parent
GAME_FILE = BASE_DIR / "claw_machine_linux.py"
HOST_KEY = BASE_DIR / "game_host_key"
PLAYER_KEYS_DIR = BASE_DIR / "player_keys"

HOST = "0.0.0.0"
PORT = 2222
AUTHORIZED_PLAYERS = {}

for key_file in PLAYER_KEYS_DIR.glob("*.pub"):
    username = key_file.stem

    try:
        AUTHORIZED_PLAYERS[username] = asyncssh.import_public_key(
            key_file.read_bytes()
        )
    except Exception as error:
        print(f"Could not load {key_file.name}: {error}")
        
class GameSSHServer(asyncssh.SSHServer):

    def begin_auth(self, username):
        return True

    def public_key_auth_supported(self):
        return True

    def validate_public_key(self, username, key):
        authorized_key = AUTHORIZED_PLAYERS.get(username)

        return authorized_key is not None and key == authorized_key

async def run_game(process):

    username = process.get_extra_info("username")

    if process.command or process.subsystem:
        process.exit(1)
        return

    if not process.term_type:
        process.stdout.write("A terminal is required.\r\n")
        process.exit(1)
        return

    if username not in AUTHORIZED_PLAYERS:
        process.exit(1)
        return

    print(f"{username} connected.")

    pid = None
    master_fd = None

    try:
        # Create a completely separate terminal for this player.
        pid, master_fd = pty.fork()

        if pid == 0:
            # Child process: launch the game.
            os.chdir(BASE_DIR)
            os.environ["CLAW_PLAYER"] = username

            os.execv(
                sys.executable,
                [sys.executable, str(GAME_FILE)]
            )
        loop = asyncio.get_running_loop()

        os.set_blocking(master_fd, False)
        size = process.term_size or (80, 24, 0, 0)

        columns, rows = size[0], size[1]

        fcntl.ioctl(
            master_fd,
            termios.TIOCSWINSZ,
            struct.pack("HHHH", rows, columns, 0, 0)
        )
        async def send_output():
            while True:
                try:
                    data = os.read(master_fd, 4096)

                    if not data:
                        break

                    process.stdout.write(
                        data.decode("utf-8", errors="replace")
                    )

                    await process.stdout.drain()

                except BlockingIOError:
                    await asyncio.sleep(0.01)

                except OSError as error:
                    if error.errno == errno.EIO:
                        break
                    raise

        async def receive_input():
            while True:
                data = await process.stdin.read(1)

                if not data:
                    break

                print(f"RK: {data!r}, flush=True")

                os.write(master_fd, data.encode("utf-8"))

        output_task = asyncio.create_task(send_output())
        input_task = asyncio.create_task(receive_input())

        await asyncio.wait(
            [output_task, input_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        input_task.cancel()
        output_task.cancel()

        await asyncio.gather(
            input_task,
            output_task,
            return_exceptions=True
        )

    except (asyncio.CancelledError, ConnectionError):
        pass

    except Exception as error:
        print(f"Game error for {username}: {error}")

    finally:
        if master_fd is not None:
            try:
                os.close(master_fd)
            except OSError:
                pass

        if pid is not None:
            try:
                os.kill(pid, signal.SIGHUP)
            except ProcessLookupError:
                pass

            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass

        print(f"{username} disconnected.")

async def main():

    print("Starting Claw Machine SSH Server...")
    print(f"Authorized players: {list(AUTHORIZED_PLAYERS)}")

    if not AUTHORIZED_PLAYERS:
        raise RuntimeError("No authorized player keys found.")

    async with asyncssh.create_server(
        GameSSHServer,
        HOST,
        PORT,
        server_host_keys=[str(HOST_KEY)],
        process_factory=run_game,
        encoding="utf-8"
    ):
        print(f"Game server listening on port {PORT}.")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Game server stopped.")


