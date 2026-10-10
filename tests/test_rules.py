"""`RULES.md` is kept true: one place per fact.

The rules of the template are in one file at the root, each with an identifier such as
`BND-3`. This holds: an identifier cited anywhere in the repository is a rule that
exists; a rule is cited by the tests its `Held by:` line names, and by no other test, or
says `Not tested:` and why; a rule the template does not keep in full says
`Not kept yet:` and names the issue for it; no identifier is used twice; and the `spec/`
folder the rules came from is gone.

The logic is that of `tests/test_rules.py` in https://github.com/kostavo-oss/tools,
which holds every package there to its own `RULES.md`. Here there is one file, for the
one template, and the template's own files count as a place where a rule may be cited.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

#: A rule in `RULES.md`: `- **BND-3** — what must be true`.
RULE = re.compile(r"^- \*\*([A-Z]{2,5}-[0-9]+)\*\* — \S", re.MULTILINE)
#: Where a block of `RULES.md` ends: at the next item or the next heading.
NEXT = re.compile(r"^(?:- |#)", re.MULTILINE)
#: A test, as `Held by:` names it: `tests/test_template.py::test_it_is_written`.
TEST = re.compile(r"`(tests/[\w/]+\.py::[\w:]+)`")
#: What follows `Not kept yet:` in a rule the template does not keep in full: the issue.
OPEN = re.compile(r" #[0-9]+ — \S")
#: A pointer to the one file `RULES.md` replaces, or to one of its requirements by its
#: old number, `R1` to `R15`. Looked for in the documents and the tests only: the
#: template's files go to products, and may hold such a token of their own.
OLD_SPEC = re.compile(r"spec/README|\bR(?:1[0-5]|[1-9])\b")
#: The documents at the root that may cite a rule.
DOCUMENTS = ("RULES.md", "DECISIONS.md", "TRIED.md", "README.md", "CLAUDE.md")


def rules(text: str) -> list[tuple[str, str]]:
    """Every rule of `RULES.md`, in order: its identifier and its whole block."""
    found = []
    for match in RULE.finditer(text):
        after = NEXT.search(text, match.end())
        found.append(
            (match.group(1), text[match.start() : after.start() if after else None])
        )
    return found


def cited(text: str, areas: set[str]) -> set[str]:
    """The identifiers a text cites. Only the areas `RULES.md` has count, so that
    `UTF-8` is not taken for a rule."""
    if not areas:
        return set()
    pattern = rf"(?<![\w-])(?:{'|'.join(sorted(areas))})-[0-9]+(?![\w-])"
    return set(re.findall(pattern, text))


FUNCTION = (ast.FunctionDef, ast.AsyncFunctionDef)


def every_test(here: Path) -> dict[str, str]:
    """Every test of the repository, as `tests/<file>.py::<test>`, with its source."""
    found = {}
    for file in sorted((here / "tests").rglob("*.py")):
        text = file.read_text(encoding="utf-8")
        lines = text.splitlines()
        todo = [(f"{file.relative_to(here).as_posix()}::", ast.parse(text).body)]
        while todo:
            prefix, body = todo.pop()
            for node in body:
                if isinstance(node, ast.ClassDef):
                    todo.append((f"{prefix}{node.name}::", node.body))
                elif isinstance(node, FUNCTION) and node.name.startswith("test"):
                    # whole lines, so a comment at the end of one counts
                    source = lines[node.lineno - 1 : node.end_lineno]
                    found[prefix + node.name] = "\n".join(source)
    return found


def citing_files(here: Path) -> list[Path]:
    """Where a rule may be cited: the documents at the root, `copier.yml`, the tests,
    and the template, whose files must cite none that does not exist."""
    files = [here / name for name in (*DOCUMENTS, "copier.yml")]
    files += sorted((here / "tests").rglob("*.py"))
    files += sorted(p for p in (here / "template").rglob("*") if p.is_file())
    return [file for file in files if file.is_file()]


def problems(here: Path) -> list[str]:
    """What is wrong between `RULES.md` and the rest of the repository. Empty when the
    file is true."""
    wrong = []
    text = (here / "RULES.md").read_text(encoding="utf-8")
    found = rules(text)
    names = [name for name, _ in found]
    areas = {name.split("-")[0] for name in names}

    for name in sorted({name for name in names if names.count(name) > 1}):
        wrong.append(f"{name} is the identifier of more than one rule")
    for line in text.splitlines():
        if line.startswith("- **") and not RULE.match(line):
            wrong.append(f"not a rule as `- **AREA-1** — text`: {line}")

    for file in citing_files(here):
        where = file.relative_to(here).as_posix()
        body = file.read_text(encoding="utf-8", errors="replace")
        for name in sorted(cited(body, areas) - set(names)):
            wrong.append(f"{where} cites {name}, and RULES.md has no such rule")
        # This file names the old spec to look for it.
        documentation = where in DOCUMENTS or where.startswith("tests/")
        if documentation and where != "tests/test_rules.py" and OLD_SPEC.search(body):
            wrong.append(f"{where} cites the spec that is gone; cite a rule of RULES.md")
    if (here / "spec").exists():
        wrong.append("there is a spec/ folder beside RULES.md: one place per fact")

    tests = every_test(here)
    citing = {test: cited(source, areas) for test, source in tests.items()}
    for name, block in found:
        held = "Held by:" in block
        reason = re.search(r"^\s+Not tested: *(.*)", block, re.MULTILINE)
        # An open rule states the whole promise. It names the issue for the part the
        # template does not keep, and may name tests for the part it does.
        open_ = re.search(r"^\s+Not kept yet:(.*)", block, re.MULTILINE)
        if open_ and not OPEN.match(open_.group(1)):
            wrong.append(
                f"{name} says `Not kept yet:` and names no issue, as"
                " `Not kept yet: #12 — what happens instead`"
            )
        if (held and reason) or not (held or reason or open_):
            wrong.append(f"{name} needs `Held by:` or `Not tested:`, and one of them")
            continue
        named = set()
        if reason and len(reason.group(1).split()) < 3:
            wrong.append(f"{name} says `Not tested:` and not why")
        if held:
            named = set(TEST.findall(block.split("Held by:", 1)[1]))
            if not named:
                wrong.append(f"{name} says `Held by:` and names no test")
        for test in sorted(named):
            if test not in tests:
                wrong.append(f"{name} is held by {test}, and there is no such test")
            elif name not in citing[test]:
                wrong.append(f"{name} is held by {test}, which does not cite {name}")
        for test in sorted(
            t for t, ids in citing.items() if name in ids and t not in named
        ):
            wrong.append(
                f"{test} cites {name}, and {name} does not name it as `Held by:`"
            )
    return wrong


def test_the_rules_are_kept_true() -> None:
    assert rules((ROOT / "RULES.md").read_text(encoding="utf-8")), "no rule in RULES.md"
    assert problems(ROOT) == []


def test_every_document_of_the_one_place_per_fact_is_there() -> None:
    for name in DOCUMENTS:
        assert (ROOT / name).is_file(), f"{name} is gone: CLAUDE.md says what lives there"


# -- that the check bites: a made-up repository, broken once in each way ----------------

GOOD = {
    "RULES.md": (
        "# Rules\n\n## APP\n\n"
        "- **APP-1** — It is written.\n"
        "  Held by: `tests/test_app.py::test_it_is_written`,\n"
        "  `tests/test_app.py::TestMore::test_it_is_written_twice`.\n"
        "- **APP-2** — It names no customer.\n"
        "  Not tested: it is an absence.\n"
        "- **APP-3** — It is written for every answer.\n"
        "  Held by: `tests/test_app.py::test_it_is_written`.\n"
        "  Not kept yet: #12 — it is written for the default answers only.\n"
        "- **APP-4** — It mentions nothing that was not chosen.\n"
        "  Not kept yet: #13 — it mentions dbt.\n"
    ),
    "README.md": "It is written, UTF-8 and all: APP-1.\n",
    "copier.yml": "# APP-1 and APP-2.\n",
    # not a pointer to the old spec: a product's file may say R2 or R40 for its own ends
    "template/README.md.jinja": "# {{ project_name }}\n\nRegion R2, runtime R40.\n",
    "TRIED.md": "On a runner with 16 cores, R40 was not a requirement.\n",
    "tests/test_app.py": (
        "def test_it_is_written():\n"
        '    """APP-1, APP-3."""\n\n\n'
        "class TestMore:\n"
        "    def test_it_is_written_twice(self):\n"
        "        pass  # APP-1\n\n\n"
        "def test_something_else():\n"
        "    pass\n"
    ),
}


def made_up(tmp_path: Path, changed: dict[str, str]) -> Path:
    for name, text in {**GOOD, **changed}.items():
        file = tmp_path / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")
    return tmp_path


def test_a_made_up_repository_that_is_true_has_no_problems(tmp_path: Path) -> None:
    assert problems(made_up(tmp_path, {})) == []


RULES_MD = GOOD["RULES.md"]
TESTS_PY = GOOD["tests/test_app.py"]


@pytest.mark.parametrize(
    ("changed", "problem"),
    [
        pytest.param(
            {"copier.yml": "# APP-9.\n"},
            "copier.yml cites APP-9, and RULES.md has no such rule",
            id="a rule that does not exist is cited in copier.yml",
        ),
        pytest.param(
            {"TRIED.md": "See APP-12.\n"},
            "TRIED.md cites APP-12, and RULES.md has no such rule",
            id="a rule that does not exist is cited in a document",
        ),
        pytest.param(
            {"template/AGENTS.md.jinja": "See APP-7.\n"},
            "template/AGENTS.md.jinja cites APP-7, and RULES.md has no such rule",
            id="a rule that does not exist is cited in the template",
        ),
        pytest.param(
            {"tests/test_app.py": TESTS_PY.replace("APP-1, APP-3.", "APP-3.")},
            "APP-1 is held by tests/test_app.py::test_it_is_written, which does not cite"
            " APP-1",
            id="a test that is named does not cite its rule",
        ),
        pytest.param(
            {
                "tests/test_app.py": TESTS_PY.replace(
                    "def test_it_is_written()", "def test_it()"
                )
            },
            "APP-1 is held by tests/test_app.py::test_it_is_written, and there is no such"
            " test",
            id="a test that is named is not there",
        ),
        pytest.param(
            {"tests/test_app.py": TESTS_PY + '    """APP-2."""\n'},
            "tests/test_app.py::test_something_else cites APP-2, and APP-2 does not name"
            " it as `Held by:`",
            id="a test cites a rule that does not name it",
        ),
        pytest.param(
            {"RULES.md": RULES_MD.replace("  Not tested: it is an absence.\n", "")},
            "APP-2 needs `Held by:` or `Not tested:`, and one of them",
            id="a rule with no test and no reason",
        ),
        pytest.param(
            {"RULES.md": RULES_MD.replace("it is an absence", "no")},
            "APP-2 says `Not tested:` and not why",
            id="a rule that is not tested and does not say why",
        ),
        pytest.param(
            {"RULES.md": RULES_MD.replace("Not kept yet: #13 — it", "Not kept yet: it")},
            "APP-4 says `Not kept yet:` and names no issue, as"
            " `Not kept yet: #12 — what happens instead`",
            id="an open rule that names no issue",
        ),
        pytest.param(
            {
                "RULES.md": RULES_MD.replace(
                    "  Not kept yet: #13 — it mentions dbt.\n", ""
                )
            },
            "APP-4 needs `Held by:` or `Not tested:`, and one of them",
            id="a rule that is neither held, nor open, nor explained",
        ),
        pytest.param(
            {"RULES.md": RULES_MD.replace("**APP-2**", "**APP-1**")},
            "APP-1 is the identifier of more than one rule",
            id="an identifier used twice",
        ),
        pytest.param(
            {"RULES.md": RULES_MD.replace("**APP-2** —", "**APP-2**:")},
            "not a rule as `- **AREA-1** — text`: - **APP-2**: It names no customer.",
            id="a rule that is not written as one",
        ),
        pytest.param(
            {"spec/README.md": "# spec\n"},
            "there is a spec/ folder beside RULES.md: one place per fact",
            id="a spec folder beside the rules",
        ),
        pytest.param(
            {"README.md": "What was tried is in `spec/README.md`.\n"},
            "README.md cites the spec that is gone; cite a rule of RULES.md",
            id="a pointer to the spec that is gone",
        ),
        pytest.param(
            {"tests/test_app.py": TESTS_PY.replace("pass  # APP-1", "pass  # APP-1, R3")},
            "tests/test_app.py cites the spec that is gone; cite a rule of RULES.md",
            id="a requirement cited by its old number",
        ),
    ],
)
def test_each_way_the_rules_file_goes_stale_is_a_problem(
    tmp_path: Path, changed: dict[str, str], problem: str
) -> None:
    assert problem in problems(made_up(tmp_path, changed))
