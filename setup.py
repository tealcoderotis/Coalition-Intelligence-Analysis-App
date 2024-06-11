from cx_Freeze import setup, Executable
from sys import setrecursionlimit, getrecursionlimit

setrecursionlimit(getrecursionlimit() * 20)

build_exe_options = {
    "include_msvcr": True,
    "include_files": ["icon.ico", "config.json"],
    "excludes": ["PyQt5"]
}

setup(
    name="Coalition Intelligence Analysis App",
    version="1.0",
    description="Coalition Intelligence Analysis App",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base="console", target_name="Coalition Intelligence Analysis App", icon="icon.ico")],
)