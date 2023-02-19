{ pkgs ? import <nixpkgs> {} }:

let
  unstable = import <nixos-unstable> { config = { allowUnfree = true; }; };
in pkgs.mkShell {
  buildInputs = with pkgs; [
    virtualenv

    python3Packages.tox
    python3Packages.poetry

    pre-commit
    python3Packages.requests
    python3Packages.sphinx
    python3Packages.sphinx-rtd-theme
    reno
    python3Packages.mypy
    python3Packages.types-requests
    python3Packages.pytest
    python3Packages.pytest-cov
    python3Packages.coverage
    python3Packages.ipdb
    python3Packages.types-toml
    python3Packages.toml
    python3Packages.black


    bashInteractive
  ];
}
