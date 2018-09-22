"""Copy changelog."""
from shutil import copyfile


def copy_changelog():
    """Copy changelog file to data folder."""

    copyfile('docs/src/markdown/changelog.md', 'rummage/lib/gui/data/changelog.md')


if __name__ == "__main__":
    copy_changelog()
