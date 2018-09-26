#include <fstream>

int flat_index(int iy,int ix){
  int width = 10;
  return width*iy +ix;
}

void analyze(){
  ofstream f;

  gStyle->SetOptStat(0);
  
  TFile * f1 = new TFile("pdout.root");
  TTree * edep = (TTree*) (f1->Get("edep"));

  edep->Print();

			   
  float gedep[200];
  edep->SetBranchAddress("cell_edep", &gedep);
  

  f.open("ntuple.txt");
  for(int ievt = 0; ievt < edep->GetEntries(); ievt++){
      edep->GetEntry(ievt);

      double e1 = 0;
      double e2 = 0;  
      int nh = 0;
      int x1=0;
      int y1=0;

      for (int ix=0; ix<10; ix++){  
	for (int iy=0; iy<10; iy++){
	  double e = gedep[flat_index(ix,iy)];
	  if (e > e1) {
	    e1 = e;
	    x1 = ix;
	    y1 = iy;
	  }
	}
      }
      
      for (int dx=-1; dx<=1; dx++){  
	ix = x1 + dx;
	if (ix < 0) continue;
	if (ix > 10) continue;
	for (int dy=-1; dy<=1; dy++){
	  if ((dx==0) && (dy==0)) continue;
	  iy = y1 + dy;
	  if (iy < 0) continue;
	  if (iy > 10) continue;
	  double e = gedep[flat_index(ix,iy)];
	  //cout << dx << ", " << dy << ": " << e << "\n";
	  if (e > e2) {
	    e2 = e;
	  }	  
	}
      }

      for (int ix=0; ix<10; ix++){  
	for (int iy=0; iy<10; iy++){
	  double e = gedep[flat_index(ix,iy)];
	  if (e > e1*0.5) nh++;
	}
      }

      cout << e1 << " " << e2 << " " << nh << "\n";
      f << e1 << " " << e2 << " " << nh << "\n";
  }
  f.close();
}
