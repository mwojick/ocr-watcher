{
  description = "A Nix-flake-based Python development environment";

  inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";

  outputs = { self, nixpkgs }:
    let
      supportedSystems =
        [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f:
        nixpkgs.lib.genAttrs supportedSystems
        (system: f { pkgs = import nixpkgs { inherit system; }; });
    in {
      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
          venvDir = ".venv";
          packages = with pkgs;
            [ python312 stdenv.cc.cc.lib makeWrapper tesseract ]
            ++ (with pkgs.python312Packages; [ uv ruff ]);

          shellHook = ''
            if [ ! -d "$venvDir" ]; then
              echo "Creating new venv using uv..."
              uv venv "$venvDir"
            fi

            if [ -d "$venvDir" ] && [ ! -f "$venvDir/bin/.python-wrapped" ]; then
              echo "Wrapping Python with required libraries..."
              wrapProgram "$PWD/$venvDir/bin/python" \
                --prefix LD_LIBRARY_PATH : "${pkgs.stdenv.cc.cc.lib}/lib"
            fi

            echo "Activating venv..."
            source "$venvDir/bin/activate"
          '';
        };
      });
    };
}
