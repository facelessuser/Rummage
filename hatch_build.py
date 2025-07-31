"""Dynamically define some metadata."""
import os
import sys
from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def get_version_dev_status(root):
    """Get version_info without importing the entire module."""

    import importlib.util

    path = os.path.join(root, 'rummage', 'lib', '__meta__.py')
    spec = importlib.util.spec_from_file_location("__meta__", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version_info__._get_dev_status()


def get_requirements(root, requirements):
    """Load list of dependencies."""

    install_requires = []
    with open(os.path.join(root, requirements)) as f:
        install_requires = [line.strip() for line in f if not line.startswith("#")]
    return install_requires


class CustomMetadataHook(MetadataHookInterface):
    """Our metadata hook."""

    PLUGIN_NAME = 'custom'

    def update(self, metadata):
        """See https://ofek.dev/hatch/latest/plugins/metadata-hook/ for more information."""

        metadata["dependencies"] = get_requirements(self.root, "requirements/project.txt")
        metadata['optional-dependencies'] = {'extras': get_requirements(self.root, "requirements/extras.txt")}
        metadata["classifiers"] = [
            f"Development Status :: {get_version_dev_status(self.root)}",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Text Processing :: Filters",
            "Topic :: Text Processing :: Markup :: HTML",
        ]
        metadata['gui-scripts'] = {
            'rummage': 'rummage.__main__:main',
            f'rummage{".".join([str(x)for x in sys.version_info[:2]])}': 'rummage.__main__:main'
        }


class CustomBuildHook(BuildHookInterface):
    """Custom build hook for Babel."""

    PLUGIN_NAME = 'custom'

    def initialize(self, version, build_data):
        """Build localization files."""

        # Lazily import in case hook is disabled but file is still loaded
        from babel.messages.frontend import compile_catalog

        compiled_catalog = compile_catalog()
        compiled_catalog.domain = 'rummage'
        compile_catalog.statistics = True
        compiled_catalog.directory = os.path.join(self.root, 'rummage', 'lib', 'gui', 'localization', 'locale')

        compiled_catalog.finalize_options()
        compiled_catalog.run()
