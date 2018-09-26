#include <math.h>
#include <iostream>
using namespace std;

#include "PDPrimaryGeneratorAction.hh"

#include "G4LogicalVolumeStore.hh"
#include "G4LogicalVolume.hh"
#include "G4Box.hh"
#include "G4RunManager.hh"
#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4SystemOfUnits.hh"
#include "Randomize.hh"
#include "Analysis.hh"

PDPrimaryGeneratorAction::PDPrimaryGeneratorAction()
: G4VUserPrimaryGeneratorAction(),
  fParticleGun(0), 
  fEnvelopeBox(0)
{
  G4int n_particle = 1;
  fParticleGun  = new G4ParticleGun(n_particle);

  // default particle kinematic
  G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
  G4String particleName;
  G4ParticleDefinition* particle
    = particleTable->FindParticle(particleName="gamma");
  fParticleGun->SetParticleDefinition(particle);
  fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0.,0.,1.));
  fParticleGun->SetParticleEnergy(6.*MeV);
}

PDPrimaryGeneratorAction::~PDPrimaryGeneratorAction()
{
  delete fParticleGun;
}

void PDPrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent)
{
  G4double envSizeX = 0;
  G4double envSizeY = 0;
  G4double envSizeZ = 0;


  G4double gen_theta = Analysis::instance()->gen_theta;
  G4double gen_theta_max = Analysis::instance()->gen_theta_max;
  G4double gen_phi_max = Analysis::instance()->gen_phi_max;
  G4double pixel_width = Analysis::instance()->pixel_width;

  if ((gen_theta_max != 0) && (gen_theta != 0)){
    G4ExceptionDescription msg;
    msg << "Inconsistent settings for gen_theta and gen_theta_max.\n"; 
    G4Exception("PDPrimaryGeneratorAction::GeneratePrimaries()",
     "MyCode0002",JustWarning,msg);
  }

  if (gen_theta_max > 0.0){
    double x,y;
    do{
      gen_theta = G4UniformRand() * gen_theta_max;
      x = G4UniformRand();
      if (Analysis::instance()->cosmic_mode == 1){
	y = cos(gen_theta);
	y = y*y;
      } else {
	y = sin(gen_theta);
      }

    } while(x > y);
  }
  
  double gen_phi = 0.0;
  if (gen_phi_max > 0.0){
    gen_phi = G4UniformRand() * gen_phi_max;
  }

  Analysis::instance()->evt_phi   = gen_phi;
  Analysis::instance()->evt_theta = gen_theta;
  
  if (!fEnvelopeBox)
  {
    G4LogicalVolume* envLV
      = G4LogicalVolumeStore::GetInstance()->GetVolume("Envelope");
    if ( envLV ) fEnvelopeBox = dynamic_cast<G4Box*>(envLV->GetSolid());
  }

  if ( fEnvelopeBox ) {
    envSizeX = fEnvelopeBox->GetXHalfLength()*2.;
    envSizeY = fEnvelopeBox->GetYHalfLength()*2.;
    envSizeZ = fEnvelopeBox->GetZHalfLength()*2.;
  }  
  else  {
    G4ExceptionDescription msg;
    msg << "Envelope volume of box shape not found.\n"; 
    msg << "Perhaps you have changed geometry.\n";
    msg << "The gun will be place at the center.";
    G4Exception("PDPrimaryGeneratorAction::GeneratePrimaries()",
     "MyCode0002",JustWarning,msg);
  }

  G4double rho = tan(gen_theta) * envSizeZ;
  G4double x0  = cos(gen_phi) * rho;
  G4double y0  = sin(gen_phi) * rho;
  G4double z0  = -0.5 * envSizeZ;
  G4double r   = sqrt(x0*x0 + y0*y0 + z0*z0);
  G4double sx = (G4UniformRand()-0.5)*pixel_width*micrometer;
  G4double sy = (G4UniformRand()-0.5)*pixel_width*micrometer;

  //cout << "rho:  " << rho << "\n";
      
  fParticleGun->SetParticlePosition(G4ThreeVector(x0+sx,y0+sy,z0));
  fParticleGun->SetParticleMomentumDirection(G4ThreeVector(-x0/r,-y0/r,-z0/r));
  fParticleGun->GeneratePrimaryVertex(anEvent);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

