
#include <iostream>
using namespace std;

#include "G4RunManager.hh"
#include "G4UImanager.hh"
#include "FTFP_BERT.hh"
#include "QGSP_BERT_HP.hh"
#include "G4VisExecutive.hh"
#include "G4UIExecutive.hh"
#include "Randomize.hh"

#include "PDDetectorConstruction.hh"
#include "Analysis.hh"

int main(int argc,char** argv)
{
  // Detect interactive mode (if no arguments) and define UI session
  //
  G4UIExecutive* ui = 0;
  if ( argc == 1 ) {
    ui = new G4UIExecutive(argc, argv);
  }

  Analysis a;

  // Choose the Random engine
  G4Random::setTheEngine(new CLHEP::RanecuEngine);

  // Construct the default run manager
  G4RunManager* runManager = new G4RunManager;

  // Physics list
  G4VModularPhysicsList* physicsList = new FTFP_BERT; // HEP
  //G4VModularPhysicsList* physicsList = new QGSP_BERT_HP; // Low-Energy Dosemetric

  // Set mandatory initialization classes
  //
  // Detector construction
  runManager->SetUserInitialization(new PDDetectorConstruction());

  physicsList->SetVerboseLevel(1);
  runManager->SetUserInitialization(physicsList);


      
  // User action initialization
  runManager->SetUserInitialization(new AnalysisActionInit);
  
  // Initialize visualization
  //
  //G4VisManager* visManager = new G4VisExecutive;
  // G4VisExecutive can take a verbosity argument - see /vis/verbose guidance.
  G4VisManager* visManager = new G4VisExecutive("Quiet");
  visManager->Initialize();

  // Get the pointer to the User Interface manager
  G4UImanager* UImanager = G4UImanager::GetUIpointer();

  // Process macro or start UI session
  if ( ! ui ) { 
    // batch mode
    G4String command = "/control/execute ";
    G4String fileName = argv[1];
    UImanager->ApplyCommand(command+fileName);
  }
  else { 
    ui->SessionStart();
    delete ui;
  }
  cout << "pixel depth:  " << Analysis::instance()->pixel_depth << "\n";
  cout << "pixel depletion:  " << Analysis::instance()->pixel_depletion << "\n";
  cout << "pixel width:  " << Analysis::instance()->pixel_width << "\n";
  cout << "pixel max x:  " << Analysis::instance()->pixel_max_x << "\n";
  cout << "pixel max y:  " << Analysis::instance()->pixel_max_y << "\n";
  cout << "gen theta:    " << Analysis::instance()->gen_theta << "\n";
  cout << "gen theta max:    " << Analysis::instance()->gen_theta_max << "\n";
  cout << "gen phi max:    " << Analysis::instance()->gen_phi_max << "\n";
  
  delete runManager;
  //delete a;
  delete visManager;
}


