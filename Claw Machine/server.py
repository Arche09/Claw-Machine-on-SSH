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

HOST = "127.0.0.1"
PORT = 2222

class GameSSHServer(asyncssh.SSHServer):

    def begin_auth(self, username):
        return False

    def connection_requested(self, dest_host, dest_port,
                              orig_host, orig_port):
        return False

    def server_requested(self, listen_host, listen_port):
        return False

async def run_game(process):

    username = process.get_extra_info("username")

    if process.command or process.subsystem:
        process.exit(1)
        return

    if not process.term_type:
        process.stdout.write("A terminal is required.\r\n")
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

    print("Starting Claw Machine SSH Server..")

    async with asyncssh.create_server(
        GameSSHServer,
        HOST,
        PORT,
        server_host_keys=[str(HOST_KEY)],
        process_factory=run_game,
        encoding="utf-8",
        line_editor=False
    ):
        print(f"Game server listening on port {PORT}.")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Game server stopped.")
