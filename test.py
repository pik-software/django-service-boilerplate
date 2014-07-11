from os.path import join, dirname

__author__ = 'pahaz'

import os
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
python setup.py
python helpers/mkvirtualenv.py
__data__\\venv\\Scripts\\activate
python manage.py syncdb --noinput
python manage.py runserver
popd
""")
f.close()

print(exec_file)
subprocess.call([exec_file])