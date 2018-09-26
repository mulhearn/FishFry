#include <iostream>
#include <algorithm>

#include <TH1D.h>
#include <TFile.h>
#include <TTree.h>

#include "G4UIdirectory.hh"
#include "G4Step.hh"
#include "G4Event.hh"
#include "G4Run.hh"
#include "G4UIdirectory.hh"
#include "G4RunManager.hh"
#include "G4LogicalVolumeStore.hh"
#include "G4LogicalVolume.hh"
#include "G4UnitsTable.hh"
#include "G4SystemOfUnits.hh"
#include "G4UIcmdWithADouble.hh"
#include "G4UIcmdWithAnInteger.hh"

#include "PDDetectorConstruction.hh"
#include "PDPrimaryGeneratorAction.hh"
#include "Analysis.hh"

using namespace std;


Analysis * Analysis::instance_ = NULL;

void Analysis::stats::reset(){
  g_hit  = e_hit  = m_hit = 0;
  g_edep = e_edep = m_edep = edep = nonion = adep = cmax = 0;
}

Analysis::Analysis()
: 
  G4UImessenger(),
  analysisDir_(0),
  cosmicModeCmd_(0),
  pixelDepletionCmd_(0),
  pixelWidthCmd_(0),
  pixelMaxXCmd_(0),
  pixelMaxYCmd_(0),
  genThetaCmd_(0),
  genThetaMaxCmd_(0),
  genPhiMaxCmd_(0),
  file_(0),
  ntuple_(0),
  scoringVolume_(0)
{ 
  // set default values:
  cosmic_mode     = 0;
  slab_depth      = 0.0;
  slab_gap        = 0.0;
  pixel_depletion = 30.0;
  pixel_depth     = 30.0;
  pixel_width     = 1.0;
  pixel_max_x     = 2;
  pixel_max_y     = 2;
  gen_theta       = 0.5;
  gen_theta_max   = 0.0;
  gen_phi_max     = 0.0;

  grid_edep = NULL;
  grid_max = 0;
  cell_edep = NULL;
  cell_max = 0;

  analysisDir_ = new G4UIdirectory("/analysis/");
  analysisDir_->SetGuidance("Analysis commands");

  cosmicModeCmd_ = new G4UIcmdWithAnInteger("/analysis/cosmic_mode", this);
  cosmicModeCmd_->SetParameterName ("cosmic_mode", true);
  cosmicModeCmd_->SetDefaultValue (cosmic_mode);  

  slabDepthCmd_ = new G4UIcmdWithADouble("/analysis/slab_depth", this);
  slabDepthCmd_->SetParameterName ("slab_depth", true);
  slabDepthCmd_->SetDefaultValue (slab_depth);  

  slabGapCmd_ = new G4UIcmdWithADouble("/analysis/slab_gap", this);
  slabGapCmd_->SetParameterName ("slab_gap", true);
  slabGapCmd_->SetDefaultValue (slab_gap);  
  
  pixelDepletionCmd_ = new G4UIcmdWithADouble("/analysis/pixel_depletion", this);
  pixelDepletionCmd_->SetParameterName ("pixel_depletion", true);
  pixelDepletionCmd_->SetDefaultValue (pixel_depletion);  

  pixelDepthCmd_ = new G4UIcmdWithADouble("/analysis/pixel_depth", this);
  pixelDepthCmd_->SetParameterName ("pixel_depth", true);
  pixelDepthCmd_->SetDefaultValue (pixel_depth);  

  pixelWidthCmd_ = new G4UIcmdWithADouble("/analysis/pixel_width", this);
  pixelWidthCmd_->SetParameterName ("pixel_width", true);
  pixelWidthCmd_->SetDefaultValue (pixel_width);  

  pixelMaxXCmd_ = new G4UIcmdWithAnInteger("/analysis/pixel_max_x", this);
  pixelMaxXCmd_->SetParameterName ("pixel_max_x", true);
  pixelMaxXCmd_->SetDefaultValue (pixel_max_x);  

  pixelMaxYCmd_ = new G4UIcmdWithAnInteger("/analysis/pixel_max_y", this);
  pixelMaxYCmd_->SetParameterName ("depletion", true);
  pixelMaxYCmd_->SetDefaultValue (pixel_max_y);  

  genThetaCmd_ = new G4UIcmdWithADouble("/analysis/gen_theta", this);
  genThetaCmd_->SetParameterName ("gen_theta", true);
  genThetaCmd_->SetDefaultValue (gen_theta);  

  genThetaMaxCmd_ = new G4UIcmdWithADouble("/analysis/gen_theta_max", this);
  genThetaMaxCmd_->SetParameterName ("gen_theta_max", true);
  genThetaMaxCmd_->SetDefaultValue (gen_theta_max);  

  genPhiMaxCmd_ = new G4UIcmdWithADouble("/analysis/gen_phi_max", this);
  genPhiMaxCmd_->SetParameterName ("gen_phi_max", true);
  genPhiMaxCmd_->SetDefaultValue (gen_phi_max);  

  instance_ = this;
}

