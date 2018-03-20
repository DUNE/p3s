// This tool adds histograms and keeps them in a dedicated "accumulator file"
//
// "init mode": Initialize a file which will serve as the accumulator for histograms
// "add mode": add another file to the accumulator

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



int main(int argc, char** argv)
{
  const double pedLow	= 0.;
  const double pedHi	= 100.;
  const int pedBins	= 100;
  
  std::string mode(argv[1]);

  if(mode.compare("-h") == 0 || mode.compare("help") == 0 || mode.compare("--help") == 0 ) {
    std::cout << "Usage:\n"
	      << "1st argument is always the mode - 'help', 'init', or 'add'\n\n"
	      << "In the init mode, the second argument is the name of the file\n"
	      << "to be initialized, and the third is the number of channels.\n\n"
	      << "In the add mode, the arguments are the name of the accumulator file and\n"
	      << "the file to be added."
	      << std::endl;
    return 0;
  }
  
  if(mode.compare("init") == 0) {
    TString accumulatorFileName(argv[2]);
    std::cout << "init mode for file " << accumulatorFileName.Data()  << std::endl;

    const int Nchannels	= std::atoi(argv[3]); // 15360 in the real TPC
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
  

