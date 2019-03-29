# -*- coding: utf-8 -*-
"""
Git hooks providing local CI

Copyright (C) 2018 The GRAND collaboration

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import ast
import glob
import json
import os
import re
import subprocess
import sys

try:
    import astor
except ImportError:
    astor = None

try:
    from pycodestyle import StyleGuide
except ImportError:
    StyleGuide = None

try:
    from .setup import system
except ImportError:
    from framework.setup import system

try:
    from framework.version import __version__, __git__
except ImportError:
    __version__ = "unknown"
    __git__ = {}

from . import PKG_FILE

__all__ = ["pre_commit", "prepare_commit_msg"]


def git(*args):
    """System git call"""
    command = "git " + " ".join(args)
    return system(command)


def get_top_directory():
    """Get the package top directory from git"""
    top = git("rev-parse", "--show-toplevel")
    return top.strip()


def count_lines_in(file_):
    """Count the number of code lines in a Python file"""

    with open(file_, "r") as f:
        lines = f.readlines()

    docmarker = None
    blank, comment, docstring, code = 4 * (0,)
    for line in lines:
        if docmarker is None:
            if (not line) or (line == os.linesep):
                blank += 1
            elif line[0] == "#":
                comment += 1
            else:
                index = line.find('"""')
                if index >= 0:
                    docmarker = '"""'
                    docstring += 1
                else:
                    index = line.find("'''")
                    if index >= 0:
                        docmarker = "'''"
                        docstring += 1
                if index == -1:
                    # This isn't a docstring neither, so it must be
                    # code finally
                    code += 1
                else:
                    index = line[index+3:].find(docmarker)
                    if index >= 0:
                        # This is a 1 line docstring
                        docmarker = None
        else:
            docstring += 1
            if docmarker in line:
                docmarker = None

    return blank, comment, docstring, code 


def count_lines(path):
    """Count the number of Python code lines, recursively"""

    def format(counts):
        return {"blank": counts[0], "comment": counts[1],
                "docstring": counts[2], "code": counts[3]}

    _, ext = os.path.splitext(path)
    if ext == ".py":
        return format(count_lines_in(path))

    counts = 4 * [0,]
    for root, dirs, files in os.walk(path):
        for file_ in files:
            _, ext = os.path.splitext(file_)
            if ext == ".py":
                c = count_lines_in(os.path.join(root, file_))
                for i, ci in enumerate(c):
                    counts[i] += ci
    return format(counts)


def check_style(path):
    """Check the conformity to PEP8"""

    if StyleGuide is not None:
        style_guide = StyleGuide(quiet=True)
        report = style_guide.check_files(paths=(path,))
        stats = [line.split(None, 2) for line in report.get_statistics()]
        return { "count": report.get_count(), "categories": stats }
    else:
        return { "count": None, "categories": None }


