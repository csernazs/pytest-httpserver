{
  description = "Application packaged using poetry2nix";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication mkPoetryEnv;
      in
      {
        packages = {
          pytest-httpserver = mkPoetryApplication { projectDir = self; };
          default = self.packages.${system}.pytest-httpserver;
        };

        devShells.default = mkPoetryEnv {
          projectDir = ./.;
          groups = [ "develop" ];
          checkGroups = [ "test" ];
          editablePackageSources = {
            pytest-httpserver = ./.;
          };
        };
      });
}
