
env-create:
	mkdir -p env
	virtualenv -p `which python3.5` env/

pip-upgrade:
	pip install --upgrade pip

pip-save:
	pip freeze > requirements.txt

pip-install:
	pip install -r requirements.txt

# OSX users only

# We've installed your MySQL database without a root password. To secure it run:
#     mysql_secure_installation
#
# To connect run:
#     mysql -uroot
#
# To have launchd start mysql at login:
#   ln -sfv /usr/local/opt/mysql/*.plist ~/Library/LaunchAgents
# Then to load mysql now:
#   launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mysql.plist
# Or, if you don't want/need launchctl, you can just run:
#   mysql.server start
# ==> Summary
# 🍺  /usr/local/Cellar/mysql/5.7.10: 12,677 files, 433.2M