def gather_doc(package_dir, package_name):
    """Gather public objects and their associated docstrings"""

    # Container for documentation statistics
    statistics = {}

    def increment_tokens(path, count=1):
        """Helper function for updating the number of tokens"""
        try:
            data = statistics[path]
        except KeyError:
            data = {"tokens": {}, "n_errors": 0, "n_tokens": 0}
            statistics[path] = data

        data["n_tokens"] += count

    def register_error(path, tag, lineno, message):
        """Helper function for recording a doc error"""

        # Unpack the error data
        try:
            data = statistics[path]
        except KeyError:
            data = set([])
            tmp = {"tokens": {tag: [lineno, data]}, "n_errors": 0,
                   "n_tokens": 0}
            statistics[path] = tmp
        else:
            try:
                data = data["tokens"][tag]
            except KeyError:
                tmp = set([])
                data["tokens"][tag] = [lineno, tmp]
                data = tmp
            else:
                data = data[1]

        # Update the error data
        n = len(data)
        data.add(message)
        if len(data) > n:
            statistics[path]["n_errors"] += 1

    def get_doc(node):
        """Get the docstring of a node"""
        try:
            doc = ast.get_docstring(node, clean=True)
        except:
            return ""
        else:
            if doc is None:
                doc = ""
            return doc

    def get_docstr(nodes, index):
        """Try to get a docstring at the given index"""
        try:
            n = nodes[index]
        except IndexError:
            pass
        else:
            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Str):
                return n.value.s
        return ""

    re_section = re.compile(
        "{0:} *(\\w*) *[:]? *{0:} *---* *{0:}".format(os.linesep))
    re_arg = re.compile("([*]*\\w*) *[:]? *(.*)")

    def get_function_doc(path, prefix, node):
        """Parse a function or method docstring in numpy style"""

        # Initialise the function meta from the AST
        function_tag = prefix + node.name
        function_line = node.lineno
        docstr = get_doc(node)
        params = {}
        meta = {"parameters": params,
                "prototype": astor.to_source(node.args)[:-1]}
        args = node.args
        tags = [a.arg for i, a in enumerate(args.args)
                if (i > 0) or ((a.arg != "self") and (a.arg != "cls"))]
        tags += [a.arg for a in args.kwonlyargs]
        if args.vararg:
            tags.append("*" + args.vararg.arg)
        if args.kwarg:
            tags.append("**" + args.kwarg.arg)
        for tag in tags:
            params[tag] = None

        def validated():
            """Validate the doc data and return them"""
            if not docstr:
                register_error(path, function_tag, function_line,
                    "Missing description")
            increment_tokens(path)

            for name, value in meta["parameters"].items():
                if value is None:
                    register_error(path, function_tag, function_line,
                        "Undocumented parameter `{}`".format(name))
                increment_tokens(path)
            return docstr, meta

        # Parse the docstring
        sections = re_section.split(docstr)
        if len(sections) == 1:
            return validated()

        def get_items(body):
            lines = [line.strip() for line in body.split(os.linesep)]
            lines = tuple(filter(lambda x:len(x), lines))
            n = int(len(lines) / 2)
            return [lines[2 * i:2 * i + 2] for i in range(n)]

        docstr = [sections[0]]
        n = int((len(sections) - 1) / 2)
        for i in range(n):
            title, body = sections[2 * i + 1: 2 * i + 3]
            title = title.lower()
            if title == "parameters":
                items = get_items(body)
                args = meta[title]
                for item in items:
                    m = re_arg.match(item[0])
                    if m is None:
                        continue
                    name, types = m.groups()
                    if name in args:
                        args[name] = (types, item[1])
                    else:
                        increment_tokens(path)
                        register_error(path, function_tag, function_line,
                            "Unknown parameter `{}`".format(name))
            elif (title == "returns") or (title == "yields"):
                items = get_items(body)
                rets = []
                for item in items:
                    m = re_arg.match(item[0])
                    if m is None:
                        continue
                    name, types = m.groups()
                    if len(types) == 0:
                        name, types = types, name
                    rets.append((types, item[1], name))
                    increment_tokens(path)
                meta[title] = rets
            elif title == "raises":
                meta[title] = get_items(body)
                increment_tokens(path)
            else:
                docstr.append(os.linesep.join(
                    ("", title.capitalize(), len(title) * "-", body)))
        docstr = "".join(docstr)

        # Return the validated data
        return validated()

    def parse_assign(node):
        """Parse an ast.Assign node"""
        return ", ".join([t.id for t in node.targets])

    def gather_module(path, data, check_imports=False):
        """Gather module top level nodes"""

        with open(os.path.join(package_dir, path)) as f:
            module = ast.parse(f.read())

        doc = ast.get_docstring(module, clean=True)
        if doc is not None:
            doc = doc.split(
                "\n\nCopyright (C) 2018 The GRAND collaboration", 1)[0]
        data["doc"] = doc

        classes, definitions, functions, imports = {}, {}, {}, {}
        data["classes"] = classes
        data["definitions"] = definitions
        data["functions"] = functions
        data["imports"] = imports
        data["path"] = path

        for index, node in enumerate(module.body):
            docstr = None

            # Check the object type
            if isinstance(node, ast.ClassDef):
                bases = [astor.to_source(b)[:-1] for b in node.bases]
                bases = [b for b in bases if b != "object"]

                meths, attrs = {}, {}
                extra = {"attributes": attrs, "methods": meths, "bases": bases}
                for i, subnode in enumerate(node.body):
                    if isinstance(subnode, ast.FunctionDef):
                        doc, meta = get_function_doc(
                            path, node.name + ".", subnode)
                        meths[subnode.name] = (subnode.lineno, doc, meta)
                    elif isinstance(subnode, ast.Assign):
                        name = parse_assign(subnode)
                        doc = get_docstr(node.body, i+1)
                        if not doc:
                            register_error(path, node.name, node.lineno,
                                "Undocumented attribute `{}`".format(name))
                        increment_tokens(path)
                        attrs[name] = (subnode.lineno, doc, None)

                container, name = classes, node.name
            elif isinstance(node, ast.FunctionDef):
                docstr, extra = get_function_doc(path, "", node)
                container, name = functions, node.name
            elif isinstance(node, ast.Assign):
                name = parse_assign(node)
                if name == "__all__":
                    data[name] = [a.s for a in node.value.elts]
                    continue
                extra = None
                docstr = get_docstr(module.body, index + 1)
                container = definitions
            elif check_imports and isinstance(node, ast.ImportFrom):
                # Skip global imports
                if node.level == 0:
                    continue

                # Create or get the container
                module_name = node.module if node.module is not None else ""
                try:
                    ii = imports[node.level]
                except KeyError:
                    i = []
                    imports[node.level] = {module_name: i}
                else:
                    try:
                        i = ii[module_name]
                    except KeyError:
                        i = []
                        ii[module_name] = i

                # Append the symbol and its alias to the liss of imports
                for a in node.names:
                    asname = a.asname
                    if asname is None:
                        asname = a.name
                    i.append((a.name, asname))
                continue
            else:
                continue

            if name.startswith("_"):
                continue

            if docstr is None:
                docstr = get_doc(node)
            if not docstr:
                register_error(path, name, node.lineno, "Missing description")
            increment_tokens(path)

            container[name] = (node.lineno, docstr, extra)


    # Parse the package and its submodules recursively
    def parse(path, data):
        # Gather the top level doc
        gather_module(os.path.join(path, "__init__.py"), data,
                      check_imports=True)

        # Gather sub modules
        modules = {}
        data["modules"] = modules

        abspath = os.path.join(package_dir, path)
        for filename in glob.glob(os.path.join(abspath, "*.py")):
            basename = os.path.basename(filename)
            if (basename == "__init__.py") or (basename == "version.py") or    \
                basename.startswith("_"):
                continue
            name, _ = os.path.splitext(basename)

            d = {}
            modules[name] = d
            gather_module(os.path.join(path, basename), d)

        for dirname in os.listdir(abspath):
            if not os.path.exists(
                os.path.join(abspath, dirname, "__init__.py")):
                continue

            d = {}
            modules[dirname] = d
            parse(os.path.join(path, dirname), d)

    # Generate the doc, starting from the top level
    data = {"statistics": statistics}
    parse(package_name, data)

    # Update the doc with local imports
    #
    def get_module(vpath):
        # Get a module given a vector path of module names
        module = data
        for name in vpath:
            try:
                module = module["modules"][name]
            except KeyError:
                return None
        return module

    def update_module(source_path):
        # Get the source module
        source = get_module(source_path)

        # Check for local imports in the source, i.e. `__init__.py`
        try:
            source_imports = source["imports"]
        except KeyError:
            return

        # Get the target module
        for level, iimps in source_imports.items():
            level = level - 1
            for module_name, imps in iimps.items():
                if level:
                    module_path = source_path[:-level]
                else:
                    module_path = source_path[:]
                module_path += module_name.split(".")

                module = get_module(module_path)
                if module is None:
                    continue

                # Expand start imports
                for (name, alias) in imps:
                    if name == "*":
                        try:
                            symbols = module["__all__"]
                        except KeyError:
                            symbols = list(module["classes"].keys()) +         \
                                      list(module["definitions"].keys()) +     \
                                      list(module["functions"].keys())
                        imps = [(s, s) for s in symbols]
                        break

                # Update the source module
                for (name, alias) in imps:
                    for category in ("classes", "definitions", "functions"):
                        if name in module[category]:
                            break
                    else:
                        continue
                    info = module[category][name]
                    source[category][alias] = (*info, module["path"])

        # Process the submodule(s)
        try:
            source_modules = source["modules"]
        except KeyError:
            return

        for module_name in source_modules.keys():
            update_module(source_path + [module_name])

    # Update the module data recursively
    update_module([])

    # Convert the statistics data to tuples, for JSON
    for _, outer in statistics.items():
        for _, inner in outer["tokens"].items():
            inner[1] = [v for v in inner[1]]

    return data