Analysis::~Analysis()
{
  instance_ = NULL;
  delete pixelDepletionCmd_;
  delete pixelWidthCmd_;
  delete pixelMaxXCmd_;
  delete pixelMaxYCmd_;
  delete genThetaCmd_;
  delete genThetaMaxCmd_;
  delete genPhiMaxCmd_;
  delete analysisDir_;
  if (file_) delete file_;
}


void Analysis::SetNewValue(G4UIcommand * command,G4String arg){
  std::istringstream is((const char *) arg);

  if (command == cosmicModeCmd_){
    is >> cosmic_mode;
    cout << "INFO:  Set cosmic mode argument " << arg << " parsed as " << cosmic_mode << "\n";
  }

  if (command == slabDepthCmd_){
    is >> slab_depth;
    cout << "INFO:  Set slab depth argument " << arg << " parsed as " << slab_depth << "\n";
  }

  if (command == slabGapCmd_){
    is >> slab_gap;
    cout << "INFO:  Set slab depth argument " << arg << " parsed as " << slab_gap << "\n";
  }

  if (command == pixelDepletionCmd_){
    is >> pixel_depletion;
    cout << "INFO:  Set pixel depletion argument " << arg << " parsed as " << pixel_depletion << "\n";
  }

  if (command == pixelDepthCmd_){
    is >> pixel_depth;
    cout << "INFO:  Set pixel depth argument " << arg << " parsed as " << pixel_depth << "\n";
  }

  if (command == pixelWidthCmd_){
    is >> pixel_width;
    cout << "INFO:  Set pixel width argument " << arg << " parsed as " << pixel_width << "\n";
  }

  if (command == pixelMaxXCmd_){
    is >> pixel_max_x;
    cout << "INFO:  Set pixel max x argument " << arg << " parsed as " << pixel_max_x << "\n";
  }

  if (command == pixelMaxYCmd_){
    is >> pixel_max_y;
    cout << "INFO:  Set pixel max y argument " << arg << " parsed as " << pixel_max_y << "\n";
  }

  if (command == genThetaCmd_){
    is >> gen_theta;
    cout << "INFO:  Set gen theta argument " << arg << " parsed as " << gen_theta << "\n";
  }

  if (command == genThetaMaxCmd_){
    is >> gen_theta_max;
    cout << "INFO:  Set gen theta max argument " << arg << " parsed as " << gen_theta_max << "\n";
  }

  if (command == genPhiMaxCmd_){
    is >> gen_phi_max;
    cout << "INFO:  Set gen phi max argument " << arg << " parsed as " << gen_phi_max << "\n";
  }

}

void Analysis::Book()
{ 
  // Creating a tree container to handle histograms and ntuples.
  // This tree is associated to an output file.
  //
  G4String fileName = "pdout.root";
  file_ = new TFile(fileName,"RECREATE");
  if (! file_) {
    G4cout << " Analysis::Book :" 
           << " problem creating the ROOT TFile "
           << G4endl;
    return;
  }
  
  // create ntuple
  ntuple_ = new TTree("edep", "");
  ntuple_->Branch("edep",     &evt_.edep, "edep/F");
  ntuple_->Branch("adep",     &evt_.adep, "adep/F");
  ntuple_->Branch("cmax",     &evt_.cmax, "cmax/F");
  ntuple_->Branch("evt_theta", &evt_theta, "evt_theta/F");
  ntuple_->Branch("evt_phi", &evt_phi, "evt_phi/F");
  ntuple_->Branch("edep1",     &edep1, "edep/F");
  ntuple_->Branch("index1",     &index1, "edep/I");

  grid_max = (2 * pixel_max_x + 1) * (2 * pixel_max_y + 1);
  grid_edep = new float[grid_max];

  cell_max = CELL_GRID_SIZE * CELL_GRID_SIZE;
  cell_edep = new float[cell_max];

  // save full grid:
  //ntuple_->Branch("grid_max", &grid_max, "grid_max/I");
  //ntuple_->Branch("grid_edep",grid_edep,"grid_edep[grid_max]/F");

  // save reduced grid:
  ntuple_->Branch("cell_max", &cell_max, "cell_max/I");
  ntuple_->Branch("cell_edep",cell_edep,"cell_edep[cell_max]/F");

  G4cout << "\n----> Output file is open in " << fileName << G4endl;
}


