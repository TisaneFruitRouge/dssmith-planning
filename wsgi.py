import sys

sys.path.insert(0, '/var/www/planning/venv/lib/python3.6/site-packages')
sys.path.append("/var/www/planning")

from planning.app import app as application

print(application.__dict__)

if __name__=="__main__":

	application.run()
