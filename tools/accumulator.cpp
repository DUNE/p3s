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
    TString accumulatorFileName(argv[2]);
    std::cout << "init mode for file " << accumulatorFileName.Data()  << std::endl;

    const int Nchannels	= std::stoi(argv[3]); // 15360 in the real TPC
    TH1F* peds[Nchannels];

    TFile * hfile = new TFile(accumulatorFileName.Data(),"CREATE","histogram accumulator");

    for(Int_t nch=0; nch<Nchannels; nch++) {
      TString numString	= TString(Form("c%d", nch));
      TString title	= TString(Form("Cumulative Pedestal %d;Channel;Count", nch));
    
      peds[nch] = new TH1F(numString, title, pedBins, pedLow, pedHi);
      peds[nch]->SetFillColor(48);
      peds[nch]->Sumw2();
    }

    hfile->Write();
    hfile->Close();

    return 0;
  }
  

  if(mode.compare("add") == 0) {
    TString accumulatorFileName(argv[2]);
    TString addFileName(argv[3]);
    std::cout << "add mode for file " << accumulatorFileName.Data() << ", adding file "<< addFileName.Data() << std::endl;

    TFile* accFile	= new TFile(accumulatorFileName.Data(), "UPDATE");
    TFile* addFile	= new TFile(addFileName.Data());
      
    TList* accList	= accFile->GetListOfKeys();
    TList* addList	= addFile->GetListOfKeys();
    
    Int_t accChannels	= accList->GetEntries();
    Int_t addChannels	= addList->GetEntries();
    
    if(accChannels!=addChannels) {
      std::cout << "Channel count does not match: accumulator file "<< accChannels
		<< ", added file " << addChannels << ", exiting..." << std::endl;
      return -1;
    }

    Int_t Nchannels = addChannels;

    accFile->cd();
    gDirectory->pwd();
    
    for(Int_t nch=0; nch<Nchannels; nch++) {
      TH1F* accHist	= (TH1F*) accFile->Get(TString(Form("c%d", nch)));
      TH1F* addHist	= (TH1F*) addFile->Get(TString(Form("p%d", nch)));

      accHist->Add(addHist);
      //      accHist->Write("",TObject::kOverwrite);
    }

    accFile->cd();
    accFile->Write("",TObject::kOverwrite);
    accFile->Close();

    return 0;
  }
}

// Dusty attic
// TH1F *sum = new TH1F("sum", "sum", pedBins, pedLow, pedHi);

// TH1F *h1 = (TH1F*)gDirectory->Get("0");
// sum->Add(h1);
  

