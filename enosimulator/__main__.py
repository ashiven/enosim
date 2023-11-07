import asyncio

from main import main


def entry_point():
    """
    The main entry point of the application.

    Will be used by the `enosimulator` command line script installed by setup.py
    """
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()