def _Informer():
    """Closure for a terminal logger"""
    max_length = [0]

    def inform(msg, end=False):
        n = len(msg)
        if n < max_length[0]:
            msg += (max_length[0] - n) * " "
        else:
            max_length[0] = n

        end = {True: "\r", False: ""}[end]
        print("\r" + msg, end=end)

    return inform


_inform = _Informer()
"""Log messages to the terminal""" 


def analyse_package(package_dir, stats):
    """Analyse the content of a package and dump its statistics"""

    package_name = stats["package"]["name"]
    path = os.path.join(package_dir, package_name)

    _inform("Counting lines ...")
    stats["lines"] = count_lines(path)

    _inform("Checking style ...")
    stats["pep8"] = check_style(path)

    _inform("Building the documentation ...")
    stats["doc"] = gather_doc(package_dir, package_name)

    _inform("Dumping framework info...")
    stats["framework"] = { "version": __version__, "git": __git__ }

    path = os.path.join(package_dir, PKG_FILE)
    with open(path, "w") as f:
        json.dump(stats, f)
        f.write(os.linesep)

    git("add", path)

    return stats


def update_readme(package_dir, stats):
    """Update the package README"""

    # Load the content of the user README file
    path = os.path.join(package_dir, "docs", "README.md")
    with open(path, "r") as f:
        readme = f.read()

    # Decorate the README
    preamble = [
"""\
<!--
    This file is auto generated by the GRAND framework.
    Beware: any change to this file will be overwritten at next commit.
    One should edit the docs/README.md file instead.
-->
"""]

    def add_badge(alt, link, pattern, image=None, shield=None):
        if shield:
            img = "https://img.shields.io/" + pattern.format(*shield)
        elif image:
            img = pattern.format(*image)
        else:
            img = pattern
        badge = "[![{:}]({:})]({:})".format(alt, img, link)
        preamble.append(badge)

    def colormap(score):
        colors = ("red", "orange", "yellow", "yellowgreen", "green",
                  "brightgreen")
        n = len(colors)
        index = int(n * score * 1E-02)
        index = min(n - 1, index)
        index = max(0, index)
        return colors[index]

    # PEP8 badge
    pkg_data = stats["package"]
    package_name, git_name, dist_name = map(lambda s: pkg_data[s],
                                            ("name", "git-name", "dist-name"))
    lines = stats["lines"]["code"]
    score = int(100. * (lines - stats["pep8"]["count"]) / float(lines))
    color = colormap(score)
    add_badge(
        "Coding style",
        "https://github.com/grand-mother/" + git_name +
            "/blob/master/docs/" + PKG_FILE,
        "badge/pep8-{:}%25-{:}.svg", shield=(score, color))

    # Code coverage badge
    base_url = "https://codecov.io/gh/grand-mother/"
    add_badge(
        "Code coverage",
        base_url + git_name,
        "{:}{:}/branch/master/graph/badge.svg", image=(base_url, git_name))

    # Travis badge
    base_url = "https://travis-ci.com/grand-mother/"  
    add_badge(
        "Build status",
        base_url + git_name,
        "{:}{:}.svg?branch=master", image=(base_url, git_name))

    n_tokens, n_errors = 0, 0
    for _, v in stats["doc"]["statistics"].items():
        n_tokens += v["n_tokens"]
        n_errors += v["n_errors"]

    if n_tokens:
        score = int(100. * (n_tokens - n_errors) / float(n_tokens))
    else:
        score = 100
    color = colormap(score)
    add_badge(
        "Documentation",
        "https://grand-mother.github.io/site/reports.html?" +
            git_name + "/docs",
        "badge/docs-{:}%25-{:}.svg", shield=(score, color))

    # PyPi badge
    add_badge(
        "PyPi version",
        "https://pypi.org/project/" + dist_name,
        "pypi/v/{:}.svg", shield=dist_name)

    path = os.path.join(package_dir, "README.md")
    with open(path, "w") as f:
        f.write(os.linesep.join(preamble))
        f.write(2 * os.linesep)
        f.write(readme)

    git("add", path)


