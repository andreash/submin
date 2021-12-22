from submin.models import options
from submin.models.exceptions import UnknownKeyError

from .common import apache_modules, ApacheCtlError
from .common import add_labels

import logging

fails = ['svn_dir_set', 'svn_apache_modules_ok', 'svn_apache_modules_exec_ok']
warnings = ['enabled_svn']

def diagnostics():
	results = {}
	results['enabled_svn'] = 'svn' in options.value('vcs_plugins', '')

	if not results['enabled_svn']:
		results['enabled_svn_label'] = 'disabled'
		results['svn_all_label'] = 'disabled'
		return results

	try:
		svn_dir = options.env_path('svn_dir')
	except UnknownKeyError:
		results['svn_dir_set'] = False
	else:
		results['svn_dir_set'] = True

	found_mods = {}
	amods = []
	try:
		amods = apache_modules()
	except ApacheCtlError as e:
		results['svn_apache_modules_ok'] = False
		results['svn_apache_modules_exec_ok'] = False
		results['svn_apache_modules_errmsg'] = str(e)
	else:
		results['svn_apache_modules_exec_ok'] = True

	required_mods = ['dav', 'dav_svn', 'authz_svn', 'authn_dbd', 'dbd']
	for mod in required_mods:
		found_mods.update({mod: mod in amods})

	if False in found_mods.values():
		required_mods = ['dav', 'dav_svn', 'authz_svn', 'authn_any']
		found_mods = {}
		for mod in required_mods:
			found_mods.update({mod: mod in amods})
		
	results['svn_apache_modules'] = found_mods
	results['svn_apache_modules_ok'] = False not in found_mods.values()

	return add_labels(results, 'svn_all', warnings, fails)
