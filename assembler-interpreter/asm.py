import operator
import re
from functools import partial


class Interpreter(object):

    MATH_OPS = {
        "add": operator.add,
        "sub": operator.sub,
        "mul": operator.mul,
        "div": operator.floordiv,
    }

    COMPARE_OPS = {
        "ne": operator.ne,
        "e": operator.eq,
        "ge": operator.ge,
        "g": operator.gt,
        "le": operator.le,
        "l": operator.lt,
    }

    def __init__(self):
        self._heap = {}
        self._pc = 0
        self._pcstack = []
        self._program = []
        self._labels = {}
        self._compares = []
        self._output = ""

        def __mov(x, y):
            self._heap[x] = self._read_arg(y)
            return None

        def __inc(x):
            self._heap[x] += 1
            return None

        def __dec(x):
            self._heap[x] -= 1
            return None

        def __cmp(x, y):
            self._compares = [
                self._read_arg(x),
                self._read_arg(y),
            ]
            return None

        def __call(label):
            self._pcstack += [
                self._pc + 1,
            ]
            return self._labels[label]

        def __msg(*args):
            for arg in args:
                if arg.startswith("'"):
                    self._output += arg[1:-1]
                else:
                    self._output += str(self._heap[arg])
            return None

        self._instructions = {
            "mov": __mov,
            "inc": __inc,
            "dec": __dec,
            "jmp": lambda label: self._labels[label],
            "cmp": __cmp,
            "call": __call,
            "ret": lambda: self._pcstack.pop(),
            "msg": __msg,
            "end": lambda: -1,
        }

        def __imath(f, x, y):
            self._heap[x] = f(
                self._heap[x],
                self._read_arg(y),
            )
            return None

        for ins, f in self.MATH_OPS.items():
            self._instructions |= {
                ins: partial(__imath, f),
            }

        def __ijmp(f, label):
            return self._labels[label] if f(*self._compares) else None

        for ins, f in self.COMPARE_OPS.items():
            self._instructions |= {
                f"j{ins}": partial(__ijmp, f)
            }

    def _read_arg(self, x):
        try:
            return int(x)
        except ValueError:
            return self._heap[x]

    def parse_line(self, tokens):
        op, *args = tokens
        if op not in self._instructions:
            self._labels |= {
                op: len(self._program)
            }
            return

        opf = partial(
            self._instructions[op],
            *args,
        )
        self._program += [opf]

    def run(self):

        while self._pc < len(self._program):
            op = self._program[self._pc]
            jmp_pc = op()
            if jmp_pc is None:
                self._pc += 1
            else:
                self._pc = jmp_pc

            if self._pc == -1:
                return self._output

        return -1

def assembler_interpreter(program):

    program_tokens = []
    for line in program.splitlines():

        try:
            icomment = line.index(";")
            line = line[:icomment]
        except ValueError:
            pass

        line = line.strip()
        if not line:
            continue

        program_tokens += [
            list(
                filter(
                    None,
                    map(
                        lambda x: x.strip() if x is not None else None,
                        re.split(
                            r":|,|(\w+)|(\d+)|('[^']+')",
                            line,
                        ),
                    ),
                ),
            ),
        ]

    i = Interpreter()
    for token in program_tokens:
        i.parse_line(token)
    return i.run()