def add_banner(msg):
    """Add a banner to git commit messages"""

    try:
        head, tail = msg.split("#", 1)
    except ValueError:
        return msg

    return """{:}\
# =================================================================
#      This commit has been analysed by grand-framework {:}
# =================================================================
#{:}
""".format(head, __version__, tail)


def pre_commit():
    """Git hook for pre-processing a commit"""

    package_dir = get_top_directory()

    # Check for a framework update
    _inform("Checking for a framework update...")
    path = os.path.join(package_dir, PKG_FILE)
    try:
        with open(path, "r") as f:
            stats = json.load(f)
    except FileNotFoundError:
        _inform("This is not a valid GRAND package. Aborting...")
        print()
        sys.exit(1)

    try:
        count = stats["framework"]["git"]["count"]
    except KeyError:
        pass
    else:
        if __git__["count"] < count:
            _inform("A framework update is required. Aborting...")
            print()
            sys.exit(1)

    # Update the stats
    analyse_package(package_dir, stats)

    # Update the package README
    _inform("Generating the README...")
    update_readme(package_dir, stats)

    # Exit back to the OS
    _inform("", end=True)
    sys.exit(0)


def prepare_commit_msg(file_=None):
    """Git hook for preparing the commit message"""
    if file_ is None:
        file_ = sys.argv[1]
    with open(file_, "r") as f:
        initial_msg = f.read()

    msg = add_banner(initial_msg)

    if msg is not initial_msg:
        with open(file_, "w") as f:
            f.write(msg)
    sys.exit(0)


if __name__ == "__main__":
    # Get the function to call from the command line
    ret = globals()[sys.argv[1]](*sys.argv[2:])
    if ret is not None:
        print(ret)
