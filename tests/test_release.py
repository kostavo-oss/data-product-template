"""A release is a tag, and copier takes it: what a tag promises, held with a template
that is a git repository in a temporary folder. No network, no workspace.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from conftest import BARE, REPO
from copier import run_copy, run_update
from copier.errors import UserMessageError

GIT = ["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid"]
NEXT = "# what main has since the release"
#: A version's section in the changelog: `## [0.1.0]`.
SECTION = re.compile(r"^## \[([^\]]+)\]\s*$", re.MULTILINE)
VERSION = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def git(folder: Path, *words: str) -> str:
    done = subprocess.run(
        [*GIT, *words], cwd=folder, check=True, capture_output=True, text=True
    )
    return done.stdout.strip()


def commit(folder: Path, message: str, tag: str | None = None) -> None:
    git(folder, "add", ".")
    git(folder, "commit", "-q", "-m", message)
    if tag:
        git(folder, "tag", tag)


def change(source: Path) -> None:
    """The template's next change: a line more in the product's `mise.toml`."""
    with (source / "template" / "mise.toml.jinja").open("a") as file:
        file.write(f"\n{NEXT}\n")


def made_from(product: Path) -> str:
    answers = yaml.safe_load((product / ".copier-answers.yml").read_text())
    return answers["_commit"]


def test_copier_takes_the_newest_release_and_not_what_main_has_since(template, tmp_path):
    """`copier copy` with no `--vcs-ref` writes the product from the newest tag and
    records it. A pre-release tag is not a release. `--vcs-ref` names another."""
    # Holds REL-1.
    source = Path(shutil.copytree(template, tmp_path / "template"))
    git(source, "init", "-q", "-b", "main")
    commit(source, "the first release", tag="v0.1.0")
    change(source)
    commit(source, "a pre-release of the next", tag="v0.2.0a1")
    change(source)
    commit(source, "not released")
    commit_of_main = git(source, "rev-parse", "HEAD")

    released = tmp_path / "released"
    run_copy(str(source), str(released), data=BARE, defaults=True, quiet=True)
    assert made_from(released) == "v0.1.0"
    assert NEXT not in (released / "mise.toml").read_text()

    ahead = tmp_path / "ahead"
    run_copy(
        str(source), str(ahead), data=BARE, defaults=True, quiet=True, vcs_ref="main"
    )
    assert (ahead / "mise.toml").read_text().count(NEXT) == 2
    assert made_from(ahead) != "v0.1.0"
    assert commit_of_main.startswith(made_from(ahead).split("-g")[-1])


def test_an_update_goes_from_the_release_a_product_has_to_the_newest(template, tmp_path):
    """Also for a product that was made before there was any tag. A product with
    changes that are not committed is refused."""
    # Holds REL-1.
    source = Path(shutil.copytree(template, tmp_path / "template"))
    git(source, "init", "-q", "-b", "main")
    commit(source, "before any release")

    product = tmp_path / "product"
    run_copy(str(source), str(product), data=BARE, defaults=True, quiet=True)
    git(product, "init", "-q", "-b", "main")
    commit(product, "made from the template")
    assert not made_from(product).startswith("v")

    change(source)
    commit(source, "the first release", tag="v0.1.0")
    (product / "notes.txt").write_text("not committed\n")
    with pytest.raises(UserMessageError, match="dirty"):
        run_update(str(product), defaults=True, overwrite=True, quiet=True)
    (product / "notes.txt").unlink()
    run_update(str(product), defaults=True, overwrite=True, quiet=True)
    commit(product, "the first release")
    assert made_from(product) == "v0.1.0"
    assert (product / "mise.toml").read_text().count(NEXT) == 1

    change(source)
    commit(source, "the second release", tag="v0.2.0")
    change(source)
    commit(source, "not released")
    run_update(str(product), defaults=True, overwrite=True, quiet=True)
    assert made_from(product) == "v0.2.0"
    assert (product / "mise.toml").read_text().count(NEXT) == 2


def test_the_changelog_has_a_section_for_every_release_newest_first():
    """`[Unreleased]` stands first, then the versions, each once, the newest first. The
    README names a version the changelog has."""
    # Holds REL-2.
    text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    first, *versions = SECTION.findall(text)

    assert first == "Unreleased"
    assert versions, "no version in CHANGELOG.md"
    for version in versions:
        assert VERSION.match(version), f"{version} is not <major>.<minor>.<patch>"
    numbers = [tuple(int(part) for part in version.split(".")) for version in versions]
    assert numbers == sorted(set(numbers), reverse=True)
    for section in re.split(SECTION, text)[4::2]:
        assert re.search(r"^- \S", section, re.MULTILINE), "a release that says nothing"

    readme = (REPO / "README.md").read_text(encoding="utf-8")
    named = set(re.findall(r"--vcs-ref v([0-9]+\.[0-9]+\.[0-9]+)", readme))
    assert named == {versions[0]}
