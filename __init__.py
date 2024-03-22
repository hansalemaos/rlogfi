import sys
import traceback
import asyncio
import aiofiles
from tkkillablethreads import ExecuteAsThreadedTask
import time
import subprocess
import os
import ctypes
from ctypes import wintypes
from touchtouch import touch
from typing import Optional, Union, Literal
creationflags = subprocess.CREATE_NO_WINDOW

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE
creationflags = subprocess.CREATE_NO_WINDOW
invisibledict = {
    "startupinfo": startupinfo,
    "creationflags": creationflags,
    "start_new_session": True,
}
invisibledict = {
    "startupinfo": startupinfo,
    "creationflags": creationflags,
    "start_new_session": True,
}
DEFAULT = "\033[0m"
RED = "\033[91m"
debug = True

windll = ctypes.LibraryLoader(ctypes.WinDLL)
kernel32 = windll.kernel32

PROCESS_QUERY_INFROMATION = 0x1000
_GetShortPathNameW = kernel32.GetShortPathNameW
_GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
_GetShortPathNameW.restype = wintypes.DWORD


def printincolor(values, color=None):
    if color:
        print("%s%s%s" % (color, values, DEFAULT))

    else:
        print("%s%s" % (values, DEFAULT))


def errwrite(s=None):
    if not debug:
        return
    printincolor("------------------------------------------", RED)
    try:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb, file=sys.stderr)
    except Exception:
        sys.stderr.write(f"{s}\n")
    sys.stderr.flush()
    printincolor("------------------------------------------", RED)


async def read_stdout(
    so_list,
    so_file,
    so_sleep,
    so_stoptrigger,
    so_print,
):
    try:
        async with aiofiles.open(so_file) as f:
            while True:
                async for line in f:
                    if any(so_stoptrigger):
                        break
                    so_list.append(line)
                    if any(so_print):
                        print(line, end="")
                await asyncio.sleep(so_sleep[0])
    except Exception as e:
        errwrite(e)


async def read_stderr(
    se_list,
    se_file,
    se_sleep,
    se_stoptrigger,
    se_print,
):
    try:
        async with aiofiles.open(se_file) as f:
            while True:
                if any(se_stoptrigger):
                    break
                async for line in f:
                    se_list.append(line)
                    if any(se_print):
                        print(line, end="")
                await asyncio.sleep(se_sleep[0])
    except Exception as e:
        errwrite(e)


async def main(
    so_list,
    se_list,
    so_file,
    se_file,
    so_sleep,
    se_sleep,
    so_stoptrigger,
    se_stoptrigger,
    so_print,
    se_print,
):
    try:
        while not os.path.exists(so_file) or not os.path.exists(se_file):
            await asyncio.sleep(1)
        stdout_task = await asyncio.to_thread(
            read_stdout,
            so_list=so_list,
            so_file=so_file,
            so_sleep=so_sleep,
            so_stoptrigger=so_stoptrigger,
            so_print=so_print,
        )
        stderr_task = await asyncio.to_thread(
            read_stderr,
            se_list=se_list,
            se_file=se_file,
            se_sleep=se_sleep,
            se_stoptrigger=se_stoptrigger,
            se_print=se_print,
        )

        await asyncio.gather(stdout_task, stderr_task)
    except Exception as e:
        errwrite(e)


def get_timest():
    return time.strftime("%Y_%m_%d_%H_%M_%S")


def run_main(
    so_list,
    se_list,
    so_file,
    se_file,
    so_sleep,
    se_sleep,
    so_stoptrigger,
    se_stoptrigger,
    so_print,
    se_print,
):
    asyncio.run(
        main(
            so_list=so_list,
            se_list=se_list,
            so_file=so_file,
            se_file=se_file,
            so_sleep=so_sleep,
            se_sleep=se_sleep,
            so_stoptrigger=so_stoptrigger,
            se_stoptrigger=se_stoptrigger,
            so_print=so_print,
            se_print=se_print,
        )
    )


