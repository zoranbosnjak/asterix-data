{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  name = "asterix-data";
  src = ./.;
  buildInputs = with pkgs; [
    scons
    jing
  ];
  doCheck = true;
  checkPhase = ''
    scons validate
  '';
  installPhase = ''
    scons install --prefix=$out
  '';
}
