from fast_common import *

def main():
    info = ToolsInfo(method="GET", url="/", name="initial_test", description="", callback=lambda : None)
    print("Hello from fast-common!")


if __name__ == "__main__":
    main()
