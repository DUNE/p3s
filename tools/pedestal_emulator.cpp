// Loosely based on the ROOT tutorial
// Generate histograms - with configurable statistics and number as channels in protoDUNE TPC

#include <TFile.h>
#include <TNtuple.h>
#include <TH2.h>
#include <TProfile.h>
#include <TCanvas.h>
#include <TFrame.h>
#include <TROOT.h>
#include <TSystem.h>
#include <TRandom3.h>
#include <TBenchmark.h>
#include <TInterpreter.h>
#include <iostream>



// Arguments:
// 1 root file name for output
// 2 number of TPC channels
// 3 number of entries in each histogram

int main(int argc, char** argv)
{
  const double pedLow	= 0.;
  const double pedHi	= 100.;
  const int pedBins	= 100;
  
  TString thefilename(argv[1]);
  const int Entries	= std::stoi(argv[2]);
  const int Nchannels	= std::stoi(argv[3]); // 15360 in the real TPC
  
  // std::cout << thefilename << std::endl;
  // std::cout << Entries << std::endl;
  // std::cout << Nchannels << std::endl;

  TH1F* peds[Nchannels];

  TRandom3 randomNum;
  Float_t px, py;
  
  TFile * hfile = new TFile(thefilename.Data(),"RECREATE","Demo ROOT file with histograms");
  
  for(Int_t nch=0; nch<Nchannels; nch++) {
    TString numString = TString(Form ("%d", nch));
    // std::cout << numString << std::endl;
    TString title = TString("Channel ")+numString;
    peds[nch] = new TH1F(numString, title, pedBins, pedLow, pedHi);
    peds[nch]->SetFillColor(48);
    peds[nch]->Sumw2();
    
    for (Int_t i = 0; i < Entries; i++) {
      randomNum.Rannor(px,py);
      peds[nch]->Fill(px*pedBins, py);
    }
    
    peds[nch]->Scale(double(pedBins)/double(Entries));
    //    peds[nch]->SetMinimum(0.);
  }

  hfile->Write();
  hfile->Close();
  
  return 0;
}
