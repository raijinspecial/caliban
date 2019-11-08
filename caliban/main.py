"""Docker and AI Platform model training and development script.

Run like this:

# Run the job locally
caliban local -m trainer.train

# Start a shell:
caliban docker shell

# Watch a local job fail, since it no longer has local access.
caliban docker run -m trainer.train -p trainer

# Run a local job via Docker successfully:
caliban docker run -m trainer.train -p trainer --epochs 2 --data_path gs://$BUCKET_NAME/data/mnist.npz

# Submit a remote job
caliban docker cloud -m trainer.train -p trainer --epochs 2 --data_path gs://$BUCKET_NAME/data/mnist.npz
"""

from __future__ import absolute_import, division, print_function

import logging as ll
import os
import subprocess
import sys

import caliban.cli as cli
import caliban.cloud as cloud
import caliban.config as c
import caliban.docker as docker
from absl import app, logging

ll.getLogger('caliban.main').setLevel(logging.ERROR)


def run_app(arg_input):
  """Any argument not absorbed by Abseil's flags gets passed along to here.
  """
  args = vars(arg_input)
  script_args = c.extract_script_args(args)

  command = args["command"]
  use_gpu = args["GPU"]

  creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

  # TODO These have defaults... the project default is probably not good. We
  # should error if this doesn't exist.
  project_id = os.environ.get("PROJECT_ID", "research-3141")
  region = os.environ.get("REGION", "us-central1")

  if command == "shell":
    docker.start_shell(use_gpu, creds_path=creds_path)

  elif command == "run":
    package = docker.Package(args["package_path"], args["module"])
    docker.submit_local(use_gpu, package, script_args, creds_path=creds_path)

  elif command == "cloud":
    package = docker.Package(args["package_path"], args["module"])
    cloud.submit_package(use_gpu,
                         package,
                         region,
                         project_id,
                         script_args=script_args,
                         creds_path=creds_path)
  else:
    logging.info(f"Unknown command: {command}")
    sys.exit(1)


def main():
  app.run(run_app, flags_parser=cli.parse_flags)


if __name__ == '__main__':
  main()