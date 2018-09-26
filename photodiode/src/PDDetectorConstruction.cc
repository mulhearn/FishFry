#include <iostream>
#include <stdlib.h>

#include "G4RunManager.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4Cons.hh"
#include "G4Orb.hh"
#include "G4Sphere.hh"
#include "G4Trd.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"

#include "PDDetectorConstruction.hh"
#include "Analysis.hh"

using namespace std;


PDDetectorConstruction::PDDetectorConstruction()
: G4VUserDetectorConstruction(),
  fScoringVolume(0)
{ }

PDDetectorConstruction::~PDDetectorConstruction()
{ }

G4VPhysicalVolume* PDDetectorConstruction::Construct()
{  
  // Obtain the analysis parameters which effect geometry:
  G4double  pix_d  = Analysis::instance()->pixel_depth * micrometer;
  G4double  pix_w  = Analysis::instance()->pixel_width * micrometer;
  G4int max_x  = Analysis::instance()->pixel_max_x;
  G4int max_y  = Analysis::instance()->pixel_max_y;
  G4double slab_depth  = Analysis::instance()->slab_depth * micrometer;  // set in config...
  G4double slab_gap = Analysis::instance()->slab_gap * micrometer;  // set in config...

  G4int num_x  = 2 * max_x + 1;
  G4int num_y  = 2 * max_y + 1;


  // Calculate derived quantities:

  // pixel grid
  double grid_size_x = num_x * pix_w;
  double grid_size_y = num_y * pix_w;
  double grid_size_z = pix_d;

  double slab_size_z   = slab_depth;
  double slab_offset_z = grid_size_z * 0.5 + slab_size_z * 0.5 + slab_gap;

  double slab_size_x   = slab_size_z + slab_offset_z;
  double slab_size_y   = slab_size_z + slab_offset_z;
  if (slab_size_x < grid_size_x) slab_size_x = grid_size_x;
  if (slab_size_y < grid_size_y) slab_size_y = grid_size_y;

  // the envelope
  double env_size_x = 1.2 * slab_size_x;
  double env_size_y = 1.2 * slab_size_y;
  double env_size_z = 1.2 * (grid_size_z + 2*(slab_gap + slab_size_z));

  // make envelope cubic, for better visualization
  double env_max = env_size_z;
  if (env_size_x > env_max) env_max = env_size_x;
  if (env_size_y > env_max) env_max = env_size_y;
  env_size_x = env_max;
  env_size_y = env_max;
  env_size_z = env_max;


  // the world
  double world_size_x = 1.2 * env_size_x;
  double world_size_y = 1.2 * env_size_y;
  double world_size_z = 1.2 * env_size_z;


 
  // Get nist material manager
  G4NistManager* nist = G4NistManager::Instance();
  
  // Envelope parameters
  //
   G4Material* env_mat = nist->FindOrBuildMaterial("G4_AIR");
   
  // Option to switch on/off checking of volumes overlaps
  //
  G4bool checkOverlaps = false;

  //     
  // World parameters
  //
  G4Material* world_mat = nist->FindOrBuildMaterial("G4_AIR");
  
  G4Box* solidWorld =    
    new G4Box("World",                       //its name
       0.5*world_size_x, 0.5*world_size_y, 0.5*world_size_z);     //its size
      
  G4LogicalVolume* logicWorld =                         
    new G4LogicalVolume(solidWorld,          //its solid
                        world_mat,           //its material
                        "World");            //its name
                                   
  G4VPhysicalVolume* physWorld = 
    new G4PVPlacement(0,                     //no rotation
                      G4ThreeVector(),       //at (0,0,0)
                      logicWorld,            //its logical volume
                      "World",               //its name
                      0,                     //its mother  volume
                      false,                 //no boolean operation
                      0,                     //copy number
                      checkOverlaps);        //overlaps checking

  //     
  // Envelope
  //  
  G4Box* solidEnv =    
    new G4Box("Envelope",                    //its name
        0.5*env_size_x, 0.5*env_size_y, 0.5*env_size_z); //its size
      
  G4LogicalVolume* logicEnv =                         
    new G4LogicalVolume(solidEnv,            //its solid
                        env_mat,             //its material
                        "Envelope");         //its name
               
  new G4PVPlacement(0,                       //no rotation
                    G4ThreeVector(),         //at (0,0,0)
                    logicEnv,                //its logical volume
                    "Envelope",              //its name
                    logicWorld,              //its mother  volume
                    false,                   //no boolean operation
                    0,                       //copy number
                    checkOverlaps);          //overlaps checking
 
  //     
  // Photodiode
  //  
  //G4Material* pd_mat = new G4Material("Silicon", 14., 28.090*g/mole, 2.33*g/cm3);
  G4Material* pd_mat = nist->FindOrBuildMaterial("G4_Si");

  G4Box* solidPD =    
    new G4Box("Photodiode", 0.5*pix_w, 0.5*pix_w, 0.5*pix_d); 
                      
  G4LogicalVolume* logicPD =                         
    new G4LogicalVolume(solidPD,         //its solid
                        pd_mat,          //its material
                        "Photodiode");           //its name               

  int count = 0;
  for (int ix = -max_x; ix <= max_x; ix++){
    for (int iy = -max_y; iy <= max_y; iy++){
      double x = ix*pix_w;
      double y = iy*pix_w;
      //cout << "INFO: building pixel number " << count << " at x=" << x << " y=" << y << "\n";

      G4ThreeVector pos = G4ThreeVector(x, y, 0);
      char name[200];
      sprintf(name,"Photodiode_%d", count);

      new G4PVPlacement(0,                       //no rotation
			pos,                    //at position
			logicPD,             //its logical volume
			name,                //its name
			logicEnv,                //its mother  volume
			false,                   //no boolean operation
			0,                       //copy number
			checkOverlaps);          //overlaps checking
      count++;
    }
  }


  // Set PD as scoring volume
  //
  fScoringVolume = logicPD;

  if (slab_depth > 0.0){

    //G4Material* slab_mat = nist->FindOrBuildMaterial("G4_POLYVINYL_CHLORIDE");
    G4Material* slab_mat = nist->FindOrBuildMaterial("G4_GLASS_PLATE");
    G4Box* solidSlab =    
      new G4Box("Slab", 0.5*slab_size_x, 0.5*slab_size_y, 0.5*slab_size_z);                       
    G4LogicalVolume* logicSlab =                         
      new G4LogicalVolume(solidSlab,         //its solid
			  slab_mat,          //its material
			  "Slab");           //its name               
    G4ThreeVector pos = G4ThreeVector(0, 0, slab_offset_z);
    new G4PVPlacement(0,                     //no rotation
		      pos,                   //at position
		      logicSlab,             //its logical volume
		      "Slab",                //its name
		      logicEnv,              //its mother  volume
		      false,                 
		      0,                     //copy number
		      checkOverlaps);        //overlaps checking
  }

  //
  //always return the physical World
  //
  return physWorld;
}