def get_short_path_name(long_name):
    try:
        if os.path.exists(long_name):
            output_buf_size = 4096
            output_buf = ctypes.create_unicode_buffer(output_buf_size)
            _ = _GetShortPathNameW(long_name, output_buf, output_buf_size)
            return output_buf.value
    except Exception:
        pass
    return long_name


def escapecmdlist(arguments):
    updatedarguments = []
    for a in arguments:
        a = str(a)
        if os.path.exists(a):
            a = "'" + get_short_path_name(a) + "'"
        else:
            if '"' not in a and "'" not in a and "`" not in a:
                a = "'" + str(a) + "'"
            elif '"' in a and ("'" not in a and "`" not in a):
                a = "'" + str(a) + "'"
            elif "'" in a and ('"' not in a and "`" not in a):
                a = '"' + str(a) + '"'
            elif "'" in a or '"' in a and "`" not in a:
                a = "`" + str(a) + "`"
        updatedarguments.append(a)
    updatedargumentsstr = ",".join(updatedarguments)
    return updatedargumentsstr


class PowerShellDetachedInteractive:
    def __init__(
        self,
        executable: str = "cmd.exe",
        logfolder: Optional[str] = None,
        working_dir: Optional[str] = None,
        execution_policy: Literal[
            "AllSigned",
            "Bypass",
            "Default",
            "RemoteSigned",
            "Restricted",
            "Undefined",
            "Unrestricted",
        ] = "Unrestricted",
        arguments: Union[str, list, tuple] = (),
        WhatIf: str = "",
        Verb: str = "",
        UseNewEnvironment: str = "",
        Wait: str = "",
        stdinadd: str = "",
        RedirectStandardInput: str = "",
        WindowStyle: Literal["Hidden", "Maximized", "Minimized", "Normal"] = "Normal",
        stdout_sleep=0,
        stderr_sleep=0,
        stdout_print=True,
        stderr_print=True,
        *args,
        **kwargs,
    ):
        r"""
        Creates a new subprocess that runs cmd.exe in PowerShell.



        Args:
            executable (str, optional): The path to the executable file to be executed. Defaults to "cmd.exe".
            logfolder (str, optional): The path to the folder where log files will be stored. If not provided, the current working directory will be used.
            working_dir (str, optional): The path to the working directory for the executed command. If not provided, the current working directory will be used.
            execution_policy (Literal["AllSigned", "Bypass", "Default", "RemoteSigned", "Restricted", "Undefined", "Unrestricted"], optional): The execution policy for PowerShell. Defaults to "Unrestricted".
            arguments (Union[str, list, tuple], optional): The arguments to be passed to the executable file. Defaults to ().
            WhatIf (str, optional): The WhatIf parameter for the executed command. Defaults to "".
            Verb (str, optional): The Verb parameter for the executed command. Defaults to "".
            UseNewEnvironment (str, optional): The UseNewEnvironment parameter for the executed command. Defaults to "".
            Wait (str, optional): The Wait parameter for the executed command. Defaults to "".
            stdinadd (str, optional): The stdinadd parameter for the executed command. Defaults to "".
            RedirectStandardInput (str, optional): The RedirectStandardInput parameter for the executed command. Defaults to "".
            WindowStyle (Literal["Hidden", "Maximized", "Minimized", "Normal"], optional): The WindowStyle parameter for the executed command. Defaults to "Normal".
            stdout_sleep (int, optional): The sleep duration for the stdout reader thread. Defaults to 0.
            stderr_sleep (int, optional): The sleep duration for the stderr reader thread. Defaults to 0.
            stdout_print (bool, optional): Whether to print the stdout output. Defaults to True.
            stderr_print (bool, optional): Whether to print the stderr output. Defaults to True.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.WindowStyle = WindowStyle
        if logfolder is None:
            self.logfolder = os.getcwd()
        else:
            self.logfolder = logfolder
        if not os.path.exists(self.logfolder):
            os.makedirs(self.logfolder)
        self.timestam = get_timest()
        self.tmpfilestderr_long = os.path.join(
            self.logfolder, f"stdout_{self.timestam}.txt"
        )
        self.tmpfilestdout_long = os.path.join(
            self.logfolder, f"stderr_{self.timestam}.txt"
        )
        touch(self.tmpfilestderr_long)
        touch(self.tmpfilestdout_long)
        if WhatIf:
            self.WhatIf = f" {WhatIf} "
        else:
            self.WhatIf = ""
        if Verb:
            self.Verb = f" {Verb} "
        else:
            self.Verb = ""
        if UseNewEnvironment:
            self.UseNewEnvironment = f" {UseNewEnvironment} "
        else:
            self.UseNewEnvironment = ""
        if Wait:
            self.Wait = f" {Wait} "
        else:
            self.Wait = ""
        if stdinadd:
            self.stdinadd = f" {stdinadd} "
        else:
            self.stdinadd = ""
        if RedirectStandardInput:
            self.RedirectStandardInput = f" {RedirectStandardInput} "
        else:
            self.RedirectStandardInput = ""
        if working_dir is None:
            self.working_dir = os.getcwd()
        else:
            self.working_dir = working_dir
        self.arguments = arguments
        self.updatedargumentsstr = escapecmdlist(self.arguments)
        self.executable = executable
        self.FilePath = get_short_path_name(self.executable)

        touch(self.tmpfilestderr_long)
        touch(self.tmpfilestdout_long)
        self.tmpfilestderr_short = get_short_path_name(self.tmpfilestderr_long)
        self.tmpfilestdout_short = get_short_path_name(self.tmpfilestdout_long)
        os.makedirs(self.working_dir, exist_ok=True)
        self.DIR = get_short_path_name(self.working_dir)
        os.chdir(self.DIR)
        self.execution_policy = execution_policy
        self.cmdfinish_unicode = r"""set endstrxxx=XXXXCOMMANDFINISHYYYY
