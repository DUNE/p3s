// makeplotsV2.C
// to execute non-interactively:  root -b -l -q 'makeplotsV2.C("rawtpcmonitor.root");'
// root -b -l -q 'makeplotsV2.C("rawtpcmonitor.root");' > /dev/null 2>&1

#include <string.h>
#include <stdio.h>
#include <time.h>
#include <vector>
#include <algorithm>

#include "TChain.h"
#include "TFile.h"
#include "TH1.h"
#include "TTree.h"
#include "TKey.h"
#include "Riostream.h"
#include "TCanvas.h"
#include "TProfile.h"
#include "TString.h"
#include "TStopwatch.h"
#include "TRegexp.h"
#include "TDatime.h"
#include "TVirtualPad.h"
#include "TObjArray.h"

//TFile *Target;
TCanvas *c1;
FILE *indexhtml_main;

const int exp_deadch = 0;
const int exp_noisych1 = 0;
const int exp_noisych2 = 0;

bool VERBOSE = false;

void FindRunAndTime(TDirectory *dir, ULong64_t& TimeStamp, TString& runid, TString& currentdate);
std::vector<TString> FindDirectories(TDirectory *dir);
TObjArray* SaveHistosFromDirectory(TDirectory *dir, TString runname, TString datename);
int PrintListofDeadNoisyChannels(TObjArray* dir, TString histoname, TString outfilename);
void PrintDeadNoisyChannelsJson(TDirectory *dir, TString jsonfilename, TString srun, TString sdate);
void PrintGausHitsJson(TDirectory *dir, TString jsonfilename);
void PrintSummaryPlots(FILE *file, TObjArray* dir, TString keyname, TString keyname2, TString runname, bool setlogy);
void IncludeOverflow(TH1 *h);

