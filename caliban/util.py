"""
Utilities for our job runner.
"""
import io
import itertools as it
import os
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
from typing import Dict, List

from absl import flags


def expand_args(items: Dict[str, str]) -> List[str]:
  """Converts the input map into a """
  pairs = [[k, v] if v is not None else [k] for k, v in items.items()]
  return list(it.chain.from_iterable(pairs))


def parse_flags_with_usage(args, known_only=False):
  """Tries to parse the flags, print usage, and exit if unparseable.
  Args:
    args: [str], a non-empty list of the command line arguments including
        program name.
  Returns:
    [str], a non-empty list of remaining command line arguments after parsing
    flags, including program name.
  """
  try:
    return flags.FLAGS(args, known_only=known_only)
  except flags.Error as error:
    sys.stderr.write('FATAL Flags parsing error: %s\n' % error)
    sys.stderr.write('Pass --helpshort or --helpfull to see help on flags.\n')
    sys.exit(1)


class TempCopy(object):

  def __init__(self, original_path):
    self.original_path = original_path
    self.path = None

  def __enter__(self):
    if self.original_path is None:
      return None

    temp_dir = os.getcwd()
    base_path = os.path.basename(self.original_path)
    self.path = os.path.join(temp_dir, base_path)

    # TODO - if that path already exists in this folder, do NOT delete it! Throw
    # an error here. This should really nest under a temp dir.
    shutil.copy2(self.original_path, self.path)
    return base_path

  def __exit__(self, exc_type, exc_val, exc_tb):
    if self.path is not None:
      os.remove(self.path)


def capture_stdout(cmd: List[str], input_str: str) -> str:
  """Executes the supplied command with the supplied string of std input, then
  streams the output to stdout, and returns it as a string.
  """
  buf = io.StringIO()
  with subprocess.Popen(cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        bufsize=1,
                        encoding="utf-8") as p:
    p.stdin.write(input_str)
    p.stdin.close()
    for line in p.stdout:
      print(line, end='')
      buf.write(line)

  return buf.getvalue()