#ifndef Analysis_h
#define Analysis_h 1

#include <iostream>
#include <fstream>

#include "globals.hh"
#include "G4UImessenger.hh"
#include "G4UserRunAction.hh"
#include "G4UserEventAction.hh"
#include "G4UserSteppingAction.hh"
#include "G4VUserActionInitialization.hh"

#define CELL_GRID_SIZE 5

class G4UIcmdWithADouble;
class G4UIcmdWithAnInteger;
class G4Step;
class G4Event;
class G4Run;
class G4UIdirectory;
class G4LogicalVolume;

class AnalysisActionInit :  public G4VUserActionInitialization {
public:
  AnalysisActionInit() : G4VUserActionInitialization() {}
  virtual ~AnalysisActionInit() {}  
  virtual void   BuildForMaster() const;
  virtual void   Build() const;          
};

class Analysis: 
  public G4UImessenger
{
  public:
  Analysis();
  virtual ~Analysis();  
  
  static Analysis * instance(){return instance_;}

  void   Step(const G4Step*);
  void   BeginRun(const G4Run*);
  void   EndRun(const G4Run*);
  void   BeginEvent(const G4Event*);
  void   EndEvent(const G4Event*);
  void   Book(int expected);
  void   Save();
  void   FillNtuple();      

  // statistics:
  struct stats {
    int   g_hit;    
    int   e_hit;    
    int   m_hit;    
    float g_edep;
    float e_edep;
    float m_edep;
    float edep;
    float nonion;
    float adep; // deposited energy in depletion zone
    float cmax; // max energy of compton scattered electron
    void reset();
  };
  stats run_;
  stats evt_;
  int edep_evt;
  int adep_evt;

  int grid_max;
  float * grid_edep;

  int cell_max;
  float * cell_edep;

  float edep1;
  int index1;

  float evt_theta; 
  float evt_phi;


  // config parameters:
  int    cosmic_mode;  //0=no 1=cos2
  double slab_depth;  
  double slab_gap;  
  double pixel_depletion;  
  double pixel_depth;  
  double pixel_width;
  int    pixel_max_x;  // total number of pixels in x = (2*pixel_max_x + 1) 
  int    pixel_max_y;  // total number of pixels in y = (2*pixel_max_y + 1) 
  double gen_theta; // fire at a fixed angle
  double gen_theta_max; // 0 for fixed theta, or max theta from a point source drawn from sin(theta) dtheta
  double gen_phi_max; // 0 for fixed phi, or max phi for flat in phi (0 or pi/2 are sensible choices)

  // track progress:
  int events;


  // set config parameters:
  virtual void SetNewValue(G4UIcommand * command,G4String arg);

private:
  G4UIdirectory*        analysisDir_; 
  G4UIcmdWithAnInteger* cosmicModeCmd_; 
  G4UIcmdWithADouble*   slabDepthCmd_;
  G4UIcmdWithADouble*   slabGapCmd_;
  G4UIcmdWithADouble*   pixelDepletionCmd_;
  G4UIcmdWithADouble*   pixelDepthCmd_;
  G4UIcmdWithADouble*   pixelWidthCmd_;
  G4UIcmdWithAnInteger* pixelMaxXCmd_;
  G4UIcmdWithAnInteger* pixelMaxYCmd_;
  G4UIcmdWithADouble*   genThetaCmd_;
  G4UIcmdWithADouble*   genThetaMaxCmd_;
  G4UIcmdWithADouble*   genPhiMaxCmd_;

  static Analysis * instance_;
  G4LogicalVolume* scoringVolume_;

  std::ofstream * output_;
};


#endif

    