void Analysis::Save()
{ 
  if (! file_) return;
  
  file_->Write();       // Writing the histograms to the file
  file_->Close();       // and closing the tree (and the file)
  
  G4cout << "\n----> Histograms and ntuples are saved\n" << G4endl;
}

void Analysis::FillNtuple(){
  if (!ntuple_) return;
  

  //int nx = 2*pixel_max_x+1;
  int ny = 2*pixel_max_y+1;
  
  index1=0;
  for (int i=0; i<grid_max; i++){
    if (grid_edep[i] > grid_edep[index1]){
      index1 = i;
    }
  }
  edep1 = grid_edep[index1];
  
  int offset = CELL_GRID_SIZE / 2;
  int ix = (index1 / ny); 
  int iy = (index1 % ny);   
  ix -= offset;
  iy -= offset;

  if (ix < 0) ix = 0;
  if (iy < 0) iy = 0;
  for (int dx = 0; dx<CELL_GRID_SIZE; dx++){
    for (int dy = 0; dy<CELL_GRID_SIZE; dy++){
      int index = (ix+dx)*ny+iy+dy;
      int itupe = dx*CELL_GRID_SIZE + dy;
      cell_edep[itupe]=grid_edep[index];
    }
  }

  
  
  ntuple_->Fill();
}

void Analysis::Step(const G4Step* step)
{
  if (!scoringVolume_) { 
    const PDDetectorConstruction* detectorConstruction
      = static_cast<const PDDetectorConstruction*>
        (G4RunManager::GetRunManager()->GetUserDetectorConstruction());
    scoringVolume_ = detectorConstruction->GetScoringVolume();   
  }

  // get volume of the current step
  G4LogicalVolume* volume 
    = step->GetPreStepPoint()->GetTouchableHandle()
      ->GetVolume()->GetLogicalVolume();

  G4VPhysicalVolume* pv 
    = step->GetPreStepPoint()->GetTouchableHandle()
    ->GetVolume();

        
  // check if we are in scoring volume
  if (volume != scoringVolume_) return;

  double z1 = step->GetPreStepPoint()->GetPosition().z() / micrometer;
  double z2 = step->GetPostStepPoint()->GetPosition().z() / micrometer;


  // calculate fraction of track that is in depletion zone:
  double d1 = -pixel_depletion*0.5;
  double d2 = pixel_depletion*0.5;
  double f = 1.0;  
  if (z1 > z2) swap(z1, z2);
  double z = z2 - z1;
  if (z > 0) {
    double d = min(z2,d2) - max(z1,d1);
    if (d < 0) d = 0;
    f = d / z;
  }
    
  //cout << "INFO: hit at physical volume named:  " << pv->GetName() << "\n";
  int index;
  sscanf(pv->GetName(), "Photodiode_%d", &index);
  //cout << "INFO: parsed the index as:  " << index << "\n";


  G4String name = step->GetTrack()->GetDefinition()->GetParticleName();
  G4double edepStep = step->GetTotalEnergyDeposit() - step->GetNonIonizingEnergyDeposit();

  if (name == "e-"){
    G4double evert = step->GetTrack()->GetVertexKineticEnergy();
    if (evert > evt_.cmax) evt_.cmax = evert; 
  }
  
  evt_.edep   += edepStep; 
  evt_.nonion += step->GetNonIonizingEnergyDeposit();
  evt_.adep   += f*edepStep; 

  if ((index >= 0) && (index < grid_max)){ 
    grid_edep[index] += f*edepStep;
  } else {
    cout << "ERROR: grid index out of range!!!\n";
  }

  if (name == "gamma"){
    evt_.g_edep += edepStep; 
    evt_.g_hit++;
  }
  if (name == "e-"){
    evt_.e_edep += edepStep; 
    evt_.e_hit++;;
  }
  if (name == "mu-"){
    evt_.m_edep += edepStep; 
    evt_.m_hit++;;
  }
  // Let us know if anything out-of-the-ordinary shows up:
  if ((name != "gamma")&&(name != "e-")&&(name != "mu-")){
    G4cout
      << "INFO:  A particle of type "
      << name
      << " has struck the photodiode."
      << G4endl;
  }
}

void Analysis::BeginEvent(const G4Event*)
{   
  events++;
  if (!(events  % 10000)) cout << "PROGRESS:  event count " << events << "\n";
  evt_.reset();
  for (int i=0; i<grid_max; i++){
    if (grid_edep) grid_edep[i] = 0;
  }

  for (int i=0; i<cell_max; i++){
    if (cell_edep) cell_edep[i] = 0;
  }

}

