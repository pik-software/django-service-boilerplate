from os.path import join, dirname

__author__ = 'pahaz'

import os
import shutil
import subprocess

if not os.path.exists('.test'):
    os.mkdir('mkdir .test')

exec_file = join(dirname(__file__), '.test', 'go.cmd')

f = open(exec_file, 'w')
f.write("""
pushd "%~dp0"
rm -rf project-name
git clone https://github.com/pahaz/django-project-stub.git project-name
cd project-name
__data__\\venv\\Scripts\\easy_install.exe pillow
python setup.py
python helpers/mkvirtualenv.py
popd
""")
f.close()

print(exec_file)
subprocess.call([exec_file])