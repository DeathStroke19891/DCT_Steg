{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell
{
  nativeBuildInputs = [
    pkgs.trashy
    pkgs.python312
    pkgs.python312Packages.opencv4
    pkgs.python312Packages.bitstring
    pkgs.python312Packages.numpy
  ];
  
  shellHook = ''
    alias rm="trash -c always put"
  '';
}
