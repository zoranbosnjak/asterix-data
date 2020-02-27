{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  name = "asterix-data";
  src = ./.;
  buildInputs = with pkgs; [
    scons
    jing
    python36
  ];
  doCheck = true;
  checkPhase = ''
    scons validate
  '';
  installPhase = ''
    scons install --prefix=$out
  '';
}
