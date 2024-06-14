{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python311.withPackages (ps: [
    ps.pip
    ps.debugpy
    ps.ipython
    ps.numpy
    ps.setuptools
  ]);
in

pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
    cmake
    poetry
    jq
    nodejs_20
    ollama
    gcc
    stdenv.cc.cc.lib
  ];

  buildInputs = [
    pythonEnv
  ];

  packages = with pkgs; [
    git
    neovim
    python311
    httpie
    ruff
    pre-commit
  ];

  GIT_EDITOR = "${pkgs.neovim}/bin/nvim";

  shellHook = ''
    pyenv global system
    export PATH=$PATH:${pythonEnv}/bin
    poetry env use ${pythonEnv}/bin/python

    ollama pull mistral
    ollama pull nomic-embed-text
  '';

  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
}