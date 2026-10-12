"""Default build entry point for the current diagnostic suite."""
from build_suite import main
if __name__ == "__main__":
    main()
    from build_home_rom import build
    build()
