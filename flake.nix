{
    description = "A python development environment.";

    inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    inputs.flake-utils.url = "github:numtide/flake-utils";

    outputs = { self, nixpkgs, flake-utils }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                # Defino "python-with-pkgs"
                pkgs = import nixpkgs { inherit system; };
                python-with-pkgs = pkgs.python3.withPackages (ps: with ps; [
                    # Python packages here
                    pandas
                    transformers
                ]);
            in 
            {
                devShells.default = pkgs.mkShell {
                    buildInputs = [
                        python-with-packages
                    ];
                };
            }
        );
}
