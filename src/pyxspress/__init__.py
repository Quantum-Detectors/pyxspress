try:
    import importlib.metadata

    __version__ = importlib.metadata.version("pyxspress")
except ImportError:  # pragma: no cover
    # Not supported in Python <=3.7
    __version__ = "unknown"  # pragma: no cover


def get_module_version_string() -> str:
    """Get a nicely formatted string including the module version.

    Returns:
        str: Formatted string including module version
    """
    module_name_colour = "\033[36m"
    default_colour = "\033[0m"

    title_string = f"{module_name_colour}pyxspress{default_colour}"
    version_string = f"{module_name_colour}{__version__}{default_colour}"

    return (
        "===========================================\n"
        f"{title_string}\n"
        "===========================================\n"
        "Python module for generating Xspress Odin\n"
        "configuration and testing.\n\n"
        f"Module version: {version_string}\n\n"
        "Written by Quantum Detectors\n"
        "===========================================\n"
    )
