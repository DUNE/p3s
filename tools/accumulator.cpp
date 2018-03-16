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
  
  std::string mode(argv[1]);

  if(mode.compare("init") == 0) {
    TString thefilename(argv[2]);
    std::cout << "init mode for file " << thefilename.Data()  << std::endl;
    const int Nchannels	= std::stoi(argv[3]); // 15360 in the real TPC

    TFile * hfile = new TFile(thefilename.Data(),"CREATE","histogram accumulator");

  }
  
  return 0;
  
  const int Entries	= std::stoi(argv[2]);
  const int Nchannels	= std::stoi(argv[3]); // 15360 in the real TPC
  TFile* f	= new TFile("dd");
  f->ls();
  TH1F* h0 = (TH1F*) f->Get("0");
  h0->Draw();
  std::cin.get();
  return 0;


  // TH1F *sum = new TH1F("sum", "sum", pedBins, pedLow, pedHi);

  // TH1F *h1 = (TH1F*)gDirectory->Get("0");
  // sum->Add(h1);
  
  // hfile->Write();
  // hfile->Close();
  
  // return 0;
}
