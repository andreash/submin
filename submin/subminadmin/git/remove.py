import os
import sys
import subprocess

from submin.models import options
from submin.models import repository

def run(reposname):
	reposdir = repository.directory('git', reposname)

	old_path = os.environ["PATH"]
	os.environ["PATH"] = options.value("env_path")
	cmd = 'rm -rf "%s"' % str(reposdir)
	(exitstatus, outtext) = subprocess.getstatusoutput(cmd)
	os.environ["PATH"] = old_path

	if exitstatus != 0:
		raise PermissionError(
			"External command '%s' failed: %s" % \
					(cmd, outtext))
