{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  name = "asterix-data";
  src = builtins.filterSource
    (path: type:
      (type != "directory" || baseNameOf path != ".git")
      && (type != "symlink" || baseNameOf path != "result"))
      ./.;

  buildInputs = with pkgs; [
    scons
    jing
    python3
  ];
  doCheck = true;
  checkPhase = ''
    scons validate
  '';
  installPhase = ''
    scons install --prefix=$out
  '';
}
