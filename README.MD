
## rlogfi provides a way to interact with PowerShell subprocesses in a detached and asynchronous manner

## pip install rlogfi

### Tested against Windows 10 / Python 3.11 / Anaconda / BlueStacks

### Asynchronous I/O: 
By using asyncio and aiofiles, the script can perform I/O operations asynchronously, allowing for more efficient handling of multiple subprocess streams simultaneously. This can be particularly useful when dealing with long-running commands or when responsiveness is crucial. It also helps to avoid deadlocks, since Start-Process allows the redirection of stdout/stdin: -RedirectStandardOutput / -RedirectStandardError 

### Detached Execution: 
The script creates a detached subprocess for running PowerShell commands, which means it operates independently of the parent process. This can be advantageous in scenarios where you need to run commands in the background or interact with PowerShell without blocking the main Python program. Instead of cmd.exe, you can start any other app that loops forever (e.g., a proxy server). The process won't close when Python closes.

### Error Handling and Reconnection: 
The script includes error handling mechanisms to handle exceptions and reconnect to the subprocess if the connection to stdin is lost. This ensures robustness in scenarios where the subprocess may encounter issues or terminate unexpectedly.

### Customization and Control: 
The class structure allows for customization of various parameters such as execution policy, working directory, and output redirection. Users can tailor the behavior of the subprocess to suit their specific requirements.

```py 
from rlogfi import PowerShellDetachedInteractive

interactivepwsh = PowerShellDetachedInteractive(
    executable=r"c:\windows\system32\cmd.exe",
    logfolder="c:\\newlogggg",
    working_dir=None,
    execution_policy="Unrestricted",
    arguments=["dir", "c:\\Windows"],
    WhatIf="",
    Verb="",
    UseNewEnvironment="",
    Wait="",
    stdinadd="",
    WindowStyle="Hidden",
)

# executing commandos 
stdout, stderr = interactivepwsh.sendcommand("dir")
print(stdout, stderr)
so, se = interactivepwsh.sendcommand("netstat")
so, se = interactivepwsh.sendcommand("cd\\")
so, se = interactivepwsh.sendcommand("ls")
```