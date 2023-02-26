import re


def diff(s):

    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b,
        "^": lambda a, b: a ** b,
    }

    funcs = {
        "cos": lambda x: {
            "op": "*",
            "left": {
                "const": -1,
            },
            "right": {
                "func": "sin",
                "arg": x,
            },
        },
        "sin": lambda x: {
            "func": "cos",
            "arg": x,
        },
        "tan": lambda x: {
            "op": "/",
            "left": {
                "const": 1,
            },
            "right": {
                "op": "^",
                "left": {
                    "func": "cos",
                    "arg": x,
                },
                "right": {
                    "const": 2,
                },
            },
        },
        "exp": lambda x: {
            "func": "exp",
            "arg": x,
        },
        "ln": lambda x: {
            "op": "/",
            "left": {
                "const": 1,
            },
            "right": x,
        },
    }

    def parse_op(tokens):

        if not tokens:
            raise ValueError()

        op = tokens.pop(0)

        if op in ops:
            return {
                "op": op,
                "left": parse_expression(tokens),
                "right": parse_expression(tokens),
            }
        elif op in funcs:
            return {
                "func": op,
                "arg": parse_expression(tokens),
            }
        else:
            raise ValueError()


    def parse_expression(tokens):

        c = tokens.pop(0)

        if c == "(":

            result = parse_op(tokens)

            if tokens.pop(0) != ")":
                raise ValueError()

            return result

        else:

            try:
                return {
                    "const": float(c),
                }
            except ValueError:
                pass

            return {
                "var": c,
            }


    def diff_tree(tree):

        if "func" in tree:
            return {
                "op": "*",
                "left": funcs[tree["func"]](tree["arg"]),
                "right": diff_tree(tree["arg"]),
            }
        elif "op" in tree:
            if tree["op"] in {"+", "-"}:
                return {
                    "op": tree["op"],
                    "left": diff_tree(tree["left"]),
                    "right": diff_tree(tree["right"]),
                }
            elif tree["op"] == "*":
                return {
                    "op": "+",
                    "left": {
                        "op": "*",
                        "left": diff_tree(tree["left"]),
                        "right": tree["right"],
                    },
                    "right": {
                        "op": "*",
                        "left": tree["left"],
                        "right": diff_tree(tree["right"]),
                    },
                }
            elif tree["op"] == "/":
                return {
                    "op": "/",
                    "left": {
                        "op": "-",
                        "left": {
                            "op": "*",
                            "left": diff_tree(tree["left"]),
                            "right": tree["right"],
                        },
                        "right": {
                            "op": "*",
                            "left": tree["left"],
                            "right": diff_tree(tree["right"]),
                        },
                    },
                    "right": {
                        "op": "^",
                        "left": tree["right"],
                        "right": {
                            "const": 2,
                        },
                    },
                }
            elif tree["op"] == "^":
                return {
                    "op": "*",
                    "left": tree["right"],
                    "right": {
                        "op": "^",
                        "left": tree["left"],
                        "right": {
                            "op": "-",
                            "left": tree["right"],
                            "right": {
                                "const": 1,
                            },
                        },
                    },
                }
        else:
            # diff x or constant
            return {
                "const": 1 if "var" in tree else 0,
            }

    def min_tree(tree):

        if "op" in tree:

            left = min_tree(tree["left"])
            right = min_tree(tree["right"])

            if "const" in left and "const" in right:
                return {
                    "const": ops[tree["op"]](
                        left["const"],
                        right["const"],
                    )
                }

            elif tree["op"] == "^" and "const" in right and right["const"] in {0, 1}:
                if right["const"] == 0:
                    return {
                        "const": 1,
                    }
                else:
                    return left
            elif tree["op"] == "*" and (("const" in left and left["const"] in {0, 1}) or ("const" in right and right["const"] in {0, 1})):
                if "const" in left:
                    if left["const"] == 0:
                        return {
                            "const": 0,
                        }
                    return right
                else:
                    if right["const"] == 0:
                        return {
                            "const": 0,
                        }
                    return left

            elif tree["op"] == "+" and (("const" in left and left["const"] == 0) or ("const" in right and right["const"] == 0)):

                if "const" in left:
                    return right
                else:
                    return left

            return {
                "op": tree["op"],
                "left": left,
                "right": right,
            }

        elif "func" in tree:
            return {
                "func": tree["func"],
                "arg": min_tree(tree["arg"]),
            }

        # const and var
        return tree

    def reorder_tree(tree):

        if "op" in tree and tree["op"] in {"+", "*"} and "const" in tree["right"]:

            return {
                "op": tree["op"],
                "left": tree["right"],
                "right": tree["left"],
            }

        return tree

    def minmuldiv_tree(tree):
        if "op" in tree and tree["op"] == "*" and "const" in tree["left"] and "op" in tree["right"] and tree["right"]["op"] == "/" and "const" in tree["right"]["left"]:
            return {
                "op": "/",
                "left": {
                    "const": tree["left"]["const"] * tree["right"]["left"]["const"],
                },
                "right": minmuldiv_tree(tree["right"]["right"]),
            }
        return tree

    def eval_tree(tree):
        if "func" in tree:
            return f"({tree['func']} {eval_tree(tree['arg'])})"
        elif "op" in tree:
            return f"({tree['op']} {eval_tree(tree['left'])} {eval_tree(tree['right'])})"
        elif "var" in tree:
            return f"{tree['var']}"

        return f"{tree['const']:g}"

    tokens = re.findall(r"(?:\d+\.\d+)|\w+|\(|\)|\+|-|\*|/|\^", s)
    tree = parse_expression(tokens)
    tree = diff_tree(tree)
    tree = min_tree(tree)
    tree = reorder_tree(tree)
    tree = minmuldiv_tree(tree)
    return eval_tree(tree)

print(
    # diff("(* 2 (/ 1 x))"),
    diff("(tan (* 2 x))"),
    # (* -1 (sin x))
    # (* -1 (sin 1))
)
