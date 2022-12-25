import os
import subprocess

os.chdir("tester")
subprocess.run(['python', 'tester.py', 'solution_task02.py', 'task02'])

# """
# a = list(map(int, input().split()))
# print(*[i for i in a if i < 5])
# """
