from ui import create_ui
from core import TaskManager


def main():
    task_manager = TaskManager()
    create_ui(task_manager)


if __name__ == "__main__":
    main()