void makeplotsV2(TString infile="np04_mon_run001113_3_dl1.root"){ // np04_mon_run001077_1_dl4.root - np04_mon_run001113_3_dl1.root

  // Silence output
  if(!VERBOSE)
    gErrorIgnoreLevel = kWarning;

  // Start timing
  TStopwatch *mn_t = new TStopwatch;
  mn_t->Start();

  // Open file
  TFile *f = new TFile(infile,"READ");

  // List name pf directories in file
  TDirectory *current_sourcedir = gDirectory;
  std::vector<TString> directories_in_file = FindDirectories(current_sourcedir);

  // Find run/subrun ID and time this run started
  TString runstr("0000"); TString datestr("00/00/00"); ULong64_t sTimeStamp = 999;
  // Loop first to find the run and the date
  for(int i=0; i < directories_in_file.size(); i++){
    TString dirstr = directories_in_file.at(i);

    if(dirstr.Contains("pdspnearlineheader")){
      current_sourcedir->cd(dirstr.Data());
      TDirectory *subdir = gDirectory;
      FindRunAndTime(subdir, sTimeStamp, runstr, datestr);
      current_sourcedir->cd("..");
      break;
    }
  }

  // Create output directory based on input file
  TRegexp re(".root");
  TString s_infile = infile;
  s_infile(re) = " ";
  //TString s_infile("TPCMonitor");

  // Define canvas
  c1 = new TCanvas("c1","c1",800,800);

  // Create main index.html file
  TString sindex_infile("index.html");
  indexhtml_main = fopen(sindex_infile.Data(),"w");
  fprintf(indexhtml_main,"<!DOCTYPE html>\n");
  fprintf(indexhtml_main,"<html>\n");
  fprintf(indexhtml_main,"<head>\n");
  fprintf(indexhtml_main,"<meta charset=utf-8 />\n");
  fprintf(indexhtml_main,"<title> DQM Monitor </title>\n");
  fprintf(indexhtml_main,"</head>\n");

  fprintf(indexhtml_main,"<body>\n");
  fprintf(indexhtml_main,"<header>\n");
  fprintf(indexhtml_main,"<h1>ProtoDUNE SP DQM Monitor</h1>\n");
  fprintf(indexhtml_main,"<br></br>\n");
  fprintf(indexhtml_main,"<nav>\n");
  fprintf(indexhtml_main,"<ul>\n");

  // Create sub-directories and json file
  for(int i=0; i < directories_in_file.size(); i++){
    TString dirstr = directories_in_file.at(i);
    if(dirstr.Contains("pdspnearlineheader")) continue;

    current_sourcedir->cd(dirstr.Data());
    TDirectory *subdir = gDirectory;
    TString subdirname = dirstr + TString("/");
    TString htmlstr = dirstr + TString(".html");

    // Create source directory where all plots are stored
    subdirname += TString("source");

    // Special for different modules
    if(dirstr.Contains("tpcmonitor")){
      subdirname = runstr + TString("_summary.json");
      PrintDeadNoisyChannelsJson(subdir, subdirname, runstr, datestr);

      fprintf(indexhtml_main,"<h3>Summary plots for %s</h3>", dirstr.Data());
      htmlstr = dirstr + TString("_DeadNoisyCh.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">Dead and noisy channels</a> </li>\n", htmlstr.Data());
      htmlstr = dirstr + TString("_ADCMeanRMS.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">Mean and RMS of ADC</a> </li>\n", htmlstr.Data());
      htmlstr = dirstr + TString("_StuckCodes.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">Stuck Codes</a> </li>\n", htmlstr.Data());
      htmlstr = dirstr + TString("_FFT.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">FFT</a> </li>\n", htmlstr.Data());
    }
    if(dirstr.Contains("pdsphitmonitor")){
      subdirname = runstr + TString("_summary.json");
      PrintGausHitsJson(subdir, subdirname);

      fprintf(indexhtml_main,"<h3>Summary plots for %s</h3>", dirstr.Data());
      htmlstr = dirstr + TString("_NHitsAPA.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">Hit analysis summary</a> </li>\n", htmlstr.Data());
      htmlstr = dirstr + TString("_NHitsAPAProfiled.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">Profiled hit analysis summary</a> </li>\n", htmlstr.Data());
    }
    if(dirstr.Contains("sspmonitor")){
      fprintf(indexhtml_main,"<h3>Summary plots for %s</h3>", dirstr.Data());

      htmlstr = dirstr + TString("_SSPMonitorSummary.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">SSP monitor summary</a> </li>\n", htmlstr.Data());
      htmlstr = dirstr + TString("_SSPMonitorPeakAmplitudes.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">SSP monitor Peak Amplitudes</a> </li>\n", htmlstr.Data());
      htmlstr = dirstr + TString("_SSPMonitorPeakAreas.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">SSP monitor Peak Areas</a> </li>\n", htmlstr.Data());
      htmlstr = dirstr + TString("_SSPMonitorFFT.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">SSP monitor FFT</a> </li>\n", htmlstr.Data());
      htmlstr = dirstr + TString("_SSPMonitorEvent.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">SSP monitor Event</a> </li>\n", htmlstr.Data());
      htmlstr = dirstr + TString("_SSPMonitorWaveform.html");
      fprintf(indexhtml_main,"<li> <a href=\"%s\">SSP monitor Waveform</a> </li>\n", htmlstr.Data());
    }

    current_sourcedir->cd("..");
  }

  fprintf(indexhtml_main,"<h2>Links to all DQM Monitor plots</h2>\n");
  for(int i=0; i < directories_in_file.size(); i++){
    TString dirstr = directories_in_file.at(i);
    if(dirstr.Contains("pdspnearlineheader")) continue;

    TString htmlstr = dirstr + TString(".html");
    fprintf(indexhtml_main,"<li> <a href=\"%s\">%s</a> </li>\n", htmlstr.Data(), dirstr.Data());
  }
  
  fprintf(indexhtml_main,"</ul>\n");
  fprintf(indexhtml_main,"</nav>\n");
  fprintf(indexhtml_main,"</header>\n");

  fprintf(indexhtml_main,"<h1>Time series plots should go here</h1>\n");
  fprintf(indexhtml_main,"</body>\n");
  fprintf(indexhtml_main,"</html>\n");
  // Close index.html file
  fclose(indexhtml_main);

  // Loop to save histograms
  for(int i=0; i < directories_in_file.size(); i++){
    TString dirstr = directories_in_file.at(i);

    if(dirstr.Contains("pdspnearlineheader")) continue;
    current_sourcedir->cd(dirstr.Data());
    TDirectory *subdir = gDirectory;
    
    // Save all histograms
    TObjArray* vec = SaveHistosFromDirectory(subdir, runstr, datestr);
    vec->SetName(subdir->GetName()); // important

    // Make sumamry plot for tpcmonitor - this should probably move to its own class
    if(dirstr.Contains("tpcmonitor")){
      //std::cout << "INFO::Attempting to plot from " << dirstr.Data() << std::endl;
      TString infile = dirstr + TString("_DeadNoisyCh.html");
      FILE *indexhtml1;
      
      int ndeadch = PrintListofDeadNoisyChannels(vec, "fNDeadChannelsList", "fNDeadChannelsList");
      int nnoise1 = PrintListofDeadNoisyChannels(vec, "fNNoisyChannelsListFromNSigma", "fNNoisyChannelsListFromNSigma");
      int nnoise2 = PrintListofDeadNoisyChannels(vec, "fNNoisyChannelsListFromNCounts", "fNNoisyChannelsListFromNCounts");

      indexhtml1 = fopen(infile.Data(),"w");
      fprintf(indexhtml1,"<h1>Summary of dead and noisy channels</h1>\n");
      fprintf(indexhtml1,"<br><br>\n");
      fprintf(indexhtml1,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml1,"<br><br>\n");

      // Print warnings if number of dead/noisy is different from the expected
      if(ndeadch == exp_deadch)
	fprintf(indexhtml1,"<h3>Number of dead channels: %i</h3>\n",ndeadch);
      else
	fprintf(indexhtml1,"<font size=4 color=red>WARNING: number of dead channels is %i. Expected dead channels %i.</font>\n", ndeadch, exp_deadch);

      fprintf(indexhtml1,"<br>\n");

      if(nnoise1 == exp_noisych1)
	fprintf(indexhtml1,"<h3>Number of noisy channels: %i</h3>\n",nnoise1);
      else
	fprintf(indexhtml1,"<font size=4 color=red>WARNING: number of noisy channels is %i. Expected noisy channels %i.</font>\n", nnoise1, exp_noisych1);

      fprintf(indexhtml1,"<br>\n");

      if(nnoise2 == exp_noisych2)
	fprintf(indexhtml1,"<h3>Number of noisy channels above threshold: %i</h3>\n",nnoise2);
      else
	fprintf(indexhtml1,"<font size=4 color=red>WARNING: number of noisy channels above threshold is %i. Expected noisy channels %i.</font>\n", nnoise2, exp_noisych2);

      fprintf(indexhtml1,"<br><br>\n");
      fprintf(indexhtml1,"<div>\n");
      fprintf(indexhtml1,"<a href=%s>List of dead channels</a>\n", "fNDeadChannelsList.txt");
      fprintf(indexhtml1,"<a href=%s>List of noisy channels</a>\n", "fNNoisyChannelsListFromNSigma.txt");
      fprintf(indexhtml1,"<a href=%s>List of noisy channels above threshold</a>\n", "fNNoisyChannelsListFromNCounts.txt");
      fprintf(indexhtml1,"</div>\n");

      fprintf(indexhtml1,"<br><br>\n");
      
      // Make the summary plots
      fprintf(indexhtml1,"<div>\n");

      fprintf(indexhtml1,"<h3>Dead channels summary</h3>\n");
      PrintSummaryPlots(indexhtml1, vec, "fN", "ChannelsHisto", runstr, false);
      fprintf(indexhtml1,"<h3>Noisy channels summary</h3>\n");
      PrintSummaryPlots(indexhtml1, vec, "fN", "ChannelsList", runstr, false);
      // Close html file
      fclose(indexhtml1);

      FILE *indexhtml2;
      infile = dirstr + TString("_ADCMeanRMS.html");
      indexhtml2 = fopen(infile.Data(),"w");
      fprintf(indexhtml2,"<h1>Summary of ADC distributions</h1>\n");
      fprintf(indexhtml2,"<br><br>\n");
      fprintf(indexhtml2,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml2,"<br><br>\n");

      fprintf(indexhtml2,"<h3>RMS of ADC per channel</h3>\n");
      PrintSummaryPlots(indexhtml2, vec, "fChanRMS", "pfx", runstr, false);
      fprintf(indexhtml2,"<h3>Mean of ADC per channel</h3>\n");
      PrintSummaryPlots(indexhtml2, vec, "fChanMean", "pfx", runstr, false);
      fprintf(indexhtml2,"<h3>RMS of ADC from all channels</h3>\n");
      PrintSummaryPlots(indexhtml2, vec, "fChanRMS", "Dist", runstr, false);
      fprintf(indexhtml2,"<h3>Mean of ADC from all channels</h3>\n");
      PrintSummaryPlots(indexhtml2, vec, "fChanMean", "Dist", runstr, false);
      fprintf(indexhtml2,"<h3>RMS of ADC from slots</h3>\n");
      PrintSummaryPlots(indexhtml2, vec, "Slot", "RMS", runstr, false);
      fprintf(indexhtml2,"<h3>Mean of ADC from slots</h3>\n");
      PrintSummaryPlots(indexhtml2, vec, "Slot", "Mean", runstr, false);
      // Close html file
      fclose(indexhtml2);
      
      FILE *indexhtml3;
      infile = dirstr + TString("_StuckCodes.html");
      indexhtml3 = fopen(infile.Data(),"w");
      fprintf(indexhtml3,"<h1>Summary of stuck codes</h1>\n");
      fprintf(indexhtml3,"<br><br>\n");
      fprintf(indexhtml3,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml3,"<br><br>\n");
      
      fprintf(indexhtml3,"<h3>Stuck Code ON</h3>\n");
      PrintSummaryPlots(indexhtml3, vec,  "fChanStuckCode", "On", runstr, false);
      fprintf(indexhtml3,"<h3>Stuck Code OFF</h3>\n");
      PrintSummaryPlots(indexhtml3, vec,  "fChanStuckCode", "Off", runstr, false);
      // Close html file
      fclose(indexhtml3);
      
      FILE *indexhtml4;
      infile = dirstr + TString("_FFT.html");
      indexhtml4 = fopen(infile.Data(),"w");
      fprintf(indexhtml4,"<h1>Summary FFT plots</h1>\n");
      fprintf(indexhtml4,"<br><br>\n");
      fprintf(indexhtml4,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml4,"<br><br>\n");

      fprintf(indexhtml4,"<h3>Persistent FFT fiber</h3>\n");
      PrintSummaryPlots(indexhtml4, vec, "Persistent", "FFT", runstr, false);
      fprintf(indexhtml4,"<h3>Profiled FFT fiber</h3>\n");
      PrintSummaryPlots(indexhtml4, vec, "Profiled", "FFT", runstr, false);
      fprintf(indexhtml4,"<h3>FFT</h3>\n");
      PrintSummaryPlots(indexhtml4, vec, "fChan", "FFT", runstr, false);
    } // end of tpcmonitor
    if(dirstr.Contains("pdsphitmonitor")){
      //std::cout << "INFO::Attempting to plot from " << dirstr.Data() << std::endl;      
      TString infile = dirstr + TString("_NHitsAPA.html");
      FILE *indexhtml1;
      indexhtml1 = fopen(infile.Data(),"w");
      fprintf(indexhtml1,"<h1>Summary of Hit analysis</h1>\n");
      fprintf(indexhtml1,"<br><br>\n");
      fprintf(indexhtml1,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml1,"<br><br>\n");

      fprintf(indexhtml1,"<h3>NHits for each view and each APA</h3>\n");
      PrintSummaryPlots(indexhtml1, vec, "NHits", "APA", runstr, false);
      fprintf(indexhtml1,"<h3>Hit Charge distribution for each view and each APA</h3>\n");
      PrintSummaryPlots(indexhtml1, vec, "Hit", "ChargeAPA", runstr, false);
      fprintf(indexhtml1,"<h3>Hit RMS distribution for each view and each APA</h3>\n");
      PrintSummaryPlots(indexhtml1, vec, "Hit", "RMSAPA", runstr, false);
      fprintf(indexhtml1,"<h3>Hit peak time for each view and each APA</h3>\n");
      PrintSummaryPlots(indexhtml1, vec, "Hit", "PeakTimeAPA", runstr, false);
      // Close html file
      fclose(indexhtml1);

      infile = dirstr + TString("_NHitsAPAProfiled.html");
      FILE *indexhtml2;
      indexhtml2 = fopen(infile.Data(),"w");
      fprintf(indexhtml2,"<h1>Summary of prfiled Hit analysis</h1>\n");
      fprintf(indexhtml2,"<br><br>\n");
      fprintf(indexhtml2,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml2,"<br><br>\n");
      

      fprintf(indexhtml2,"<h3>NHits profile</h3>\n");
      PrintSummaryPlots(indexhtml2, vec, "fNHits", "View", runstr, false);
      fprintf(indexhtml2,"<h3>Hit charge profile</h3>\n");
      PrintSummaryPlots(indexhtml2, vec, "fCharge", "View", runstr, false);
      fprintf(indexhtml2,"<h3>Hit RMS profile</h3>\n");
      PrintSummaryPlots(indexhtml2, vec, "fRMS", "View", runstr, false);
      // Close html file
      fclose(indexhtml2);
    }
    if(dirstr.Contains("sspmonitor")){
      TString infile = dirstr + TString("_SSPMonitorSummary.html");
      FILE *indexhtml1;
      indexhtml1 = fopen(infile.Data(),"w");
      fprintf(indexhtml1,"<h1>Summary of SSP Monitor</h1>\n");
      fprintf(indexhtml1,"<br><br>\n");
      fprintf(indexhtml1,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml1,"<br><br>\n");

      fprintf(indexhtml1,"<h3>Event Number</h3>\n");
      PrintSummaryPlots(indexhtml1, vec, "Event", "Number", runstr, false);
      fprintf(indexhtml1,"<h3>ADC values</h3>\n");
      PrintSummaryPlots(indexhtml1, vec, "ssp", "adc_values", runstr, false);
      fprintf(indexhtml1,"<h3>Hit times</h3>\n");
      PrintSummaryPlots(indexhtml1, vec, "ssp", "hit_times", runstr, false);

      // Close html file
      fclose(indexhtml1);

      infile = dirstr + TString("_SSPMonitorPeakAmplitudes.html");
      FILE *indexhtml2;
      indexhtml2 = fopen(infile.Data(),"w");
      fprintf(indexhtml2,"<h1>SSP Monitor Peak Amplitudes</h1>\n");
      fprintf(indexhtml2,"<br><br>\n");
      fprintf(indexhtml2,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml2,"<br><br>\n");

      PrintSummaryPlots(indexhtml2, vec, "peaks", "peaks", runstr, false);

      // Close html file
      fclose(indexhtml2);

      infile = dirstr + TString("_SSPMonitorPeakAreas.html");
      FILE *indexhtml3;
      indexhtml3 = fopen(infile.Data(),"w");
      fprintf(indexhtml3,"<h1>SSP Monitor Peak Areas</h1>\n");
      fprintf(indexhtml3,"<br><br>\n");
      fprintf(indexhtml3,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml3,"<br><br>\n");

      PrintSummaryPlots(indexhtml3, vec, "areas", "areas", runstr, false);

      // Close html file
      fclose(indexhtml3);

      infile = dirstr + TString("_SSPMonitorFFT.html");
      FILE *indexhtml4;
      indexhtml4 = fopen(infile.Data(),"w");
      fprintf(indexhtml4,"<h1>SSP Monitor FFT</h1>\n");
      fprintf(indexhtml4,"<br><br>\n");
      fprintf(indexhtml4,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml4,"<br><br>\n");

      PrintSummaryPlots(indexhtml4, vec, "fft", "channel", runstr, false);

      // Close html file
      fclose(indexhtml4);

      infile = dirstr + TString("_SSPMonitorEvent.html");
      FILE *indexhtml5;
      indexhtml5 = fopen(infile.Data(),"w");
      fprintf(indexhtml5,"<h1>SSP Monitor Events</h1>\n");
      fprintf(indexhtml5,"<br><br>\n");
      fprintf(indexhtml5,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml5,"<br><br>\n");

      PrintSummaryPlots(indexhtml5, vec, "evt", "channel", runstr, false);

      // Close html file
      fclose(indexhtml5);

      infile = dirstr + TString("_SSPMonitorWaveform.html");
      FILE *indexhtml6;
      indexhtml6 = fopen(infile.Data(),"w");
      fprintf(indexhtml6,"<h1>SSP Monitor Waveforms</h1>\n");
      fprintf(indexhtml6,"<br><br>\n");
      fprintf(indexhtml6,"<h2>%s histograms from %s taken on %s</h2>\n", dirstr.Data(), s_infile.Data(),datestr.Data());
      fprintf(indexhtml6,"<br><br>\n");

      PrintSummaryPlots(indexhtml6, vec, "persistent", "waveform", runstr, false);

      // Close html file
      fclose(indexhtml6);
    }
    
    delete vec;

    current_sourcedir->cd("..");
    
  }
  
  // Stop timing
  mn_t->Stop();
  if(VERBOSE){
    std::cout << std::endl;
    std::cout << "INFO::Total CPU  time: " << mn_t->CpuTime() << std::endl;
    std::cout << "INFO::Total real time: " << mn_t->RealTime() << std::endl;
  }
  delete mn_t;

  // Terminate root application
  gApplication->Terminate();
}

// --------------------------------------------------
std::vector<TString> FindDirectories(TDirectory *dir){
  // --------------------------------------------------

  std::vector<TString> dir_vector;

  // loop over all keys in this directory
  TIter nextkey(dir->GetListOfKeys());
  TKey *f1key, *f1oldkey=0;
  while((f1key = (TKey*)nextkey())){
    //plot only the highest cycle number for each key
    if (f1oldkey && !strcmp(f1oldkey->GetName(),f1key->GetName())) continue;

    // read object from  source file
    TObject *obj = f1key->ReadObj();

    // Object name
    TString objname(obj->GetName());

    if(obj->IsA()->InheritsFrom( TDirectory::Class()))
      dir_vector.push_back(objname);
  }

  return dir_vector;
}

// --------------------------------------------------
void FindRunAndTime(TDirectory *dir, ULong64_t& TimeStamp, TString& runid, TString& currentdate){
  // --------------------------------------------------

  // loop over all keys in this directory
  TIter nextkey(dir->GetListOfKeys());
  TKey *fkey, *foldkey=0;

  while((fkey = (TKey*)nextkey())){
    //plot only the highest cycle number for each key
    if (foldkey && !strcmp(foldkey->GetName(),fkey->GetName())) continue;

    // read object from  source file
    TObject *obj = fkey->ReadObj();

    // Object name
    TString objname(obj->GetName());

    if(obj->IsA()->InheritsFrom(TTree::Class()) ){
      if(!objname.Contains("Header")) continue;

      Int_t fRun, fSubRun; ULong64_t fTimeStamp;
      TTree *htree = (TTree*)obj;
      htree->SetBranchAddress("fRun",       &fRun);
      htree->SetBranchAddress("fSubRun",    &fSubRun);
      htree->SetBranchAddress("fTimeStamp", &fTimeStamp);
      
      Int_t runfirst = 100000000; Int_t subrunfirst = 100000000;
      Int_t runlast = -1; Int_t subrunlast = -1;
      // Find first and last runs/subruns
      for(Int_t ii = 0; ii < htree->GetEntries(); ii++){
	htree->GetEntry(ii);

	if(ii == 0){
	  TimeStamp = fTimeStamp;
	  time_t epoch = fTimeStamp;
	  currentdate = TString(asctime(gmtime(&epoch)));
	  //printf("%s", asctime(gmtime(&epoch)));
	}
	
	if(fRun < runfirst)
	  runfirst = fRun;
	
	if(fSubRun < subrunfirst)
	  subrunfirst = fSubRun;
	
	if(fRun > runlast)
	  runlast = fRun;
	
	if(fSubRun > subrunlast)
	  subrunlast = fSubRun;
      }
      
      if(runfirst != runlast){ // Multiple runs: ignore subruns
	runid.Form("run%i-%i",runfirst,runlast);
      }
      else{ // one run: find subrun(s)
	if(subrunfirst != subrunlast)
	  runid.Form("run%i_subrun%i-%i",runfirst,subrunfirst,subrunlast);
	else
	  runid.Form("run%i_subrun%i",runfirst,subrunfirst);
      }
    }
  }

}

// --------------------------------------------------
TObjArray* SaveHistosFromDirectory(TDirectory *dir, TString runname, TString datename){
  // --------------------------------------------------

  TObjArray* vec = new TObjArray();

  //outfilename += TString("source/");
  TString sourcefile_str = TString(dir->GetName()) + TString(".html"); 
  FILE *sourcefile = fopen(sourcefile_str.Data(),"w");
  fprintf(sourcefile,"<h1>All %s histograms from %s taken on %s</h1>\n", dir->GetName(), runname.Data(), datename.Data());
  fprintf(sourcefile,"<br><br>\n");
  
  // loop over all keys in this directory
  //int APANumber = 0;
  //TRegexp reg("_");
  TIter nextkey(dir->GetListOfKeys() );
  TKey *key, *oldkey=0;
  while((key = (TKey*)nextkey())){
    // plot only the highest cycle number for each key
    if (oldkey && !strcmp(oldkey->GetName(),key->GetName())) continue;

    // read object from  source file
    TObject *obj = key->ReadObj();

    vec->Add(obj);

    // Object name
    TString objname(obj->GetName());
    objname.ReplaceAll("#","_");

    if(obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1 -> make a plot
      TH1 *h = (TH1*)obj;
      
      std::string temp_str(objname.Data());
      temp_str.erase(std::remove(temp_str.begin(), temp_str.end(), '_'), temp_str.end());
      TString HistoNameOrig(temp_str.c_str());
      //HistoNameOrig.ReplaceAll("#","_");
      //HistoNameOrig(reg) = "F";
      
      TString HistoTitle = runname + TString(" : ") + TString(h->GetTitle());
      TString HistoName = runname + TString("_") + TString(dir->GetName()) + TString("_") + HistoNameOrig;

      TH1 *h1 = (TH1*)h->Clone("hnew");
      h1->SetDirectory(0);
      h1->SetTitle(HistoTitle.Data());
      h1->SetName(HistoName.Data());

      h1->GetXaxis()->SetTitle(h->GetXaxis()->GetTitle());
      h1->GetYaxis()->SetTitle(h->GetYaxis()->GetTitle());
      h1->GetYaxis()->SetTitleOffset(1.2);

      if(h1->GetNbinsY()==1){
        if(obj->IsA()->InheritsFrom(TProfile::Class())){
	  h1->SetStats(false);
	  h1->Draw("e0");
	}
	else{
	  h1->SetStats(true);
	  h1->Draw("hist");
	  IncludeOverflow(h1);
	}
      }
      else{
        h1->SetStats(false);
        h1->Draw("colz");
      }

      // Add second line of title
      gPad->Update();
      TPaveText * pt = (TPaveText *)gPad->FindObject("title");
      TString datename_new = TString("(Run taken on ") + datename + TString(")");
      pt->InsertText(datename_new.Data());
      pt->SetX1NDC(0.05);   pt->SetY1NDC(0.9);
      pt->SetX2NDC(0.75);    pt->SetY2NDC(0.99);
      pt->SetTextSize(0.03);
      pt->Draw();
    
      //TString outfilename2 = TString(dir->GetName()) + TString("_");//=outfilename;
      TString figname = h1->GetName(); //key->GetName();
      //figname.ReplaceAll("#","_");
      figname += ".png";
      //outfilename2 += figname;

      //c1->SaveAs(outfilename2.Data());
      c1->SaveAs(figname.Data());
      /*
      // Split plots into themes
      TString APAString = Form("APA%i",APANumber);
      if(HistoTitle.Contains(APAString.Data()) && APANumber == 0){
        fprintf(sourcefile,"<hr>\n");
	fprintf(sourcefile,"<p style=\"color: green; font-size: 300%; background-color: #ffff42\"> %s </p>\n",APAString.Data());
        APANumber++;
      }
      else if(HistoTitle.Contains(APAString.Data()) && APANumber == 1){
        fprintf(sourcefile,"<hr>\n");
	fprintf(sourcefile,"<p style=\"color: green; font-size: 300%; background-color: #ffff42\"> %s </p>\n",APAString.Data());
        APANumber++;
      }
      else if(HistoTitle.Contains(APAString.Data()) && APANumber == 2){
        fprintf(sourcefile,"<hr>\n");
	fprintf(sourcefile,"<p style=\"color: green; font-size: 300%; background-color: #ffff42\"> %s </p>\n",APAString.Data());
        APANumber++;
      }
      else if(HistoTitle.Contains(APAString.Data()) && APANumber == 3){
        fprintf(sourcefile,"<hr>\n");
	fprintf(sourcefile,"<p style=\"color: green; font-size: 300%; background-color: #ffff42\"> %s </p>\n",APAString.Data());
        APANumber++;
      }
      else if(HistoTitle.Contains(APAString.Data()) && APANumber == 4){
        fprintf(sourcefile,"<hr>\n");
	fprintf(sourcefile,"<p style=\"color: green; font-size: 300%; background-color: #ffff42\"> %s </p>\n",APAString.Data());
        APANumber++;
      }
      else if(HistoTitle.Contains(APAString.Data()) && APANumber == 5){
        fprintf(sourcefile,"<hr>\n");
	fprintf(sourcefile,"<p style=\"color: green; font-size: 300%; background-color: #ffff42\"> %s </p>\n",APAString.Data());
        APANumber++;
      }
      else if(HistoTitle.Contains("Slot") && APANumber == 6){
        fprintf(sourcefile,"<hr>\n");
	fprintf(sourcefile,"<p style=\"color: green; font-size: 300%; background-color: #ffff42\"> Slots of mean and RMS from ADC counts </p>\n");
        APANumber++;
      }
      else if(HistoTitle.Contains("FFT_Fiber") && APANumber == 7){
        fprintf(sourcefile,"<hr>\n");
	fprintf(sourcefile,"<p style=\"color: green; font-size: 300%; background-color: #ffff42\"> FFT Fibers </p>\n");
        APANumber++;
      }
      else if(HistoTitle.Contains("NTicks") && APANumber == 8){
        fprintf(sourcefile,"<hr>\n");
        fprintf(sourcefile,"<p style=\"color: green; font-size: 300%; background-color: #ffff42\"> Other Plots </p>\n");
        APANumber++;
      }

      if(VERBOSE)
	cout << HistoTitle << " - " << APAString << " , " << APANumber << endl;
      */
      //fprintf(sourcefile,"<a href=%s><img src=%s width=350></a>\n",outfilename2.Data(), outfilename2.Data());
      fprintf(sourcefile,"<a href=%s><img src=%s width=350></a>\n", figname.Data(), figname.Data());
      
      delete h1;
    }
  }

  // Close file
  fclose(sourcefile);

  return vec;
}

// --------------------------------------------------
void PrintSummaryPlots(FILE *file, TObjArray* dir, TString keyname, TString keyname2, TString runname, bool setlogy){
  // --------------------------------------------------

  //TRegexp reg("_");
  for(int i=0; i<dir->GetEntries(); i++){
    TObject *obj = (TObject*)dir->At(i);

    // Object name
    TString objname(obj->GetName());
    objname.ReplaceAll("#","_");
    if(!objname.Contains(keyname.Data()) || !objname.Contains(keyname2.Data())) continue;

    if(obj->IsA()->InheritsFrom(TH1::Class())){
      //objname(reg) = "F";
      //TString outfilename2 = TString(dir->GetName()) + TString("_");
      std::string temp_str(objname.Data());
      temp_str.erase(std::remove(temp_str.begin(), temp_str.end(), '_'), temp_str.end());
      TString HistoNameOrig(temp_str.c_str());

      TString figname = runname + TString("_") + TString(dir->GetName()) + TString("_") + HistoNameOrig;
      //figname.ReplaceAll("#","_");
      figname += ".png";
      //outfilename2 += figname;
      
      fprintf(file,"<a href=%s><img src=%s width=350></a>\n",figname.Data(), figname.Data());
    }
  }

}

// --------------------------------------------------
int PrintListofDeadNoisyChannels(TObjArray* dir, TString histoname, TString outfilename){
  // --------------------------------------------------
  
  TString deadchanFile_str = outfilename + TString(".txt");
  FILE *deadchanFile = fopen(deadchanFile_str.Data(),"w");

  for(int i=0; i<dir->GetEntries(); i++){
    TObject *obj = (TObject*)dir->At(i);

    TString objname(obj->GetName());
    if(!objname.Contains(histoname.Data())) continue;
    if(obj->IsA()->InheritsFrom(TH1::Class())){
      TH1 *h1 = (TH1*)obj;

      for(int j=0; j<=h1->GetNbinsX(); j++){ // here
	if(h1->GetBinContent(j) != 0){
	  fprintf(deadchanFile,"%i\n",(int)(h1->GetXaxis()->GetBinUpEdge(j)));
	}
      }
    }
  }

  // Close file
  fclose(deadchanFile);

  // Have to close and re-open the file?
  FILE *infile = fopen(deadchanFile_str.Data(), "r");

  // Count the number of channels found
  int number_of_lines = 0;
  int ch;
  while (EOF != (ch=getc(deadchanFile)))
    if ('\n' == ch)
      ++number_of_lines;

  if(VERBOSE)
    std::cout << "INFO::Number of lines in text file: " << number_of_lines << endl;

  // Close file
  fclose(infile);

  return number_of_lines;
}

// --------------------------------------------------
void PrintDeadNoisyChannelsJson(TDirectory *dir, TString jsonfilename, TString srun, TString sdate){
  // --------------------------------------------------

  FILE *deadchanJsonFile = fopen(jsonfilename.Data(),"a");
  
  //fprintf(deadchanJsonFile,"[\n");
  //fprintf(deadchanJsonFile,"   {\n");

  fprintf(deadchanJsonFile,"      \"run\": \"%s\",\n", srun.Data());
  fprintf(deadchanJsonFile,"      \"TimeStamp\": \"%s\",\n", sdate.Data());
  fprintf(deadchanJsonFile,"      \"APA\": \"APA0, APA1, APA2, APA3, APA4, APA5\",\n");

  // loop over all keys in this directory
  TString deadchannel_str("");
  TString nois1channel_str("");
  TString nois2channel_str("");

  TIter nextkey(dir->GetListOfKeys() );
  TKey *key, *oldkey=0;
  int histfound = 0;
  while((key = (TKey*)nextkey())){
    // plot only the highest cycle number for each key
    if (oldkey && !strcmp(oldkey->GetName(),key->GetName())) continue;

    // read object from  source file
    TObject *obj = key->ReadObj();

    // Object name
    TString objname(obj->GetName());

    if(objname.Contains("DeadChannelsHisto") && obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1
      TH1 *h1 = (TH1*)obj;
      for(int j=1; j<h1->GetNbinsX(); j++){
	TString tempstr = Form(",%i",(int)h1->GetBinContent(j));
	if(j == 1)
	  tempstr = Form("%i",(int)h1->GetBinContent(j));

	deadchannel_str += tempstr;
      }
    }
    if(objname.Contains("ChannelsHistoFromNSigma") && obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1
      TH1 *h1 = (TH1*)obj;
      for(int j=1; j<h1->GetNbinsX(); j++){
        TString tempstr = Form(",%i",(int)h1->GetBinContent(j));
        if(j == 1)
          tempstr = Form("%i",(int)h1->GetBinContent(j));

        nois1channel_str += tempstr;
      }
    }
    if(objname.Contains("ChannelsHistoFromNCounts") && obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1
      TH1 *h1 = (TH1*)obj;
      for(int j=1; j<h1->GetNbinsX(); j++){
        TString tempstr = Form(",%i",(int)h1->GetBinContent(j));
        if(j == 1)
          tempstr = Form("%i",(int)h1->GetBinContent(j));

        nois2channel_str += tempstr;
      }
    }

  }

  fprintf(deadchanJsonFile,"      \"NDead\": \"%s\",\n",deadchannel_str.Data());
  fprintf(deadchanJsonFile,"      \"NNoisy-1\": \"%s\",\n",nois1channel_str.Data());
  fprintf(deadchanJsonFile,"      \"NNoisy-2\": \"%s\"\n",nois2channel_str.Data());
  fprintf(deadchanJsonFile,"   }\n");
  fprintf(deadchanJsonFile,"]\n");
  
  // Close file
  fclose(deadchanJsonFile);
}

// --------------------------------------------------
void PrintGausHitsJson(TDirectory *dir, TString jsonfilename){
  // --------------------------------------------------

  // Open file
  FILE *deadchanJsonFile = fopen(jsonfilename.Data(),"w");

  fprintf(deadchanJsonFile,"[\n");
  fprintf(deadchanJsonFile,"   {\n");

  // loop over all keys in this directory
  TString nhits_Ustr("");
  TString nhits_Vstr("");
  TString nhits_Zstr("");
  TString hitchargeM_Ustr("");
  TString hitchargeM_Vstr("");
  TString hitchargeM_Zstr("");
  TString hitchargeS_Ustr("");
  TString hitchargeS_Vstr("");
  TString hitchargeS_Zstr("");
  TString hitrmsM_Ustr("");
  TString hitrmsM_Vstr("");
  TString hitrmsM_Zstr("");
  TString hitrmsS_Ustr("");
  TString hitrmsS_Vstr("");
  TString hitrmsS_Zstr("");

  TIter nextkey(dir->GetListOfKeys() );
  TKey *key, *oldkey=0;
  int histfound = 0;
  while((key = (TKey*)nextkey())){
    // plot only the highest cycle number for each key
    if (oldkey && !strcmp(oldkey->GetName(),key->GetName())) continue;

    // read object from  source file
    TObject *obj = key->ReadObj();

    // Object name
    TString objname(obj->GetName());

    if(objname.Contains("NHitsAPA") && obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1
      TH1 *h1 = (TH1*)obj;
      TString tempstr = Form(",%f",(float)h1->GetMean());
      
      if(objname.Contains("_U")){
	nhits_Ustr += tempstr;
      }
      else if(objname.Contains("_V")){
        nhits_Vstr += tempstr;
      }
      else if(objname.Contains("_Z")){
        nhits_Zstr += tempstr;
      }
    }
    if(objname.Contains("HitChargeAPA") && obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1
      TH1 *h1 = (TH1*)obj;
      TString tempstr = Form(",%f",(float)h1->GetMean());
      TString tempstr2 = Form(",%f",(float)h1->GetRMS());
      
      if(objname.Contains("_U")){
        hitchargeM_Ustr += tempstr;
	hitchargeS_Ustr += tempstr2;
      }
      else if(objname.Contains("_V")){
	hitchargeM_Vstr += tempstr;
        hitchargeS_Vstr += tempstr2;
      }
      else if(objname.Contains("_Z")){
	hitchargeM_Zstr += tempstr;
        hitchargeS_Zstr += tempstr2;
      }
    }
    if(objname.Contains("HitRMSAPA") && obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1
      TH1 *h1 = (TH1*)obj;
      TString tempstr = Form(",%f",(float)h1->GetMean());
      TString tempstr2 = Form(",%f",(float)h1->GetRMS());

      if(objname.Contains("_U")){
        hitrmsM_Ustr += tempstr;
        hitrmsS_Ustr += tempstr2;
      }
      else if(objname.Contains("_V")){
        hitrmsM_Vstr += tempstr;
        hitrmsS_Vstr += tempstr2;
      }
      else if(objname.Contains("_Z")){
        hitrmsM_Zstr += tempstr;
        hitrmsS_Zstr += tempstr2;
      }
    }

  }

  fprintf(deadchanJsonFile,"      \"Plane U Mean NHits\": \"%s\",\n",nhits_Ustr.Data());
  fprintf(deadchanJsonFile,"      \"Plane V Mean NHits\": \"%s\",\n",nhits_Vstr.Data());
  fprintf(deadchanJsonFile,"      \"Plane Z Mean NHits\": \"%s\",\n",nhits_Zstr.Data());
  fprintf(deadchanJsonFile,"      \"Plane U Mean of Charge\": \"%s\",\n",hitchargeM_Ustr.Data());
  fprintf(deadchanJsonFile,"      \"Plane V Mean of Charge\": \"%s\",\n",hitchargeM_Vstr.Data());
  fprintf(deadchanJsonFile,"      \"Plane Z Mean of Charge\": \"%s\",\n",hitchargeM_Zstr.Data());
  fprintf(deadchanJsonFile,"      \"Plane U RMS of Charge\": \"%s\",\n",hitchargeS_Ustr.Data());
  fprintf(deadchanJsonFile,"      \"Plane V RMS of Charge\": \"%s\",\n",hitchargeS_Vstr.Data());
  fprintf(deadchanJsonFile,"      \"Plane Z RMS of Charge\": \"%s\",\n",hitchargeS_Zstr.Data());
  fprintf(deadchanJsonFile,"      \"Plane U Mean of Hit RMS\": \"%s\",\n",hitrmsM_Ustr.Data());
  fprintf(deadchanJsonFile,"      \"Plane V Mean of Hit RMS\": \"%s\",\n",hitrmsM_Vstr.Data());
  fprintf(deadchanJsonFile,"      \"Plane Z Mean of Hit RMS\": \"%s\",\n",hitrmsM_Zstr.Data());
  fprintf(deadchanJsonFile,"      \"Plane U RMS of Hit RMS\": \"%s\",\n",hitrmsS_Ustr.Data());
  fprintf(deadchanJsonFile,"      \"Plane V RMS of Hit RMS\": \"%s\",\n",hitrmsS_Vstr.Data());
  fprintf(deadchanJsonFile,"      \"Plane Z RMS of Hit RMS\": \"%s\",\n",hitrmsS_Zstr.Data());

  //fprintf(deadchanJsonFile,"   }\n");
  //fprintf(deadchanJsonFile,"]\n");

  // Close file
  fclose(deadchanJsonFile);

}

void IncludeOverflow(TH1 *h){
  //add overflow to bin=nbin
  int nentries = h->GetEntries();
  int nbin = h->GetNbinsX();
  double lastbc = h->GetBinContent(nbin);
  double lastberr = h->GetBinError(nbin);
  double overflow =  h->GetBinContent(nbin+1);
  double overflowerr =  h->GetBinError(nbin+1);
  //double err =  TMath::Sqrt(lastberr*lastberr+overflowerr*overflowerr);
  //cout << lastbc << " , " << overflow << " , " << endl;
  h->SetBinContent(nbin,overflow+lastbc);
  //h->SetBinError(nbin,err);
  // Restore number of entries
  h->SetEntries(nentries);
}
