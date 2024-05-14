"""
    Slang -- A simple scripting language
    Copyright (C) 2024  Butterroach

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import math
import os
import sys
import inspect
from typing import Callable  # I LOVE TYPE HINTING I LOVE TYPE HINTING YES YES

os.system("")

linec = 0

__version__ = "2.0.0-alpha"


class SlangError(Exception):
    pass


class NoSuchFunction(SlangError):
    """
    [msg] function does not exist
    """


class NoSuchVariable(SlangError):
    """
    No variable named [msg]
    """


def split_args(text):
    words = []
    current_word = ""
    in_quotes = False
    escape_next = False

    for char in text:
        if char == "\\":
            if escape_next:
                current_word += char
                escape_next = False
            else:
                escape_next = True
        elif char == '"':
            if escape_next:
                current_word += char
                escape_next = False
            elif in_quotes:
                if current_word:
                    words.append(current_word)
                current_word = ""
                in_quotes = False
            else:
                in_quotes = True
        elif char == " ":
            if in_quotes:
                current_word += char
            elif current_word:
                words.append(current_word.strip('"'))
                current_word = ""
        else:
            current_word += char

    if current_word:
        words.append(current_word.strip('"'))

    words = [word.replace("\\\\", "\\") for word in words]

    return words


def process_function_calls(code: str, functions: list[tuple[str, Callable]]):
    global linec
    function_names = [function[0] for function in functions]
    for line in code.splitlines():
        if not line.split():
            linec += 1
            continue
        lout = process_single_line(line, function_names, functions)
        if lout != None:
            print(lout)
        linec += 1


def process_single_line(
    line: str, function_names: list[str], functions: list[tuple[str, Callable]]
):
    # TODO this fucking btich
    # ^ i dont remember what this is about and im too scared to touch that todo
    # print("reading line")
    if line == "exit":
        os._exit(0)
    wompwomp = True
    for i, function_name in enumerate(function_names):
        # print("checking line for functions")
        if line.startswith(function_name):
            wompwomp = False
            # print("function found!", function_name)
            args: list[str] = split_args(line.replace(f"{function_name} ", "", 1))
            internalfunction = functions[i][1]
            # print("converting args to correct types")
            restannotate = None
            unannotatedargs = args.copy()
            for i, annotate, argname in zip(
                range(len(internalfunction.__annotations__.values())),
                internalfunction.__annotations__.values(),
                inspect.signature(internalfunction).parameters.values(),
            ):
                # print(i, annotate, argname)
                if str(argname).startswith("*"):
                    restannotate = annotate
                    break
                if args[i].startswith("$"):
                    orig_var = args[i]
                    args[i] = slang_vars.get(args[i].replace("$", ""))
                    if args[i] is None:
                        raise NoSuchVariable(orig_var)
                args[i] = annotate(args[i])
                unannotatedargs.pop(0)
                # print(f"converted to {type(args[i])} successfully!")
            if restannotate is not None:
                i = 0
                for _ in unannotatedargs:
                    args.remove(unannotatedargs[i])
                    if unannotatedargs[i].startswith("$"):
                        orig_var = unannotatedargs[i]
                        unannotatedargs[i] = slang_vars.get(
                            unannotatedargs[i].replace("$", "")
                        )
                        if unannotatedargs[i] is None:
                            raise NoSuchVariable(orig_var)
                    unannotatedargs[i] = restannotate(unannotatedargs[i])
                    i += 1
            if unannotatedargs and args != unannotatedargs:  # how does this even happen
                return internalfunction(*(args + unannotatedargs))
            return internalfunction(*args)
    if wompwomp:
        raise NoSuchFunction(line.split(" ")[0])


def add(x: float, y: float):
    return x + y


def subtract(x: float, y: float):
    return x - y


def multiply(x: float, y: float):
    return x * y


def divide(x: float, y: float):
    return x / y


def slang_print(prints: str = ""):
    return prints


def slang_sin(x: float):
    # why do i have to do this
    return math.sin(x)


def slang_cos(x: float):
    return math.cos(x)


def slang_asin(x: float):
    return math.asin(x)


def slang_acos(x: float):
    return math.acos(x)


def con(*str1: str):
    return "".join(str1)


def slang_exit(code: int):
    os._exit(code)


def define_var_str(var_name: str, var_value: str):
    slang_vars[var_name] = var_value


def define_var_int(var_name: str, var_value: int):
    slang_vars[var_name] = var_value


def define_var_float(var_name: str, var_value: float):
    slang_vars[var_name] = var_value


def define_var_fun(var_name: str, *var_value: str):
    slang_vars[var_name] = process_single_line(
        " ".join(var_value), [function[0] for function in functions], functions
    )


slang_vars = {}
functions = [
    ("add", add, "Adds two numbers."),
    ("sub", subtract, "Subtracts two numbers."),
    ("mul", multiply, "Multiplies two numbers."),
    ("div", divide, "Divides two numbers."),
    ("print", slang_print, "Prints output."),
    ("var str", define_var_str),
    ("var int", define_var_int),
    ("var float", define_var_float),
    ("var fun", define_var_fun),
    ("sin", slang_sin, "Calculates sine of x radians."),
    ("cos", slang_cos, "Calculates cosine of x radians."),
    (
        "con",
        con,
        "Concatenates 2 strings together.",
    ),
    ("asin", slang_asin, "Calculates the arc sine."),
    ("acos", slang_acos, "Calculates the arc cosine."),
    (
        "exit",
        slang_exit,
        "Exits the program. The function itself needs an exit code, but you can still type in no exit code because of how this stupid thing works.",
    ),
    ("#", lambda *x: None, "it's a comment......."),
    (
        "exec_py",
        lambda x: exec(x),
        "Executes Python code using Python's built-in exec.",
    ),
    (
        "eval_py",
        lambda x: eval(x),
        "Evaluates a Python expression using Python's built-in eval.",
    ),
]


def replace_error_msg(e: SlangError, code: str):
    return type(e).__doc__.replace("[msg]", str(e))


if __name__ == "__main__" and (
    len(sys.argv) < 2
    or (
        len(sys.argv) == 2
        and (sys.argv[1] in ("--shh", "-s") if len(sys.argv) > 1 else True)
    )
):
    if "--shh" not in sys.argv and "-s" not in sys.argv:
        print(f"Slang v{__version__}")
        print()
        print(
            "This program is licensed under the GNU AGPL-v3 license (apparently I can't put it under the GPL now)."
        )
        print(
            "You should have received a copy of the GNU Affero General Public License along with this program. If not, see https://www.gnu.org/licenses/"
        )
        print(
            "You can use the --shh (or -s) argument to make this not appear when you start the interactive shell."
        )
        print()
    while True:
        code = input(">")
        try:
            process_function_calls(code, functions)
        except SlangError as e:
            print(code)
            print(f"\u001b[31mERROR! {replace_error_msg(e, code)}\u001b[0m")
        except Exception as e:
            # print(f"\u001b[31mUH OH! PYTHON ERROR!\t{type(e).__name__}: {e}\u001b[0m")
            raise e

if __name__ == "__main__" and len(sys.argv) > 1:
    try:
        with open(sys.argv[1], "r") as f:
            fread = f.read()
    except FileNotFoundError:
        print("that file doesn't exist dumbass")
        os._exit(1)
    try:
        process_function_calls(fread, functions)
    except SlangError as e:
        print(
            f"\u001b[1m\u001b[31mLINE {linec+1}: \u001b[0m\u001b[4m\u001b[32m{fread.splitlines()[linec]}\u001b[0m"
        )
        print(
            f"\u001b[1m\u001b[31mERROR! {replace_error_msg(e, fread.splitlines()[linec])}\u001b[0m"
        )