call set endstrxxx=%endstrxxx:YYYY=%XXXX
echo %endstrxxx%
echo %endstrxxx% 1>&2
        """.strip()
        self.cmdfinish_bytes = self.cmdfinish_unicode.encode("utf-8")
        self.finaloutput_bytes = b"XXXXCOMMANDFINISHXXXX"
        self.finaloutput_unicode = self.finaloutput_bytes.decode("utf-8")
        self.wholecommandline = f"""powershell.exe -ExecutionPolicy {self.execution_policy} Start-Process -FilePath {self.FilePath}{self.WhatIf}{self.Verb}{self.UseNewEnvironment}{self.Wait}{self.stdinadd} -ArgumentList {self.updatedargumentsstr} -RedirectStandardOutput {self.tmpfilestdout_short} -RedirectStandardError {self.tmpfilestderr_short} -WorkingDirectory {self.DIR} -WindowStyle {self.WindowStyle}"""
        self._proc = subprocess.Popen(
            self.wholecommandline,
            cwd=self.DIR,
            env=os.environ.copy(),
            shell=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **invisibledict,
        )
        self.original_sleepdata = stdout_sleep, stderr_sleep, stdout_print, stderr_print
        self._start_read_threads(stdout_sleep, stderr_sleep, stdout_print, stderr_print)

    def _start_read_threads(
        self, stdout_sleep, stderr_sleep, stdout_print, stderr_print
    ):
        time.sleep(3)
        self.stdout_list = []
        self.stderr_list = []
        self.stdout_sleep = [stdout_sleep]
        self.stderr_sleep = [stderr_sleep]
        self.stderr_file = self.tmpfilestderr_short
        self.stdout_file = self.tmpfilestdout_short
        self.stdout_stoptrigger = [False]
        self.stderr_stoptrigger = [False]
        self.stdout_print = [stdout_print]
        self.stderr_print = [stderr_print]
        self.thread_being_executed = ExecuteAsThreadedTask(
            fu=run_main,
            kwargs={
                "so_list": self.stdout_list,
                "se_list": self.stderr_list,
                "so_file": self.stdout_file,
                "se_file": self.stderr_file,
                "so_sleep": self.stdout_sleep,
                "se_sleep": self.stderr_sleep,
                "so_stoptrigger": self.stdout_stoptrigger,
                "se_stoptrigger": self.stderr_stoptrigger,
                "so_print": self.stdout_print,
                "se_print": self.stderr_print,
            },
        )
        self.thread_being_executed()

    def __str__(self):
        return str(self._proc)

    def __repr__(self):
        return repr(self._proc)

    def __getattr__(self, key):
        if hasattr(self._proc, key):
            return getattr(self._proc, key)

    def sendcommand(self, cmd, **kwargs):
        r"""
        Sends a command to the subprocess and returns the stdout and stderr outputs.

        Args:
            cmd (str or bytes): The command to send to the subprocess.
            **kwargs: Additional keyword arguments to be passed to the subprocess.Popen constructor.

        Returns:
            tuple: A tuple containing the stdout and stderr outputs as byte arrays.

        Raises:
            Exception: If there is an error connecting to the subprocess.

        """
        while self.stdout_list:
            try:
                self.stdout_list.pop(0)
            except Exception:
                pass
        while self.stderr_list:
            try:
                self.stderr_list.pop(0)
            except Exception:
                pass

        if isinstance(cmd, str):
            cmd2send = cmd + "\n" + self.cmdfinish_unicode + "\n"
            cmd2send = cmd2send.encode("utf-8")
        else:
            cmd2send = cmd + b"\n" + self.cmdfinish_bytes + b"\n"

        stdout_result, stderr_result = [], []
        try:
            self._proc.stdin.flush()
            self._proc.stdin.write(cmd2send)
            self._proc.stdin.flush()
            time.sleep(0.050)
        except Exception as ef:
            errwrite(ef)
            sys.stderr.write("Connection lost... Reconnecting")
            self.stdout_stoptrigger[0] = True
            self.stderr_stoptrigger[0] = True
            time.sleep(5)
            self.thread_being_executed.killthread()
            time.sleep(5)
            try:
                self._proc.stdin.flush()
                self._proc.stdin.close()
            except Exception:
                errwrite(ef)
            try:
                self._proc.stdout.flush()
                self._proc.stdout.close()
            except Exception:
                errwrite(ef)

            try:
                self._proc.stderr.flush()
                self._proc.stderr.close()
            except Exception:
                errwrite(ef)
            try:
                self._proc.wait(timeout=1)
            except Exception:
                errwrite(ef)
            try:
                self._proc.terminate()
            except Exception:
                errwrite(ef)
            time.sleep(15)
            self._proc = subprocess.Popen(
                self.wholecommandline,
                cwd=self.DIR,
                env=os.environ.copy(),
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **invisibledict,
            )
            self._start_read_threads(*self.original_sleepdata)
            self._proc.stdin.write(cmd2send)
            self._proc.stdin.flush()
            time.sleep(0.050)
        stdout_result.append(b"")
        stderr_result.append(b"")
        while self.stdout_list:
            try:
                stdout_result.append(self.stdout_list.pop(0))
            except Exception:
                pass
            if len(self.stdout_list) == 0:
                time.sleep(0.50)
            try:
                if self.finaloutput_unicode in self.stdout_list[-1]:
                    break
            except Exception:
                pass
        while self.stderr_list:
            try:
                stderr_result.append(self.stderr_list.pop(0))
            except Exception:
                pass
            if len(self.stderr_list) == 0:
                time.sleep(0.50)
            try:
                if self.finaloutput_unicode in self.stderr_list[-1]:
                    break
            except Exception:
                pass
        stdoutcut = 0
        for line in stdout_result[1:]:
            if (
                b"XXXXCOMMANDFINISHYYYY" in line
                if isinstance(line, bytes)
                else "XXXXCOMMANDFINISHYYYY" in line
            ):
                break
            else:
                stdoutcut = stdoutcut + 1
        stderrcut = 0
        for line in stderr_result[1:]:
            if (
                b"XXXXCOMMANDFINISHYYYY" in line
                if isinstance(line, bytes)
                else "XXXXCOMMANDFINISHYYYY" in line
            ):
                break
            else:
                stderrcut = stderrcut + 1
        return stdout_result[1:stdoutcut], stderr_result[1:stderrcut]
