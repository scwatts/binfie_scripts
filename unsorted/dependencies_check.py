'''Code from hicap show examples of:
    * logging
    * dependency checking
'''
from distutils.version import LooseVersion
import logging
import re
import shutil
import subprocess
import sys


def initialise_logging(log_level, log_file):
    log_handles = list()
    log_handles.append(logging.StreamHandler())
    # Ensure that parent dir of log file exists, otherwise raise error during check_arguments
    if log_file and log_file.parent.exists():
        log_handles.append(logging.FileHandler(log_file, mode='w'))

    log_message_format = '%(asctime)s %(levelname)s: %(message)s'
    log_formatter = logging.Formatter(fmt=log_message_format, datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger()
    for log_handle in log_handles:
        log_handle.setFormatter(log_formatter)
        logger.addHandler(log_handle)

    logger.setLevel(log_level)


def check_dependencies():
    logging.info('Checking dependencies')
    dependencies = {
            'blastn': {
                'vcommand': 'blastn -version',
                'vregex': re.compile(r'^blastn: (.+)\n'),
                'vrequired': '2.2.28'},
            'makeblastdb': {
                'vcommand': 'makeblastdb -version',
                'vregex': re.compile(r'^makeblastdb: (.+)\n'),
                'vrequired': '2.2.28'},
            'prodigal': {
                'vcommand': 'prodigal -v 2>&1',
                'vregex': re.compile(r'.*Prodigal V(.+?):'),
                'vrequired': '2.6.1'}
            }
    for dependency, version_data in dependencies.items():
        if not shutil.which(dependency):
            logging.critical('Could not find dependency %s' % dependency)
            sys.exit(1)
        result = execute_command(version_data['vcommand'], check=False)
        try:
            version = version_data['vregex'].search(result.stdout).group(1)
        except AttributeError:
            # TODO: should we have an option to skip dependency check?
            logging.critical('Unable to determine version for %s' % dependency)
            sys.exit(1)
        if LooseVersion(version) < LooseVersion(version_data['vrequired']):
            msg = '%s version %s or high is required'
            logging.critical(msg % (dependency, version_data['vrequired']))
            sys.exit(1)
        else:
            logging.debug('Found %s version %s' % (dependency, version))
