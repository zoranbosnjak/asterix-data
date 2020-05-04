{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  name = "asterix-data";
  src = ./.;
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
