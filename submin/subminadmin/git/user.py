import os
import sys
import pprint

from submin.models import permissions
from submin.models import repository
from submin.models import options
from submin.models import user

READ_CMDS = [
		"upload-pack",
		"upload-archive",
]

WRITE_CMDS = [
		"receive-pack",
]

def run(username):
	if "SSH_ORIGINAL_COMMAND" not in os.environ:
		print ("No command provided. " \
				+ "Expected something like git-receive-pack", file=sys.stderr)
		sys.exit(1)

	orig_cmd = os.environ["SSH_ORIGINAL_COMMAND"]
	if not orig_cmd.startswith("git") or orig_cmd[3] not in (' ', '-'):
		print ("Not a git-command. Expected something like " \
				+ "git-receive-pack",file=sys.stderr)
		sys.exit(1)

	# command is something like `git-receive-pack repo.git'
	# or `git receive-pack repo.git'
	cmd, repo = orig_cmd.split(" ", 1)
	if repo[0] == repo[-1] == "'":
		repo = repo[1:-1]
	# git 1.5 adds a slash?
	if repo[0] == '/':
		repo = repo[1:]
	repo = repo[:-4] # remove '.git'
	sub_cmd = cmd[4:]

	u = user.User(username)

	readable_paths = permissions.list_readable_user_paths(repo, "git", u)
	if not readable_paths:
		print ("Permission denied for %s to user %s" % (repo, u),file=sys.stderr)
		sys.exit(1)

	if sub_cmd not in WRITE_CMDS + READ_CMDS:
		print ("Unrecognized command:", cmd, file=sys.stderr)
		sys.exit(1)
	elif sub_cmd in WRITE_CMDS:
		# check if we have write access
		writeable_paths = permissions.list_writeable_user_paths(repo, "git", u)
		if not writeable_paths:
			print ("Permission denied for writing, for %s to user %s" % \
					(repo, u),file=sys.stderr)
			sys.exit(1)

	# To pass on to the git-hook
	os.environ["SUBMIN_USERNAME"] = username
	os.environ["SUBMIN_REPO"] = repo

	repo_path = repository.directory('git', repo)
	print ("Original command: %s" % orig_cmd,file=sys.stderr)
	print ("executing git-%s '%s'" % (sub_cmd, repo_path),file=sys.stderr) 
	# XXX: retreive git-path from options.
	os.execvp('git',
			['git', 'shell', '-c', "git-%s '%s'" % (sub_cmd, repo_path)])
