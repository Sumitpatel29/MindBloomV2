import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindbloom.settings')
    from django.core.management import execute_from_command_line

    if len(sys.argv) == 1:
        execute_from_command_line([sys.argv[0], 'bootstrap_db'])
        execute_from_command_line([sys.argv[0], 'runserver', '0.0.0.0:5000'])
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
