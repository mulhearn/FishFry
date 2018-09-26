# $Id: GNUmakefile 68058 2013-03-13 14:47:43Z gcosmo $
# --------------------------------------------------------------
# GNUmakefile for examples module.  Gabriele Cosmo, 06/04/98.
# --------------------------------------------------------------

name := photodiode
G4TARGET := $(name)
G4EXLIB := true

ifndef G4INSTALL
  G4INSTALL = ../../..
endif


# ROOT support
CPPFLAGS += -I$(shell root-config --incdir) -g
EXTRALIBS = $(shell root-config --glibs)


.PHONY: all
all: lib bin

include $(G4INSTALL)/config/binmake.gmk

visclean:
	rm -f g4*.prim g4*.eps g4*.wrl
	rm -f .DAWN_*

