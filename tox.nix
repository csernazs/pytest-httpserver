{ pkgs ? import <nixpkgs> {} }:

let
  unstable = import <nixos-unstable> { config = { allowUnfree = true; }; };
  toxPython = p: p.withPackages ( p: [ p.pip ] );
  basePython = p: (p.withPackages ( p: [ p.virtualenv p.pip p.tox ] ));

in pkgs.mkShell {
  buildInputs = with pkgs; [
    (basePython python311)
    (toxPython python310)
    (toxPython python39)
    (toxPython python38)

    bashInteractive
  ];
}
