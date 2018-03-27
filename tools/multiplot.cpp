#include "TH1F.h"
#include "TCanvas.h"
#include "TFile.h"
#include "TImage.h"

int main(int argc, char** argv) {

  TString inputfile(argv[1]);
  TString outputfile(argv[2]);
  const int Nchannels	= std::atoi(argv[3]); // 15360 in the real TPC
  
  TFile* inFile= new TFile(inputfile.Data());

  TCanvas* cnv = new TCanvas("cnv","Channel histograms", 3200, 1800);
  cnv->Divide(10,10);
    
  for(Int_t nch=0; nch<Nchannels; nch++) {
    TH1F* chanHist = (TH1F*) inFile->Get(TString(Form("c%d", nch)));

    cnv->cd(nch+1);
    chanHist->Draw();
  }

  TImage *img = TImage::Create();
  img->FromPad(cnv);
  img->WriteImage(outputfile.Data());

  return 0;
}
