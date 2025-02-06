with import <nixpkgs> {};

# nix-shell -K
# cd result
# source env-vars

(let

foo= "bar";

in


stdenv.mkDerivation {

  name = "impurePythonEnv";
  buildInputs = [
    #gcc

    (python311.buildEnv.override {
      extraLibs = [
	pkgs.python311Packages.gnureadline
        pkgs.python311Packages.bottle
        pkgs.python311Packages.reportlab
	pkgs.python311Packages.pillow        
        
        #pkgs.python37Packages.websockets
        #pkgs.python37Packages.watchdog
	#pkgs.python37Packages.matplotlib
	#pkgs.python37Packages.numpy
	#pkgs.python37Packages.scipy
        #pkgs.python37Packages.cython
	#pkgs.python37Packages.numpy-stl
        #pkgs.python37Packages.scikitimage
      ];
      ignoreCollisions = true;
    })
  ];
  shellHook = ''
	
  '';
})