void Analysis::EndEvent(const G4Event*)
{   
  if (evt_.g_hit > 0) run_.g_hit++;
  if (evt_.e_hit > 0) run_.e_hit++;
  if (evt_.m_hit > 0) run_.m_hit++;
  run_.g_edep += evt_.g_edep;
  run_.e_edep += evt_.e_edep;
  run_.m_edep += evt_.m_edep;
  run_.edep   += evt_.edep;
  run_.nonion += evt_.nonion;
  run_.adep   += evt_.adep;  

  if (evt_.cmax > run_.cmax) run_.cmax = evt_.cmax;

  if (evt_.edep > 0.0){
    edep_evt++;
  }
  if (evt_.adep > 0.0){
    adep_evt++;
    FillNtuple();
  }
}

void Analysis::BeginRun(const G4Run*)
{ 
  //inform the runManager to save random number seed
  G4RunManager::GetRunManager()->SetRandomNumberStore(false);
  Analysis::instance()->Book();
  run_.reset();
  edep_evt = 0;
  adep_evt = 0;
  events = 0;
}

void Analysis::EndRun(const G4Run* run)
{
  G4int nofEvents = run->GetNumberOfEvent();
  if (nofEvents == 0) return;
 
  Analysis::instance()->Save();

  // Run conditions
  //  note: There is no primary generator action object for "master"
  //        run manager for multi-threaded mode.
  const PDPrimaryGeneratorAction* generatorAction
   = static_cast<const PDPrimaryGeneratorAction*>
     (G4RunManager::GetRunManager()->GetUserPrimaryGeneratorAction());
  G4String runCondition;
  if (generatorAction)
  {
    const G4ParticleGun* particleGun = generatorAction->GetParticleGun();
    runCondition += particleGun->GetParticleDefinition()->GetParticleName();
    runCondition += " of ";
    G4double particleEnergy = particleGun->GetParticleEnergy();
    runCondition += G4BestUnit(particleEnergy,"Energy");
  }
         
   G4double avg_edep = 0.0;
   G4double avg_adep = 0.0;
  
   if (edep_evt > 0) avg_edep = run_.edep / edep_evt;
   if (adep_evt > 0) avg_adep = run_.adep / adep_evt;

  G4cout
     << G4endl
     << " The run consists of " << nofEvents << " " << runCondition << G4endl
     << " evts with non-zero energy:  " << edep_evt << G4endl
     << " evts with gamma hit:  " << run_.g_hit << G4endl
     << " evts with e- hit:     " << run_.e_hit << G4endl
     << " evts with muon hit:   " << run_.m_hit << G4endl
     << " evts with non-zero energy in depletion zone:  " << adep_evt << G4endl

     << " total nonionizing energy deposited:   " << G4BestUnit(run_.nonion, "Energy") << G4endl

     << " total energy deposited:   " << G4BestUnit(run_.edep, "Energy") << G4endl
     << "  - by gamma:               " << G4BestUnit(run_.g_edep, "Energy") << G4endl
     << "  - by electrons:           " << G4BestUnit(run_.e_edep, "Energy") << G4endl
     << "  - by muons:               " << G4BestUnit(run_.m_edep, "Energy") << G4endl
     << " for events with non-zero energy, avg energy deposited:   " << G4BestUnit(avg_edep, "Energy") << G4endl

     << " total energy deposited in pixel depletion zone:   " << G4BestUnit(run_.adep, "Energy") << G4endl
     << " for events with non-zero energy in depletion zone, avg energy deposited:   " << G4BestUnit(avg_adep, "Energy") << G4endl


    // << "------------------------------------------------------------"
     << G4endl;

}


// G4 zealously deletes our classes for us, so need this bit of misdirection for a clean exits:

class AnalysisRunAction :  public G4UserRunAction {
public:
  virtual void   BeginOfRunAction(const G4Run*r) {Analysis::instance()->BeginRun(r); }
  virtual void   EndOfRunAction(const G4Run*r) {Analysis::instance()->EndRun(r); }  
};

class AnalysisStepAction :  public G4UserSteppingAction{
  virtual void   UserSteppingAction(const G4Step* step) {Analysis::instance()->Step(step); }
};
													   
class AnalysisEventAction :   public G4UserEventAction{
  virtual void   BeginOfEventAction (const G4Event* evt) {Analysis::instance()->BeginEvent(evt); }
  virtual void   EndOfEventAction   (const G4Event* evt) {Analysis::instance()->EndEvent(evt);   }
};

void AnalysisActionInit::BuildForMaster() const
{
  SetUserAction(new AnalysisRunAction());
}

void AnalysisActionInit::Build() const
{
  SetUserAction(new PDPrimaryGeneratorAction);
  SetUserAction(new AnalysisRunAction);
  SetUserAction(new AnalysisEventAction);
  SetUserAction(new AnalysisStepAction);
}  

