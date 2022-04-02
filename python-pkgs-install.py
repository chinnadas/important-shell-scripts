#!/usr/bin/env python

'''
This file is meant to setup your environment on AWS ec2 instance from a sample
config.json file.
'''

import os
import apt
import sys
import json
import subprocess
import shlex

# Open the environment configuration file
config_file = open('environments.json')
config = json.load(config_file)

if len(sys.argv[1:]) != 0:
  environment = sys.argv[1:][0]
  if environment not in config:
    sys.exit("ERROR\nPlease pass in a valid environment parameter, see the configuration.json.\nExample usage:\nsudo python setup.py development")
else:
  print("Please pass an argument, example usage: \n sudo python setup.py development")

def run(cmd, path=None):
  print('Running: '+cmd+'\n')
  p = subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=path)
  for line in iter(p.stdout.readline, b''):
      print(">>> " + line.rstrip())

def bash(cmd):
  print('Running: '+cmd+'\n')
  subprocess.Popen(cmd, shell=True)
def update():
  run('sudo apt-get update -y')
  run('sudo apt-get upgrade -y')
  run('sudo apt-get dist-upgrade -y')

def clean():
  run('sudo apt-get clean')
  run('sudo apt-get autoclean')
  run('sudo apt-get check')

clean()
update()

for repo in config[environment]["repos"]:
  run('sudo add-apt-repository ppa:' + repo + ' -y')
  update()

for pkg_name in config[environment]["pkgs"]:
  cache = apt.cache.Cache()
  cache.update()
  pkg = cache[pkg_name]

  if pkg.is_installed:
      print "{pkg_name} already installed".format(pkg_name=pkg_name)
  else:
      pkg.mark_install()

      try:
          cache.commit()
      except Exception, arg:
          print >> sys.stderr, "Sorry, package installation failed [{err}]".format(err=str(arg))

update()
clean()

print('\nCopy below and past to github/bitbucket:\n\n')
run('ssh-keygen -t rsa -b 4096 -N "" -f /home/ubuntu/.ssh/id_rsa')
run('cat /home/ubuntu/.ssh/id_rsa.pub')

raw_input('Copy and paste the key to github/bitbucket. Then press any key.')
raw_input('Press enter to clone.')

print('\n Configuring Git')
run('git config --global user.name '+ config[environment]["git"]["username"])
run('git config --global user.email '+ config[environment]["git"]["email"])

for repo in config[environment]["git"]["repos"]:
  run('git clone '+repo)

print('Installing gruntjs \n')
run('sudo npm install grunt-cli -g')
print('Installing compass \n')
run('gem install update')
run('gem install compass')
run('gem install sass-globbing')


#run('sudo /sbin/shutdown -r now')
