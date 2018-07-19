// This is a tool for generation of mockup histograms to test p3s.
//
// Configurable statistics and number of channels.

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
// 2 number of entries in each histogram
// 3 number of TPC channels

int main(int argc, char** argv)
{
  const double pedLow	= 0.;
  const double pedHi	= 100.;
  const int pedBins	= 100;
  
  std::string mode(argv[1]);

  if(mode.compare("-h") == 0 || mode.compare("help") == 0 || mode.compare("--help") == 0 ) {
    std::cout << "Arguments:\n"
	      << "1st argument can be - 'help', which prints this message\n"
	      << "Otherwise, it's the name of the output file\n\n"
	      <<"2nd argument: entries in the histogram (statistics)\n\n"
	      << "3rd is the number of channels."
	      << std::endl;
    return 0;
  }
  
  TString thefilename(mode);


  
  const int Entries	= std::atoi(argv[2]);
  const int Nchannels	= std::atoi(argv[3]); // 15360 in the real TPC
  
  // std::cout << thefilename << std::endl;
  // std::cout << Entries << std::endl;
  // std::cout << Nchannels << std::endl;

  TH1F* peds[Nchannels];

  TRandom3 randomNum;
  Float_t px, py;
  
  TFile* hfile = new TFile(thefilename.Data(),"RECREATE","protoDUNE pedestal emulator for testing");
  
  for(Int_t nch=0; nch<Nchannels; nch++) {
    TString numString	= TString(Form("p%d", nch));
    TString title	= TString(Form("Pedestal %d;Channel;Count", nch));
    
    peds[nch] = new TH1F(numString, title, pedBins, pedLow, pedHi);
    peds[nch]->SetFillColor(48);
    peds[nch]->Sumw2();
    
    for (Int_t i = 0; i < Entries; i++) {
      randomNum.Rannor(px,py);
      peds[nch]->Fill((0.2*px)*pedBins, 1.0);
    }
    
    //    peds[nch]->Scale(double(pedBins)/double(Entries));
    //    peds[nch]->SetMinimum(0.);
  }

  hfile->Write();
  hfile->Close();
  
  return 0;
}
