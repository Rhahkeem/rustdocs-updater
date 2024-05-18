#!/usr/bin/python3
import os
from git import Repo, Remote
import shutil
import subprocess
import glob
import toml


RUST_DOCS_DIR = os.path.realpath("~/Code/rust-docs/")
IS_TEST = False


def do_git_pull(directory_path):
    print(f"Doing a git pull in {directory_path}")
    remote = Remote(Repo(directory_path), "origin")
    remote.pull()


def run_cargo_doc(directory_path):
    execute_cmd = f"cargo-docset docset --manifest-path {directory_path}/Cargo.toml"
    print(f"Running {execute_cmd}")

    subprocess.run(
        execute_cmd.split(), encoding="utf-8", check=True, capture_output=True
    )


def move_necessary_files(docset_root_dir):
    print("Moving files to zeal directory")
    docset_name = os.path.basename(docset_root_dir)
    cargo_toml = toml.load(f"{docset_root_dir}/Cargo.toml")
    try:
        docset_name = cargo_toml["package"]["name"]
    except KeyError:
        print(
            f"Package {docset_name} doesn't have a package Key in its Cargo.toml.\
                Falling back to dirname"
        )

    docset_dir_name = f"{docset_name}.docset"
    destination_dir = (
        "~/playground/docset" if IS_TEST else "~/.local/share/Zeal/Zeal/docsets"
    )

    destination_dir = os.path.realpath(destination_dir)

    shutil.copytree(
        f"{docset_root_dir}/target/docset/{docset_dir_name}",
        f"{destination_dir}/{docset_dir_name}",
        dirs_exist_ok=True,
    )

    for file in glob.glob(f"{RUST_DOCS_DIR}/*.png"):
        shutil.copy(file, f"{destination_dir}/{docset_dir_name}")


directories = [dir for dir in os.scandir(RUST_DOCS_DIR) if dir.is_dir()]
# if IS_TEST:
#     directories = directories[0:1]
for directory in directories:
    full_path = os.path.realpath(directory.path)
    current_dir = os.path.basename(full_path)
    print(f"Beginning with {current_dir}")
    do_git_pull(full_path)
    run_cargo_doc(full_path)
    move_necessary_files(full_path)
    print(f"Finishing with {current_dir}", end="\n\n")
