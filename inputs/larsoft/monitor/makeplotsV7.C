// makeplotsV7.C
// to execute non-interactively:  root -b -l -q 'makeplotsV7.C("rawtpcmonitor.root");'
// root -b -l -q 'makeplotsV7.C("rawtpcmonitor.root");' > /dev/null 2>&1

#include <string.h>
#include <stdio.h>
#include <time.h>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <ctime>

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
#include "TPaletteAxis.h"

TCanvas *c1;

// These are per APA
int exp_deadch[6] = {0,0,0,0,0,0};
int exp_noisych1[6] = {0,0,0,0,0,0};
int exp_noisych2[6] = {0,0,0,0,0,0};

TString apaname[6] = {"APA1: DS-RaS", "APA2: MS-RaS", "APA3: US-RaS", "APA4: DS-DaS", "APA5: US-DaS", "APA6: MS-DaS"};

// Global switches
bool VERBOSE = false;
// This will save txt files with the channel ids of the dead/noisy channels
bool SAVELISTOFDEADNOISYCHANNELS = true;

// Helper functions
void FindRunAndTime(TDirectory *dir, ULong64_t& TimeStamp, TString& runid, TString& currentdate);
std::vector<TString> FindDirectories(TDirectory *dir);
TObjArray* SaveHistosFromDirectory(TDirectory *dir, TString runname, TString datename, std::vector<TString>& imagesvec);
void PrintListofDeadNoisyChannels(TObjArray* dir, TString histoname, TString outfilename);
void PrintDeadNoisyChannelsJson(TDirectory *dir, TString jsonfilename, TString srun, TString sdate);
void PrintGausHitsJson(TDirectory *dir, TString jsonfilename, TString srun, TString sdate);
void PrintSummaryPlots(FILE *file, TObjArray* dir, TString keyname, TString keyname2, TString runname, bool setlogy);
void IncludeOverflow(TH1 *h);
void SaveImageNameInJson(TString jsonfile, TString dirstr, std::vector<TString> imagevec);
TString FindImagesAndPrint(TString strtolook, TString strtolook2, TString dirstr, std::vector<TString> imagevec);
void PlotDistToMean(TH1 *h,Int_t mean);
void DrawEventDisplays(TDirectory *dir, TString jsonfile, bool drawbeamline=true);

// For CRT plots
void MakeCRTPlots(TDirectory *dir, TString jsonfile); // modify this one
void PrintCRTSummary(TDirectory *dir, TString jsonfilename, TString srun, TString sdate); // don't change this one

void makeplotsV7(TString infile="rawtpcmonitor.root"){ // np04_mon_run001113_3_dl1.root

  // Start timing
  TStopwatch *mn_t = new TStopwatch;
  mn_t->Start();

  // Silence output
  if(!VERBOSE)
    gErrorIgnoreLevel = kWarning;

  // 2D color palette
  gStyle->SetPalette(kBird);

  // Open file
  TFile *f = new TFile(infile,"READ");

  // List name pf directories in file
  TDirectory *current_sourcedir = gDirectory;
  std::vector<TString> directories_in_file = FindDirectories(current_sourcedir);
  
  // Find run/subrun ID and time this run started
  TString runstr("run0000_000"); TString datestr("00/00/00"); ULong64_t sTimeStamp = 999;
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

  // Define canvas
  c1 = new TCanvas("c1","c1",800,800);

  TString subdirname = runstr + TString("_tpcmonitor") + TString("_summary.json");
  FILE *summaryJsonFile = fopen(subdirname.Data(),"w");

  fprintf(summaryJsonFile,"[\n");
  fprintf(summaryJsonFile,"   {\n");
  fclose(summaryJsonFile);

  // Create summary json file
  for(int i=0; i < directories_in_file.size(); i++){
    TString dirstr = directories_in_file.at(i);
    
    if(dirstr.Contains("pdspnearlineheader") || dirstr.Contains("tjcosmic") || dirstr.Contains("gaushit") || dirstr.Contains("reco3d") || dirstr.Contains("lifetime") || dirstr.Contains("sps")) continue;

    current_sourcedir->cd(dirstr.Data());
    TDirectory *subdir = gDirectory;
    //TString subdirname = runstr + TString("_") + dirstr + TString("_summary.json");
    // Special for different modules
    if(dirstr.Contains("tpcmonitor")){
      PrintDeadNoisyChannelsJson(subdir, subdirname, runstr, datestr);
    }
    else if(dirstr.Contains("pdsphitmonitor")){
      PrintGausHitsJson(subdir, subdirname, runstr, datestr);
    }
    else if(dirstr.Contains("sspmonitor")){
      //
    }
    else if(dirstr.Contains("CRTOnlineMonitor")){
      subdirname = dirstr + TString("_summary.json");
      PrintCRTSummary(subdir, subdirname, runstr, datestr);
    }

    current_sourcedir->cd("..");
    
  }

  FILE *summaryJsonFile2 = fopen(subdirname.Data(),"a");
  fprintf(summaryJsonFile2,"      \"run\": \"%s\",\n", runstr.Data());
  fprintf(summaryJsonFile2,"      \"TimeStamp\": \"%s\",\n", datestr.Data());
  fprintf(summaryJsonFile2,"      \"Type\": \"monitor\",\n");
  fprintf(summaryJsonFile2,"      \"APA\": \"1, 2, 3, 4, 5, 6\"\n");
  fprintf(summaryJsonFile2,"   }\n");
  fprintf(summaryJsonFile2,"]\n");
  fclose(summaryJsonFile2);

  // ---------------------------------------------------------------------------
  for(int i=0; i < directories_in_file.size(); i++){
    TString dirstr = directories_in_file.at(i);

    // Skip these directories for now
    if(dirstr.Contains("pdspnearlineheader") || dirstr.Contains("tjcosmic") || dirstr.Contains("gaushit") || dirstr.Contains("reco3d") || dirstr.Contains("lifetime") ) continue;

    current_sourcedir->cd(dirstr.Data());
    TDirectory *subdir = gDirectory;

    if(dirstr.Contains("sps")){
      //std::cout << "INFO::Attempting to plot from " << dirstr.Data() << std::endl;
      TString jsonfile = runstr + TString("_") + TString(subdir->GetName()) + TString("_FileList.json");
      DrawEventDisplays(subdir, jsonfile);
      // Nothing else to do here
      continue;
    }
    if(dirstr.Contains("CRTOnlineMonitor")){
      //std::cout << "INFO::Attempting to plot from " << dirstr.Data() << std::endl;
      TString jsonfile = TString(subdir->GetName()) + TString("_FileList.json");
      MakeCRTPlots(subdir, jsonfile);
      // Nothing else to do here
      continue;
    }

    // Save all histograms
    std::vector<TString> imagenamevec;
    TObjArray* vec = SaveHistosFromDirectory(subdir, runstr, datestr, imagenamevec);
    vec->SetName(subdir->GetName()); // important

    // Create json file containing the list of histograms
    TString jsonfile = runstr + TString("_") + TString(subdir->GetName()) + TString("_FileList.json");
    FILE *jfile = fopen(jsonfile.Data(),"w");
    fprintf(jfile,"[\n");
    fclose(jfile);
    SaveImageNameInJson(jsonfile, dirstr, imagenamevec);

    // Make sumamry plot for tpcmonitor - this should probably move to its own class
    if(dirstr.Contains("tpcmonitor")){
      //std::cout << "INFO::Attempting to plot from " << dirstr.Data() << std::endl;
      if(SAVELISTOFDEADNOISYCHANNELS){
	PrintListofDeadNoisyChannels(vec, "fNDeadChannelsList",             "fNDeadChannelsList");
	PrintListofDeadNoisyChannels(vec, "fNNoisyChannelsListFromNSigma",  "fNNoisyChannelsListFromNSigma");
	PrintListofDeadNoisyChannels(vec, "fNNoisyChannelsListFromNCounts", "fNNoisyChannelsListFromNCounts");
      }
    }
    else if(dirstr.Contains("sspmonitor")){
      //std::cout << "INFO::Attempting to plot from " << dirstr.Data() << std::endl;
    }
    
    delete vec;

    FILE *jcfile = fopen(jsonfile.Data(),"a");
    fprintf(jcfile,"]\n");
    fclose(jcfile);

    current_sourcedir->cd("..");
    
  }
  // ---------------------------------------------------------------------------
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
  std::string cdate;
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
	  //currentdate = TString(asctime(gmtime(&epoch)));
	  if(fTimeStamp < 9999999999) // dummy protection
	    cdate = asctime(gmtime(&epoch));
	  else
	    cdate = "00/00/00 ";
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
      
      std::string st = cdate.substr(0, cdate.size()-1);
      currentdate = TString(st.c_str());
      //std::cout << "Current date " << currentdate << std::endl;
      //std::cout << "Run " << runfirst << " , subrun = " << subrunfirst << std::endl;
      if(runfirst != runlast){ // Multiple runs: ignore subruns
	runid.Form("run%i-%i_XXX",runfirst,runlast);
      }
      else{ // one run: find subrun(s)
	if(subrunfirst != subrunlast){
	  runid.Form("run%i_%i-%i",runfirst,subrunfirst,subrunlast);
	}
	else{ // add six digits for run-subrun, probably not the most best way...
	  if(runfirst >= 100000){
	    if(subrunfirst >= 1000)
	      runid.Form("run%i_%i",runfirst,subrunfirst);
	    else if(subrunfirst >= 100)
	      runid.Form("run%i_0%i",runfirst,subrunfirst);
	    else if(subrunfirst >= 10)
	      runid.Form("run%i_00%i",runfirst,subrunfirst);
	    else if(subrunfirst >= 0)
	      runid.Form("run%i_000%i",runfirst,subrunfirst);
	  }
	  else if(runfirst >= 10000){
	    if(subrunfirst >= 1000)
	      runid.Form("run0%i_%i",runfirst,subrunfirst);
            else if(subrunfirst >= 100)
              runid.Form("run0%i_0%i",runfirst,subrunfirst);
            else if(subrunfirst >= 10)
              runid.Form("run0%i_00%i",runfirst,subrunfirst);
            else if(subrunfirst >= 0)
              runid.Form("run0%i_000%i",runfirst,subrunfirst);
          }
	  else if(runfirst >= 1000){
	    if(subrunfirst >= 1000)
	      runid.Form("run00%i_%i",runfirst,subrunfirst);
            else if(subrunfirst >= 100)
              runid.Form("run00%i_0%i",runfirst,subrunfirst);
            else if(subrunfirst >= 10)
              runid.Form("run00%i_00%i",runfirst,subrunfirst);
            else if(subrunfirst >= 0)
              runid.Form("run00%i_000%i",runfirst,subrunfirst);
	  }
	  else if(runfirst >= 100){
	    if(subrunfirst >= 1000)
	      runid.Form("run000%i_%i",runfirst,subrunfirst);
            else if(subrunfirst >= 100)
              runid.Form("run000%i_0%i",runfirst,subrunfirst);
            else if(subrunfirst >= 10)
              runid.Form("run000%i_00%i",runfirst,subrunfirst);
            else if(subrunfirst >= 0)
              runid.Form("run000%i_000%i",runfirst,subrunfirst);
          }
	  else if(runfirst >= 10){
	    if(subrunfirst >= 1000)
	      runid.Form("run0000%i_%i",runfirst,subrunfirst);
            else if(subrunfirst >= 100)
              runid.Form("run0000%i_0%i",runfirst,subrunfirst);
            else if(subrunfirst >= 10)
              runid.Form("run0000%i_00%i",runfirst,subrunfirst);
            else if(subrunfirst >= 0)
              runid.Form("run0000%i_000%i",runfirst,subrunfirst);
          }
	  else if(runfirst >= 0){
	    if(subrunfirst >= 1000)
	      runid.Form("run00000%i_%i",runfirst,subrunfirst);
            else if(subrunfirst >= 100)
              runid.Form("run00000%i_0%i",runfirst,subrunfirst);
            else if(subrunfirst >= 10)
              runid.Form("run00000%i_00%i",runfirst,subrunfirst);
            else if(subrunfirst >= 0)
              runid.Form("run00000%i_000%i",runfirst,subrunfirst);
          }
	}
      } // one run
    }
  }
  
}

// --------------------------------------------------
TObjArray* SaveHistosFromDirectory(TDirectory *dir, TString runname, TString datename, std::vector<TString>& imagesvec){
  // --------------------------------------------------

  TObjArray* vec = new TObjArray();

  TString dirname(dir->GetName());

  // loop over all keys in this directory
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
    objname.ReplaceAll("#","");
    objname.ReplaceAll("_","");

    if(obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1 -> make a plot
      TH1 *h = (TH1*)obj;
  
      // Make sure that the order of view and APA is always the same  
      if(dirname.Contains("pdsphitmonitor")){
	objname.ReplaceAll("0U","U0");
	objname.ReplaceAll("0V","V0");
	objname.ReplaceAll("0Z","Z0");
	objname.ReplaceAll("1U","U1");
	objname.ReplaceAll("1V","V1");
	objname.ReplaceAll("1Z","Z1");
	objname.ReplaceAll("2U","U2");
	objname.ReplaceAll("2V","V2");
	objname.ReplaceAll("2Z","Z2");
	objname.ReplaceAll("3U","U3");
	objname.ReplaceAll("3V","V3");
	objname.ReplaceAll("3Z","Z3");
	objname.ReplaceAll("4U","U4");
	objname.ReplaceAll("4V","V4");
	objname.ReplaceAll("4Z","Z4");
	objname.ReplaceAll("5U","U5");
	objname.ReplaceAll("5V","V5");
	objname.ReplaceAll("5Z","Z5");
	objname.ReplaceAll("6U","U6");
	objname.ReplaceAll("6V","V6");
	objname.ReplaceAll("6Z","Z6");
      }
      
      //TString HistoTitle = runname + TString(":") + TString(h->GetTitle());
      TString HistoName = runname + TString("_") + TString(dir->GetName()) + TString("_") + objname;

      TString HistoTitle(h->GetTitle());
      HistoTitle.ReplaceAll("APA1","APA1:DS-RaS");
      HistoTitle.ReplaceAll("APA2","APA2:MS-RaS");
      HistoTitle.ReplaceAll("APA3","APA3:US-RaS");
      HistoTitle.ReplaceAll("APA4","APA4:DS-DaS");
      HistoTitle.ReplaceAll("APA5","APA5:US-DaS");
      HistoTitle.ReplaceAll("APA6","APA6:MS-DaS");
      HistoTitle.ReplaceAll("distribution"," ");

      TH1 *h1 = (TH1*)h->Clone("hnew");
      h1->SetDirectory(0);
      //h1->SetTitle(h->GetTitle());
      h1->SetTitle(HistoTitle.Data());
      h1->SetName(HistoName.Data());

      h1->GetXaxis()->SetTitle(h->GetXaxis()->GetTitle());
      h1->GetYaxis()->SetTitle(h->GetYaxis()->GetTitle());
      h1->GetYaxis()->SetTitleOffset(1.4);

      if(dirname.Contains("tpcmonitor")){
	if(HistoName.Contains("fAllChan") || HistoName.Contains("fBitValue")){
	  Double_t stops[9] = { 0.0000, 1./255., 1./6., 1./3., 1./2., 2./3., 5./6., 254./255., 1.0000};
	  Double_t red[9]   = {  0./255.,   5./255.,  15./255.,  35./255., 102./255., 196./255., 208./255., 199./255., 110./255.};
	  Double_t green[9] = {  0./255.,  48./255., 124./255., 192./255., 206./255., 226./255.,  97./255.,  16./255.,   0./255.};
	  Double_t blue[9]  = { 99./255., 142./255., 198./255., 201./255.,  90./255.,  22./255.,  13./255.,   8./255.,   2./255.};
	  TColor::CreateGradientColorTable(9, stops, red, green, blue, 255);
	  h1->GetXaxis()->SetLabelSize(0.0);
	  h1->GetYaxis()->SetLabelSize(0.04);
	  h1->GetZaxis()->SetLabelSize(0.025);
	  h1->GetXaxis()->SetTickLength(0.0);
	  h1->GetYaxis()->SetTickLength(0.0);
	  h1->GetZaxis()->SetTitleOffset(1.1);
	  h1->GetXaxis()->SetTitle(" ");
	  c1->SetPad(0.0001,0.0001,0.99,0.99);
	}
      }

      if(h1->GetNbinsY()==1){
        if(obj->IsA()->InheritsFrom(TProfile::Class())){
	  h1->SetStats(false);
	  h1->Draw("e0");
	}
	else{
	  h1->SetStats(true);
	  if(HistoName.Contains("NDeadChannelsHisto") || HistoName.Contains("NNoisyChannels"))
	    h1->SetStats(false);
	  h1->Draw("hist");
	  IncludeOverflow(h1);
	}
      }
      else{
        h1->SetStats(false);
        h1->Draw("colz");
	if(obj->IsA()->InheritsFrom(TProfile2D::Class())){
	  TText *apa3 = new TText(20,-4,apaname[2].Data());
	  TText *apa2 = new TText(100,-4,apaname[1].Data());
	  TText *apa1 = new TText(180,-4,apaname[0].Data());
	  TText *apa5 = new TText(20,64,apaname[4].Data());
	  TText *apa6 = new TText(100,64,apaname[5].Data());
	  TText *apa4 = new TText(180,64,apaname[3].Data());
	  apa3->SetTextSize(0.025);
	  apa2->SetTextSize(0.025);
	  apa1->SetTextSize(0.025);
	  apa5->SetTextSize(0.025);
	  apa6->SetTextSize(0.025);
	  apa4->SetTextSize(0.025);

	  apa1->Draw("SAME");
	  apa2->Draw("SAME");
	  apa3->Draw("SAME");
	  apa4->Draw("SAME");
	  apa5->Draw("SAME");
	  apa6->Draw("SAME");

	  TLine *line1 = new TLine(79.5,-0.5,79.5,63.5);
	  TLine *line2 = new TLine(159.5,-0.5,159.5,63.5);
	  TLine *line3 = new TLine(-0.5,31.5,239.5,31.5);
	  line1->Draw("SAME");
	  line2->Draw("SAME");
	  line3->Draw("SAME");

	  TLine *line4 = new TLine(-0.5,9.5,239.5,9.5); line4->SetLineStyle(2);
	  TLine *line5 = new TLine(-0.5,19.5,239.5,19.5); line5->SetLineStyle(2);
	  TLine *line6 = new TLine(-0.5,41.5,239.5,41.5); line6->SetLineStyle(2);
	  TLine *line7 = new TLine(-0.5,51.5,239.5,51.5); line7->SetLineStyle(2);
	  line4->Draw("SAME");
	  line5->Draw("SAME");
	  line6->Draw("SAME");
	  line7->Draw("SAME");

	  TLine *l[3][19];
	  for(int i=0; i<19; i++){
	    for(int j=0; j<3; j++){
	      float x1 =(3.5 + 4*i + 80*j);
	      l[j][i] = new TLine(x1,-0.5,x1,63.5);
	      l[j][i]->SetLineStyle(3);
	      l[j][i]->Draw("SAME");
	    }
	  }

	  c1->Update();
	  TPaletteAxis *palette = (TPaletteAxis*)h1->GetListOfFunctions()->FindObject("palette");
	  if(palette)
	    palette->SetX2NDC(0.92);
	  c1->Modified();
	}
      }

      // Rename bin label for dead/noisy channels
      if(HistoName.Contains("NDeadChannelsHisto") || HistoName.Contains("NNoisyChannelsHistoFromNCounts") || HistoName.Contains("NNoisyChannelsHistoFromNSigma")){
	for(int j=1; j<7; j++){
	  h1->GetXaxis()->SetBinLabel(j+1, apaname[j-1].Data());
	}
      }

      // Add horizontal line for expected number of dead channels
      if(HistoName.Contains("NDeadChannelsHisto")){
	for(int i=1;i<7;i++){
	  TLine *line = new TLine(h1->GetXaxis()->GetBinLowEdge(i+1),exp_deadch[i-1],h1->GetXaxis()->GetBinLowEdge(i+1)+h1->GetXaxis()->GetBinWidth(i+1),exp_deadch[i-1]);
          line->SetLineColor(kRed);
          line->SetLineWidth(2);
          line->Draw();
	}
      }
      else if(HistoName.Contains("NNoisyChannelsHistoFromNCounts")){
        for (int i=1;i<7;i++){
          TLine *line = new TLine(h1->GetXaxis()->GetBinLowEdge(i+1), exp_noisych1[i-1],h1->GetXaxis()->GetBinLowEdge(i+1)+h1->GetXaxis()->GetBinWidth(i+1), exp_noisych1[i-1]);
          line->SetLineColor(kRed);
          line->SetLineWidth(2);
          line->Draw();
        }
      }
      else if(HistoName.Contains("NNoisyChannelsHistoFromNSigma")){
        for (int i=1;i<7;i++){
          TLine *line = new TLine(h1->GetXaxis()->GetBinLowEdge(i+1), exp_noisych2[i-1],h1->GetXaxis()->GetBinLowEdge(i+1)+h1->GetXaxis()->GetBinWidth(i+1), exp_noisych2[i-1]);
          line->SetLineColor(kRed);
          line->SetLineWidth(2);
          line->Draw();
        }
      }
      else if(HistoName.Contains("tpcmonitor_fChan") && HistoName.Contains("pfx")){
	//Double_t hmean = h1->GetMean(2); // 2: Mean along y axis
	// Add line for calculated mean
        //TLine *line_mean = new TLine(h1->GetXaxis()->GetXmin(),hmean,h1->GetXaxis()->GetXmax(),hmean);
        //line_mean->SetLineColor(kRed);
        //line_mean->SetLineWidth(2);
        //line_mean->Draw();

	// Add line for expected value for the mean (update this to a real value!)
	//TLine *line_exp = new TLine(h1->GetXaxis()->GetXmin(),exp,h1->GetXaxis()->GetXmax(),exp);
	//line_exp->SetLineColor(kRed);
	//line_exp->SetLineWidth(2);
	//line_exp->SetLineStyle(3);
	//line_exp->Draw();
	
	// Make histogram of distance between point and mean value
	//PlotDistToMean(h1,mean);
      }

      // Add second line of title
      TString datename_new = runname + TString("(taken on ") + datename + TString(")");
      if(HistoName.Contains("fAllChan") || HistoName.Contains("fBitValue")){
	HistoTitle += TString(":") + datename_new;
	h1->SetTitle(HistoTitle.Data());
      }
      else{
	gPad->Update();
	TPaveText * pt = (TPaveText *)gPad->FindObject("title");
	pt->InsertText(datename_new.Data());
	pt->SetX1NDC(0.05);   pt->SetY1NDC(0.9);
	pt->SetX2NDC(0.75);    pt->SetY2NDC(0.99);
	pt->SetTextSize(0.03);
	pt->Draw();
      }
    
      TString figname = h1->GetName(); //key->GetName();
      figname += ".png";

      // Add image name in vector
      imagesvec.push_back(figname);

      c1->SaveAs(figname.Data());
      
      delete h1;
    }
  }

  return vec;

}

// --------------------------------------------------
void PrintSummaryPlots(FILE *file, TObjArray* dir, TString keyname, TString keyname2, TString runname, bool setlogy){
  // --------------------------------------------------

  for(int i=0; i<dir->GetEntries(); i++){
    TObject *obj = (TObject*)dir->At(i);

    // Object name
    TString objname(obj->GetName());
    objname.ReplaceAll("#","");
    objname.ReplaceAll("_","");

    if(!objname.Contains(keyname.Data()) || !objname.Contains(keyname2.Data())) continue;

    if(obj->IsA()->InheritsFrom(TH1::Class())){
      objname.ReplaceAll("0U","U0");
      objname.ReplaceAll("0V","V0");
      objname.ReplaceAll("0Z","Z0");
      objname.ReplaceAll("1U","U1");
      objname.ReplaceAll("1V","V1");
      objname.ReplaceAll("1Z","Z1");
      objname.ReplaceAll("2U","U2");
      objname.ReplaceAll("2V","V2");
      objname.ReplaceAll("2Z","Z2");
      objname.ReplaceAll("3U","U3");
      objname.ReplaceAll("3V","V3");
      objname.ReplaceAll("3Z","Z3");
      objname.ReplaceAll("4U","U4");
      objname.ReplaceAll("4V","V4");
      objname.ReplaceAll("4Z","Z4");
      objname.ReplaceAll("5U","U5");
      objname.ReplaceAll("5V","V5");
      objname.ReplaceAll("5Z","Z5");
      objname.ReplaceAll("6U","U6");
      objname.ReplaceAll("6V","V6");
      objname.ReplaceAll("6Z","Z6");

      TString figname = runname + TString("_") + TString(dir->GetName()) + TString("_") + objname;
      figname += ".png";

      fprintf(file,"<a href=%s><img src=%s width=350></a>\n",figname.Data(), figname.Data());
    }
  }

}

// --------------------------------------------------
void PrintListofDeadNoisyChannels(TObjArray* dir, TString histoname, TString outfilename){
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
  /*
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
  */
}

// --------------------------------------------------
void PrintDeadNoisyChannelsJson(TDirectory *dir, TString jsonfilename, TString srun, TString sdate){
  // --------------------------------------------------

  FILE *deadchanJsonFile = fopen(jsonfilename.Data(),"a"); // "w"
  
  //fprintf(deadchanJsonFile,"[\n");
  //fprintf(deadchanJsonFile,"   {\n");

  //fprintf(deadchanJsonFile,"      \"run\": \"%s\",\n", srun.Data());
  //fprintf(deadchanJsonFile,"      \"TimeStamp\": \"%s\",\n", sdate.Data());
  //fprintf(deadchanJsonFile,"      \"Type\": \"tpcmonitor\",\n");
  //fprintf(deadchanJsonFile,"      \"APA\": \"1, 2, 3, 4, 5, 6\",\n");

  // loop over all keys in this directory
  TString deadchannel_str("");
  TString nois1channel_str("");
  TString nois2channel_str("");

   const Int_t napas = 6;
  Int_t deadchannel_arr[napas] = {0,0,0,0,0,0};
  Int_t nois1channel_arr[napas] = {0,0,0,0,0,0};
  Int_t nois2channel_arr[napas] = {0,0,0,0,0,0};

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
	TString binlabel(h1->GetXaxis()->GetBinLabel(j));
	if(!binlabel.Contains("APA")) continue;
	if(binlabel.Contains("APA 1"))
	  deadchannel_arr[0] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 2"))
	  deadchannel_arr[1] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 3"))
	  deadchannel_arr[2] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 4"))
	  deadchannel_arr[3] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 5"))
	  deadchannel_arr[4] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 6"))
	  deadchannel_arr[5] = (int)h1->GetBinContent(j);
	else
	  cout << "WARNING::DeadChannelsHisto unknown bin label " << binlabel << endl;
      }
      
      for(Int_t i=0; i<napas; i++){
	TString tempstr = Form(",%i", deadchannel_arr[i]);
	if(i == 0)
	  tempstr = Form("%i",deadchannel_arr[i]);

	// 
	if(deadchannel_arr[i] > 1000){
	  // Nothing to do here
	}
	else if(deadchannel_arr[i] > 100){
	  tempstr = Form(", %i",deadchannel_arr[i]);
	  if(i == 0)
	    tempstr = Form(" %i",deadchannel_arr[i]);
	}
	else if(deadchannel_arr[i] > 10){
	  tempstr = Form(",  %i",deadchannel_arr[i]);
	  if(i == 0)
	    tempstr = Form("  %i",deadchannel_arr[i]);
	}
	else if(deadchannel_arr[i] >= 0){
	  tempstr = Form(",   %i",deadchannel_arr[i]);
	  if(i == 0)
	    tempstr = Form("   %i",deadchannel_arr[i]);
	}
	else{
	  if(VERBOSE)
	    cout << "WARNING::Unknown bin content for histogram " << h1->GetName() << endl;
	}

	deadchannel_str += tempstr;
      }

    }
    if(objname.Contains("ChannelsHistoFromNSigma") && obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1
      TH1 *h1 = (TH1*)obj;
      for(int j=1; j<h1->GetNbinsX(); j++){
	TString binlabel(h1->GetXaxis()->GetBinLabel(j));
	if(!binlabel.Contains("APA")) continue;
	if(binlabel.Contains("APA 1"))
	  nois1channel_arr[0] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 2"))
	  nois1channel_arr[1] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 3"))
	  nois1channel_arr[2] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 4"))
	  nois1channel_arr[3] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 5"))
	  nois1channel_arr[4] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 6"))
	  nois1channel_arr[5] = (int)h1->GetBinContent(j);
	else
	  cout << "WARNING::ChannelsHistoFromNSigma unknown bin label " << binlabel << endl;
      }

      for(Int_t i=0; i<napas; i++){
	TString tempstr = Form(",%i", nois1channel_arr[i]);
	if(i == 0)
	  tempstr = Form("%i",nois1channel_arr[i]);

	// 
	if(nois1channel_arr[i] > 1000){
	  // Nothing to do here
	}
	else if(nois1channel_arr[i] > 100){
	  tempstr = Form(", %i",nois1channel_arr[i]);
	  if(i == 0)
	    tempstr = Form(" %i",nois1channel_arr[i]);
	}
	else if(nois1channel_arr[i] > 10){
	  tempstr = Form(",  %i",nois1channel_arr[i]);
	  if(i == 0)
	    tempstr = Form("  %i",nois1channel_arr[i]);
	}
	else if(nois1channel_arr[i] >= 0){
	  tempstr = Form(",   %i",nois1channel_arr[i]);
	  if(i == 0)
	    tempstr = Form("   %i",nois1channel_arr[i]);
	}
	else{
	  if(VERBOSE)
	    cout << "WARNING::Unknown bin content for histogram " << h1->GetName() << endl;
	}

	nois1channel_str += tempstr;
      }
    }
    if(objname.Contains("ChannelsHistoFromNCounts") && obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1
      TH1 *h1 = (TH1*)obj;
    
      for(int j=1; j<h1->GetNbinsX(); j++){
	TString binlabel(h1->GetXaxis()->GetBinLabel(j));
	if(!binlabel.Contains("APA")) continue;
	if(binlabel.Contains("APA 1"))
	  nois2channel_arr[0] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 2"))
	  nois2channel_arr[1] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 3"))
	  nois2channel_arr[2] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 4"))
	  nois2channel_arr[3] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 5"))
	  nois2channel_arr[4] = (int)h1->GetBinContent(j);
	else if(binlabel.Contains("APA 6"))
	  nois2channel_arr[5] = (int)h1->GetBinContent(j);
	else
	  cout << "WARNING::ChannelsHistoFromNCounts unknown bin label " << binlabel << endl;
      }

      for(Int_t i=0; i<napas; i++){
	TString tempstr = Form(",%i", nois2channel_arr[i]);
	if(i == 0)
	  tempstr = Form("%i",nois2channel_arr[i]);

	// 
	if(nois2channel_arr[i] > 1000){
	  // Nothing to do here
	}
	else if(nois2channel_arr[i] > 100){
	  tempstr = Form(", %i",nois2channel_arr[i]);
	  if(i == 0)
	    tempstr = Form(" %i",nois2channel_arr[i]);
	}
	else if(nois2channel_arr[i] > 10){
	  tempstr = Form(",  %i",nois2channel_arr[i]);
	  if(i == 0)
	    tempstr = Form("  %i",nois2channel_arr[i]);
	}
	else if(nois2channel_arr[i] >= 0){
	  tempstr = Form(",   %i",nois2channel_arr[i]);
	  if(i == 0)
	    tempstr = Form("   %i",nois2channel_arr[i]);
	}
	else{
	  if(VERBOSE)
	    cout << "WARNING::Unknown bin content for histogram " << h1->GetName() << endl;
	}

	nois2channel_str += tempstr;
      }

    }

  }

  fprintf(deadchanJsonFile,"      \"NDead  Channels\": \"%s\",\n",deadchannel_str.Data());
  fprintf(deadchanJsonFile,"      \"NNoisy Channels 6Sigma away from mean value of the ADC RMS\": \"%s\",\n",nois1channel_str.Data());
  fprintf(deadchanJsonFile,"      \"NNoisy Channels Above ADC RMS Threshold\": \"%s\",\n",nois2channel_str.Data());
  //fprintf(deadchanJsonFile,"   }\n");
  //fprintf(deadchanJsonFile,"]\n");
  
  // Close file
  fclose(deadchanJsonFile);
}

// --------------------------------------------------
void PrintGausHitsJson(TDirectory *dir, TString jsonfilename, TString srun, TString sdate){
  // --------------------------------------------------

  // Open file
  FILE *deadchanJsonFile = fopen(jsonfilename.Data(),"a"); // "w"

  //fprintf(deadchanJsonFile,"[\n");
  //fprintf(deadchanJsonFile,"   {\n");

  //fprintf(deadchanJsonFile,"      \"run\": \"%s\",\n", srun.Data());
  //fprintf(deadchanJsonFile,"      \"TimeStamp\": \"%s\",\n", sdate.Data());
  //fprintf(deadchanJsonFile,"      \"Type\": \"hitmonitor\",\n");
  //fprintf(deadchanJsonFile,"      \"APA\": \"1, 2, 3, 4, 5, 6\",\n");

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

 const Int_t napas = 6;
  Float_t nhits_Uarr[napas];
  Float_t nhits_Varr[napas];
  Float_t nhits_Zarr[napas];
  Float_t hitchargeM_Uarr[napas];
  Float_t hitchargeM_Varr[napas];
  Float_t hitchargeM_Zarr[napas];
  Float_t hitchargeS_Uarr[napas];
  Float_t hitchargeS_Varr[napas];
  Float_t hitchargeS_Zarr[napas];
  Float_t hitrmsM_Uarr[napas];
  Float_t hitrmsM_Varr[napas];
  Float_t hitrmsM_Zarr[napas];
  Float_t hitrmsS_Uarr[napas];
  Float_t hitrmsS_Varr[napas];
  Float_t hitrmsS_Zarr[napas];

  // loop over all keys in this directory
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

      if(objname.Contains("APA1_U"))
	nhits_Uarr[0] = h1->GetMean();
      else if(objname.Contains("APA2_U"))
	nhits_Uarr[1] = h1->GetMean();
      else if(objname.Contains("APA3_U"))
	nhits_Uarr[2] = h1->GetMean();
      else if(objname.Contains("APA4_U"))
	nhits_Uarr[3] = h1->GetMean();
      else if(objname.Contains("APA5_U"))
	nhits_Uarr[4] = h1->GetMean();
      else if(objname.Contains("APA6_U"))
	nhits_Uarr[5] = h1->GetMean();
      else if(objname.Contains("APA1_V"))
	nhits_Varr[0] = h1->GetMean();
      else if(objname.Contains("APA2_V"))
	nhits_Varr[1] = h1->GetMean();
      else if(objname.Contains("APA3_V"))
	nhits_Varr[2] = h1->GetMean();
      else if(objname.Contains("APA4_V"))
	nhits_Varr[3] = h1->GetMean();
      else if(objname.Contains("APA5_V"))
	nhits_Varr[4] = h1->GetMean();
      else if(objname.Contains("APA6_V"))
	nhits_Varr[5] = h1->GetMean();
      else if(objname.Contains("APA1_Z"))
	nhits_Zarr[0] = h1->GetMean();
      else if(objname.Contains("APA2_Z"))
	nhits_Zarr[1] = h1->GetMean();
      else if(objname.Contains("APA3_Z"))
	nhits_Zarr[2] = h1->GetMean();
      else if(objname.Contains("APA4_Z"))
	nhits_Zarr[3] = h1->GetMean();
      else if(objname.Contains("APA5_Z"))
	nhits_Zarr[4] = h1->GetMean();
      else if(objname.Contains("APA6_Z"))
	nhits_Zarr[5] = h1->GetMean();
    }
    if(objname.Contains("HitChargeAPA") && obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1
      TH1 *h1 = (TH1*)obj;

      if(objname.Contains("APA1_U")){
	hitchargeM_Uarr[0] = h1->GetMean();
	hitchargeS_Uarr[0] = h1->GetRMS();
      }
      else if(objname.Contains("APA2_U")){
	hitchargeM_Uarr[1] = h1->GetMean();
	hitchargeS_Uarr[1] = h1->GetRMS();
      }
      else if(objname.Contains("APA3_U")){
	hitchargeM_Uarr[2] = h1->GetMean();
	hitchargeS_Uarr[2] = h1->GetRMS();
      }
      else if(objname.Contains("APA4_U")){
	hitchargeM_Uarr[3] = h1->GetMean();
	hitchargeS_Uarr[3] = h1->GetRMS();
      }
      else if(objname.Contains("APA5_U")){
	hitchargeM_Uarr[4] = h1->GetMean();
	hitchargeS_Uarr[4] = h1->GetRMS();
      }
      else if(objname.Contains("APA6_U")){
	hitchargeM_Uarr[5] = h1->GetMean();
	hitchargeS_Uarr[5] = h1->GetRMS();
      }
      else if(objname.Contains("APA1_V")){
	hitchargeM_Varr[0] = h1->GetMean();
	hitchargeS_Varr[0] = h1->GetRMS();
      }
      else if(objname.Contains("APA2_V")){
	hitchargeM_Varr[1] = h1->GetMean();
	hitchargeS_Varr[1] = h1->GetRMS();
      }
      else if(objname.Contains("APA3_V")){
	hitchargeM_Varr[2] = h1->GetMean();
	hitchargeS_Varr[2] = h1->GetRMS();
      }
      else if(objname.Contains("APA4_V")){
	hitchargeM_Varr[3] = h1->GetMean();
	hitchargeS_Varr[3] = h1->GetRMS();
      }
      else if(objname.Contains("APA5_V")){
	hitchargeM_Varr[4] = h1->GetMean();
	hitchargeS_Varr[4] = h1->GetRMS();
      }
      else if(objname.Contains("APA6_V")){
	hitchargeM_Varr[5] = h1->GetMean();
	hitchargeS_Varr[5] = h1->GetRMS();
      }
      else if(objname.Contains("APA1_Z")){
	hitchargeM_Zarr[0] = h1->GetMean();
	hitchargeS_Zarr[0] = h1->GetRMS();
      }
      else if(objname.Contains("APA2_Z")){
	hitchargeM_Zarr[1] = h1->GetMean();
	hitchargeS_Zarr[1] = h1->GetRMS();
      }
      else if(objname.Contains("APA3_Z")){
	hitchargeM_Zarr[2] = h1->GetMean();
	hitchargeS_Zarr[2] = h1->GetRMS();
      }
      else if(objname.Contains("APA4_Z")){
	hitchargeM_Zarr[3] = h1->GetMean();
	hitchargeS_Zarr[3] = h1->GetRMS();
      }
      else if(objname.Contains("APA5_Z")){
	hitchargeM_Zarr[4] = h1->GetMean();
	hitchargeS_Zarr[4] = h1->GetRMS();
      }
      else if(objname.Contains("APA6_Z")){
	hitchargeM_Zarr[5] = h1->GetMean();
	hitchargeS_Zarr[5] = h1->GetRMS();
      }
    }
    if(objname.Contains("HitRMSAPA") && obj->IsA()->InheritsFrom(TH1::Class())){
      // descendant of TH1
      TH1 *h1 = (TH1*)obj;

      if(objname.Contains("APA1_U")){
	hitrmsM_Uarr[0] = h1->GetMean();
	hitrmsS_Uarr[0] = h1->GetRMS();
      }
      else if(objname.Contains("APA2_U")){
	hitrmsM_Uarr[1] = h1->GetMean();
	hitrmsS_Uarr[1] = h1->GetRMS();
      }
      else if(objname.Contains("APA3_U")){
	hitrmsM_Uarr[2] = h1->GetMean();
	hitrmsS_Uarr[2] = h1->GetRMS();
      }
      else if(objname.Contains("APA4_U")){
	hitrmsM_Uarr[3] = h1->GetMean();
	hitrmsS_Uarr[3] = h1->GetRMS();
      }
      else if(objname.Contains("APA5_U")){
	hitrmsM_Uarr[4] = h1->GetMean();
	hitrmsS_Uarr[4] = h1->GetRMS();
      }
      else if(objname.Contains("APA6_U")){
	hitrmsM_Uarr[5] = h1->GetMean();
	hitrmsS_Uarr[5] = h1->GetRMS();
      }
      else if(objname.Contains("APA1_V")){
	hitrmsM_Varr[0] = h1->GetMean();
	hitrmsS_Varr[0] = h1->GetRMS();
      }
      else if(objname.Contains("APA2_V")){
	hitrmsM_Varr[1] = h1->GetMean();
	hitrmsS_Varr[1] = h1->GetRMS();
      }
      else if(objname.Contains("APA3_V")){
	hitrmsM_Varr[2] = h1->GetMean();
	hitrmsS_Varr[2] = h1->GetRMS();
      }
      else if(objname.Contains("APA4_V")){
	hitrmsM_Varr[3] = h1->GetMean();
	hitrmsS_Varr[3] = h1->GetRMS();
      }
      else if(objname.Contains("APA5_V")){
	hitrmsM_Varr[4] = h1->GetMean();
	hitrmsS_Varr[4] = h1->GetRMS();
      }
      else if(objname.Contains("APA6_V")){
	hitrmsM_Varr[5] = h1->GetMean();
	hitrmsS_Varr[5] = h1->GetRMS();
      }
      else if(objname.Contains("APA1_Z")){
	hitrmsM_Zarr[0] = h1->GetMean();
	hitrmsS_Zarr[0] = h1->GetRMS();
      }
      else if(objname.Contains("APA2_Z")){
	hitrmsM_Zarr[1] = h1->GetMean();
	hitrmsS_Zarr[1] = h1->GetRMS();
      }
      else if(objname.Contains("APA3_Z")){
	hitrmsM_Zarr[2] = h1->GetMean();
	hitrmsS_Zarr[2] = h1->GetRMS();
      }
      else if(objname.Contains("APA4_Z")){
	hitrmsM_Zarr[3] = h1->GetMean();
	hitrmsS_Zarr[3] = h1->GetRMS();
      }
      else if(objname.Contains("APA5_Z")){
	hitrmsM_Zarr[4] = h1->GetMean();
	hitrmsS_Zarr[4] = h1->GetRMS();
      }
      else if(objname.Contains("APA6_Z")){
	hitrmsM_Zarr[5] = h1->GetMean();
	hitrmsS_Zarr[5] = h1->GetRMS();
      }
    
    }
  }
  
  for(Int_t i=0; i < napas; i++){
    TString tempstr = Form("%.2f,",(float)nhits_Uarr[i]);
    nhits_Ustr += tempstr;
    tempstr = Form("%.2f,",(float)nhits_Varr[i]);
    nhits_Vstr += tempstr;
    tempstr = Form("%.2f,",(float)nhits_Zarr[i]);
    nhits_Zstr += tempstr;
    
    tempstr = Form("%.2f,",(float)hitchargeM_Uarr[i]);
    hitchargeM_Ustr += tempstr;
    tempstr = Form("%.2f,",(float)hitchargeS_Uarr[i]);
    hitchargeS_Ustr += tempstr;
    tempstr = Form("%.2f,",(float)hitchargeM_Varr[i]);
    hitchargeM_Vstr += tempstr;
    tempstr = Form("%.2f,",(float)hitchargeS_Varr[i]);
    hitchargeS_Vstr += tempstr;
    tempstr = Form("%.2f,",(float)hitchargeM_Zarr[i]);
    hitchargeM_Zstr += tempstr;
    tempstr = Form("%.2f,",(float)hitchargeS_Zarr[i]);
    hitchargeS_Zstr += tempstr;
    
    tempstr = Form("%.2f,",(float)hitrmsM_Uarr[i]);
    hitrmsM_Ustr += tempstr;
    tempstr = Form("%.2f,",(float)hitrmsS_Uarr[i]);
    hitrmsS_Ustr += tempstr;
    tempstr = Form("%.2f,",(float)hitrmsM_Varr[i]);
    hitrmsM_Vstr += tempstr;
    tempstr = Form("%.2f,",(float)hitrmsS_Varr[i]);
    hitrmsS_Vstr += tempstr;
    tempstr = Form("%.2f,",(float)hitrmsM_Zarr[i]);
    hitrmsM_Zstr += tempstr;
    tempstr = Form("%.2f,",(float)hitrmsS_Zarr[i]);
    hitrmsS_Zstr += tempstr;
  }

  // Remove last comma
  nhits_Ustr.Remove(nhits_Ustr.Length()-1);
  nhits_Vstr.Remove(nhits_Vstr.Length()-1);
  nhits_Zstr.Remove(nhits_Zstr.Length()-1);
  hitchargeM_Ustr.Remove(hitchargeM_Ustr.Length()-1);
  hitchargeM_Vstr.Remove(hitchargeM_Vstr.Length()-1);
  hitchargeM_Zstr.Remove(hitchargeM_Zstr.Length()-1);
  hitchargeS_Ustr.Remove(hitchargeS_Ustr.Length()-1);
  hitchargeS_Vstr.Remove(hitchargeS_Vstr.Length()-1);
  hitchargeS_Zstr.Remove(hitchargeS_Zstr.Length()-1);
  hitrmsM_Ustr.Remove(hitrmsM_Ustr.Length()-1);
  hitrmsM_Vstr.Remove(hitrmsM_Vstr.Length()-1);
  hitrmsM_Zstr.Remove(hitrmsM_Zstr.Length()-1);
  hitrmsS_Ustr.Remove(hitrmsS_Ustr.Length()-1);
  hitrmsS_Vstr.Remove(hitrmsS_Vstr.Length()-1);
  hitrmsS_Zstr.Remove(hitrmsS_Zstr.Length()-1);

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

// --------------------------------------------------
void SaveImageNameInJson(TString jsonfile, TString dirstr, std::vector<TString> imagevec){
  // --------------------------------------------------
  
  // Open file
  FILE *JsonFile = fopen(jsonfile.Data(),"a");

  if(dirstr.Contains("timingrawdecoder")){
    TString category("Timing Raw Decoder");
    fprintf(JsonFile,"   {\n");
    fprintf(JsonFile,"     \"Category\":\"%s\",\n",category.Data());
    fprintf(JsonFile,"     \"Files\": {\n");

    fprintf(JsonFile,"       \"Timing Raw Decoder Plots\":\"");
    TString filesstr = FindImagesAndPrint(dirstr, dirstr, dirstr, imagevec);
    fprintf(JsonFile,"%s\"\n",filesstr.Data());
    fprintf(JsonFile,"      }\n");

    fprintf(JsonFile,"   }\n");
  }
  else if(dirstr.Contains("ssprawdecoder")){
    TString category("SSP Raw Decoder");
    fprintf(JsonFile,"   {\n");
    fprintf(JsonFile,"     \"Category\":\"%s\",\n",category.Data());
    fprintf(JsonFile,"     \"Files\": {\n");

    fprintf(JsonFile,"       \"SSP Raw Decoder Plots\":\"");
    TString filesstr = FindImagesAndPrint(dirstr, dirstr, dirstr, imagevec);
    fprintf(JsonFile,"%s\"\n",filesstr.Data());
    fprintf(JsonFile,"      }\n");

    fprintf(JsonFile,"   }\n");
  }
  else if(dirstr.Contains("sspmonitor")){
    TString category("SSP Monitor");
    fprintf(JsonFile,"   {\n");
    fprintf(JsonFile,"     \"Category\":\"%s\",\n",category.Data());
    fprintf(JsonFile,"     \"Files\": {\n");

    TString strtolook("sspadcvalues");
    TString strtolook2("ssphittimes");
    fprintf(JsonFile,"       \"ADC values\":\"");
    TString filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    fprintf(JsonFile,"       \"Hit times\":\"");
    filesstr = FindImagesAndPrint(strtolook2, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "peaks";
    fprintf(JsonFile,"       \"Peak Amplitude\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());
    
    strtolook = "areas";
    fprintf(JsonFile,"       \"Peak Area\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "persistent";
    strtolook2 = "waveform";
    fprintf(JsonFile,"       \"Persistent Waveform\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "fft";
    strtolook2 = "channel";
    fprintf(JsonFile,"       \"FFT Channel\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "evt";
    strtolook2 = "channel";
    fprintf(JsonFile,"       \"Waveform for Channel\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s\"\n",filesstr.Data());
    fprintf(JsonFile,"      }\n");

    fprintf(JsonFile,"   }\n");
  }
  else if(dirstr.Contains("pdsphitmonitor")){ // Hit Monitor
    TString category("Hit Monitor");
    fprintf(JsonFile,"   {\n");
    fprintf(JsonFile,"     \"Category\":\"%s\",\n",category.Data());
    fprintf(JsonFile,"     \"Files\": {\n");
    
    TString strtolook("NHitsAPA");
    fprintf(JsonFile,"       \"Number of hits per APA per view\":\"");
    TString filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());
      
    strtolook = "HitChargeAPA";
    fprintf(JsonFile,"       \"Hit Charge distribution per APA per view\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());
      
    strtolook = "HitRMSAPA";
    fprintf(JsonFile,"       \"Hit RMS distribution per APA per view\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());
      
    strtolook = "HitPeakTimeAPA";
    fprintf(JsonFile,"       \"Hit peak time distribution per APA per view\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());
      
    strtolook = "fNHitsView";
    fprintf(JsonFile,"       \"Profiled number of hits\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());
      
    strtolook = "fChargeView";
    fprintf(JsonFile,"       \"Profiled hit charge\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());
      
    strtolook = "fRMSView";
    fprintf(JsonFile,"       \"Profiled hit RMS\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\"\n",filesstr.Data());
    fprintf(JsonFile,"      }\n"); 
    
    fprintf(JsonFile,"   }\n");
  }
  else if(dirstr.Contains("tpcmonitor")){ // TPC monitor
    TString category("TPC Monitor");
    fprintf(JsonFile,"   {\n");
    fprintf(JsonFile,"     \"Category\":\"%s\",\n",category.Data());
    fprintf(JsonFile,"     \"Files\": {\n");
  
    TString strtolook("fChanRMSDist");
    fprintf(JsonFile,"       \"RMS of ADC per view per APA for all channels\":\"");
    TString filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "fChanMeanDist";
    fprintf(JsonFile,"       \"Mean of ADC per view per APA for all channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "fChanRMS";
    TString strtolook2("pfx");
    fprintf(JsonFile,"       \"RMS of ADC per view per APA and per channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "fChanMean";
    fprintf(JsonFile,"       \"Mean of ADC per view per APA and per channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "fAllChan";
    fprintf(JsonFile,"       \"Mean and RMS of ADC for all channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "Slot";
    strtolook2 = "RMSpfx";
    fprintf(JsonFile,"       \"RMS of channel ADC from slot\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "Slot";
    strtolook2 = "Meanpfx";
    fprintf(JsonFile,"       \"Mean of channel ADC from slot\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "fChanStuckCodeOnFrac";
    fprintf(JsonFile,"       \"Channel stuck code on\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "fChanStuckCodeOffFrac";
    fprintf(JsonFile,"       \"Channel stuck code off\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "fChanFFT";
    fprintf(JsonFile,"       \"FFT\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "PersistentFFTFiber";
    fprintf(JsonFile,"       \"Persistent FFT Fiber\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    //fprintf(JsonFile,"%s",filesstr.Data());
    fputs(filesstr.Data(),JsonFile); // long string, fprintf has a limitiation on the number of chars
    fprintf(JsonFile,"\",\n");

    strtolook = "ProfiledFFTFiber";
    fprintf(JsonFile,"       \"Profiled FFT Fiber\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    //fprintf(JsonFile,"%s",filesstr.Data());
    fputs(filesstr.Data(),JsonFile);  // long string, fprintf has a limitiation on the number of chars
    fprintf(JsonFile,"\",\n");

    strtolook = "fNDeadChannels";
    fprintf(JsonFile,"       \"Number of dead channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "fNNoisyChannels";
    fprintf(JsonFile,"       \"Number of noisy channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "fBitValue";
    fprintf(JsonFile,"       \"Bit values\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\",\n",filesstr.Data());

    strtolook = "NTicks";
    fprintf(JsonFile,"       \"Number of Ticks in TPC channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s\"\n",filesstr.Data());
    fprintf(JsonFile,"      }\n");

    fprintf(JsonFile,"   }\n");
  }

  // Close file
  fclose(JsonFile);

}

// --------------------------------------------------
TString FindImagesAndPrint(TString strtolook, TString strtolook2, TString dirstr, std::vector<TString> imagevec){
  // --------------------------------------------------

  TString filesstr("");
  for(UInt_t i=0; i < imagevec.size(); i++){
    TString name = imagevec[i];
    if(!name.Contains(dirstr.Data())) continue;
    if(!name.Contains(strtolook.Data())) continue;
    if(!name.Contains(strtolook2.Data())) continue;

    filesstr = filesstr + name + TString(",");
  }
  
  // Remove last comma
  filesstr.Remove(filesstr.Length()-1);

  return filesstr;

}

// --------------------------------------------------
void PlotDistToMean(TH1 *h,Int_t mean){
  // --------------------------------------------------

  TString figname = h->GetName();
  figname += "_DistToMean.png";

  TCanvas *c2 = new TCanvas("c2","c2",800,800);
  TH1F *histo;
  if (figname.Contains("RMS")){
    histo = new TH1F("dist_to_mean","Distance to Mean;Distance;#",50,-3,3);
  } else {
    histo = new TH1F("dist_to_mean","Distance to Mean;Distance;#",50,-150,150);
  }

  for (int i=1;i<=h->GetNbinsX();i++){
    if (h->GetBinContent(i) != 0){
      histo->Fill(h->GetBinContent(i)-mean);
    }
  }

  histo->Draw();

  c2->SaveAs(figname.Data());

  delete histo;
  delete c2;

}

// --------------------------------------------------
void IncludeOverflow(TH1 *h){
  // --------------------------------------------------

  //add overflow to bin=nbin
  int nentries = h->GetEntries();
  int nbin = h->GetNbinsX();
  double lastbc = h->GetBinContent(nbin);
  double lastberr = h->GetBinError(nbin);
  double overflow =  h->GetBinContent(nbin+1);
  double overflowerr =  h->GetBinError(nbin+1);
  //double err =  TMath::Sqrt(lastberr*lastberr+overflowerr*overflowerr);
  h->SetBinContent(nbin,overflow+lastbc);
  //h->SetBinError(nbin,err);
  // Restore number of entries
  h->SetEntries(nentries);

}

// --------------------------------------------------
void DrawEventDisplays(TDirectory *dir, TString jsonfile, bool drawbeamline){
  // --------------------------------------------------

  std::vector<TString> vec;
  std::vector<TString> beamvec;

  // Define beam lines - this is approximate
  //TPolyLine3D *polyline = new TPolyLine3D(2);
  //polyline->SetPoint(0, 24.07, 475.0, -175.0);
  //polyline->SetPoint(1, -25.0, 424.5, -22.22);

  TLine *yzline = new TLine(-175.0, 475.0, 0.0, 417.5);
  yzline->SetLineColor(kRed);
  yzline->SetLineWidth(2.0);

  TLine *xzline = new TLine(-175.0, 24.07, 0.0, -29.0);
  xzline->SetLineColor(kRed);
  xzline->SetLineWidth(2.0);

  TLine *xyline = new TLine(24.07,  475.0, -29.0, 417.5);
  xyline->SetLineColor(kRed);
  xyline->SetLineWidth(2.0);

  // loop over all keys in this directory
  TIter nextkey(dir->GetListOfKeys());
  TKey *fkey, *foldkey=0;
  std::string cdate;
  while((fkey = (TKey*)nextkey())){
    //plot only the highest cycle number for each key
    if (foldkey && !strcmp(foldkey->GetName(),fkey->GetName())) continue;

    // read object from  source file
    TObject *obj = fkey->ReadObj();

    // Object name
    TString objname(obj->GetName());

    if(obj->IsA()->InheritsFrom(TTree::Class()) ){
      if(!objname.Contains("spt")) continue;

      Int_t run, subrun, event; Double_t evttime;
      std::vector<double> *vx = 0;
      std::vector<double> *vy = 0;
      std::vector<double> *vz = 0;
      std::vector<double> *vcharge = 0;
      TTree *spttree = (TTree*)obj;
      spttree->SetBranchAddress("run",      &run);
      spttree->SetBranchAddress("subrun",   &subrun);
      spttree->SetBranchAddress("event",    &event);
      spttree->SetBranchAddress("evttime",  &evttime);
      spttree->SetBranchAddress("vx",       &vx);
      spttree->SetBranchAddress("vy",       &vy);
      spttree->SetBranchAddress("vz",       &vz);
      spttree->SetBranchAddress("vcharge",  &vcharge);

      for(Int_t i = 0; i < spttree->GetEntries(); i++){
	spttree->GetEntry(i);

	TString runstr;
	if(run >= 100000){
	  if(subrun >= 100)
	    runstr = Form("run%i_%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 10)
	    runstr = Form("run%i_0%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 0)
	    runstr = Form("run%i_00%i_sps_event%i",run,subrun,event);
	}
	else if(run >= 10000){
	  if(subrun >= 100)
	    runstr = Form("run0%i_%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 10)
	    runstr = Form("run0%i_0%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 0)
	    runstr = Form("run0%i_00%i_sps_event%i",run,subrun,event);
	}
	else if(run >= 1000){
	  if(subrun >= 100)
	    runstr = Form("run00%i_%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 10)
	    runstr = Form("run00%i_0%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 0)
	    runstr = Form("run00%i_00%i_sps_event%i",run,subrun,event);
	}
	else if(run >= 100){
	  if(subrun >= 100)
	    runstr = Form("run000%i_%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 10)
	    runstr = Form("run000%i_0%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 0)
	    runstr = Form("run000%i_00%i_sps_event%i",run,subrun,event);
	}
	else if(run >= 10){
	  if(subrun >= 100)
	    runstr = Form("run0000%i_%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 10)
	    runstr = Form("run0000%i_0%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 0)
	    runstr = Form("run0000%i_00%i_sps_event%i",run,subrun,event);
	}
	else if(run >= 0){
	  if(subrun >= 100)
	    runstr = Form("run00000%i_%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 10)
	    runstr = Form("run00000%i_0%i_sps_event%i",run,subrun,event);
	  else if(subrun >= 0)
	    runstr = Form("run00000%i_00%i_sps_event%i",run,subrun,event);
	}

	TString imagestrxy = runstr + TString("XYEventDisplay.png");
	TString imagestrxz = runstr + TString("XZEventDisplay.png");
	TString imagestryz = runstr + TString("YZEventDisplay.png");

	TH2D* YZHisto = new TH2D(Form("ZYrun%i-%ievent%i",run,subrun,event),Form("Z-Y display for run %i-%i and event %i",run,subrun,event), 180, 0, 720, 152, 0, 608);
	TH2D* XZHisto = new TH2D(Form("ZXrun%i-%ievent%i",run,subrun,event),Form("Z-X display for run %i-%i and event %i",run,subrun,event), 180, 0, 720, 180, -360, 360);
	TH2D* XYHisto = new TH2D(Form("XYrun%i-%ievent%i",run,subrun,event),Form("X-Y display for run %i-%i and event %i",run,subrun,event), 180, -360, 360, 152, 0, 608);

	TH2D* YZHistoBeam = new TH2D(Form("BeamZYrun%i-%ievent%i",run,subrun,event),Form("Z-Y display for run %i-%i and event %i",run,subrun,event), 110, -30, 80, 50, 390, 440);
	TH2D* XZHistoBeam = new TH2D(Form("BeamZXrun%i-%ievent%i",run,subrun,event),Form("Z-X display for run %i-%i and event %i",run,subrun,event), 110, -30, 80, 60, -60, 0);
	TH2D* XYHistoBeam = new TH2D(Form("BeamXYrun%i-%ievent%i",run,subrun,event),Form("X-Y display for run %i-%i and event %i",run,subrun,event), 60, -60, 0, 50, 390, 440);
	
	for(Int_t j = 0; j < vx->size(); j++){
	  Double_t vxval = vx->at(j);
	  Double_t vyval = vy->at(j);
	  Double_t vzval = vz->at(j);
	  Double_t vcval = vcharge->at(j)/1000.0;

	  XYHisto->Fill(vxval, vyval, vcval);
	  XZHisto->Fill(vzval, vxval, vcval);
	  YZHisto->Fill(vzval, vyval, vcval);

	  YZHistoBeam->Fill(vzval, vyval, vcval);
	  XZHistoBeam->Fill(vzval, vxval, vcval);
	  XYHistoBeam->Fill(vxval, vyval, vcval);
	}

	YZHisto->GetXaxis()->SetTitle("Z [cm]"); XZHisto->GetXaxis()->SetTitle("Z [cm]"); XYHisto->GetXaxis()->SetTitle("X [cm]");
	YZHisto->GetYaxis()->SetTitle("Y [cm]"); XZHisto->GetYaxis()->SetTitle("X [cm]"); XYHisto->GetYaxis()->SetTitle("Y [cm]");
	YZHisto->GetZaxis()->SetTitle("ADC counts (#times 10^{3})"); XZHisto->GetZaxis()->SetTitle("ADC counts (#times 10^{3})"); XYHisto->GetZaxis()->SetTitle("ADC counts (#times 10^{3})");
	YZHistoBeam->GetXaxis()->SetTitle("Z [cm]"); XZHistoBeam->GetXaxis()->SetTitle("Z [cm]"); XYHistoBeam->GetXaxis()->SetTitle("X [cm]");
	YZHistoBeam->GetYaxis()->SetTitle("Y [cm]"); XZHistoBeam->GetYaxis()->SetTitle("X [cm]"); XYHistoBeam->GetYaxis()->SetTitle("Y [cm]");
	YZHistoBeam->GetZaxis()->SetTitle("ADC counts (#times 10^{3})"); XZHistoBeam->GetZaxis()->SetTitle("ADC counts (#times 10^{3})"); XYHistoBeam->GetZaxis()->SetTitle("ADC counts (#times 10^{3})");
	YZHisto->SetStats(0); XZHisto->SetStats(0); XYHisto->SetStats(0);
	YZHistoBeam->SetStats(0); XZHistoBeam->SetStats(0); XYHistoBeam->SetStats(0);

	YZHisto->GetZaxis()->SetTitleOffset(1.2); XZHisto->GetZaxis()->SetTitleOffset(1.2); XYHisto->GetZaxis()->SetTitleOffset(1.2);
	YZHistoBeam->GetZaxis()->SetTitleOffset(1.2); XZHistoBeam->GetZaxis()->SetTitleOffset(1.2); XYHistoBeam->GetZaxis()->SetTitleOffset(1.2);

	// 
	TCanvas *cyz = new TCanvas(Form("CZYrun%i-%ievent%i",run,subrun,event),Form("Z-Y display for run %i-%i and event %i",run,subrun,event));
	cyz->SetFrameFillColor(kBlue+3);
	YZHisto->Draw("colz");
	if(YZHisto->GetEntries() > 0){
	  cyz->Update();
	  TPaletteAxis *yzpalette = (TPaletteAxis*)YZHisto->GetListOfFunctions()->FindObject("palette");
	  if(yzpalette)
	    yzpalette->SetX2NDC(0.92);
	  cyz->Modified();
	}
	cyz->SaveAs(imagestryz.Data());
	
	TCanvas *cxz = new TCanvas(Form("CZXrun%i-%ievent%i",run,subrun,event),Form("Z-X display for run %i-%i and event %i",run,subrun,event));
	cxz->SetFrameFillColor(kBlue+3);
	XZHisto->Draw("colz");
	if(XZHisto->GetEntries() > 0){
	  cxz->Update();
	  TPaletteAxis *xzpalette = (TPaletteAxis*)XZHisto->GetListOfFunctions()->FindObject("palette");
	  if(xzpalette)
	    xzpalette->SetX2NDC(0.92);
	  cxz->Modified();
	}
	cxz->SaveAs(imagestrxz.Data());

	TCanvas *cxy = new TCanvas(Form("CXYrun%i-%ievent%i",run,subrun,event),Form("X-Y display for run %i-%i and event %i",run,subrun,event));
	cxy->SetFrameFillColor(kBlue+3);
	XYHisto->Draw("colz");
	if(XYHisto->GetEntries() > 0){
	  cxy->Update();
	  TPaletteAxis *xypalette = (TPaletteAxis*)XYHisto->GetListOfFunctions()->FindObject("palette");
	  if(xypalette)
	    xypalette->SetX2NDC(0.92);
	  cxy->Modified();
	}
	cxy->SaveAs(imagestrxy.Data());

	vec.push_back(imagestrxy);
	vec.push_back(imagestrxz);
	vec.push_back(imagestryz);
	
	imagestrxy = runstr + TString("XYBeamEventDisplay.png");
	imagestrxz = runstr + TString("XZBeamEventDisplay.png");
	imagestryz = runstr + TString("YZBeamEventDisplay.png");

	TCanvas *cyzbeam = new TCanvas(Form("CBeamZYrun%i-%ievent%i",run,subrun,event),Form("Z-Y display for run %i-%i and event %i",run,subrun,event));
	cyzbeam->SetFrameFillColor(kBlue+3);
	YZHistoBeam->Draw("colz");
	if(drawbeamline)
	  yzline->Draw("same");
	else
	  YZHistoBeam->GetXaxis()->SetRangeUser(0,80);
	if(YZHistoBeam->GetEntries() > 0){
	  cyzbeam->Update();
	  TPaletteAxis *byzpalette = (TPaletteAxis*)YZHistoBeam->GetListOfFunctions()->FindObject("palette");
	  if(byzpalette)
	    byzpalette->SetX2NDC(0.92);
	  cyzbeam->Modified();
	}
	cyzbeam->SaveAs(imagestryz.Data());

	TCanvas *cxzbeam = new TCanvas(Form("CBeamZXrun%i-%ievent%i",run,subrun,event),Form("Z-X display for run %i-%i and event %i",run,subrun,event));
	cxzbeam->SetFrameFillColor(kBlue+3);
	XZHistoBeam->Draw("colz");
	if(drawbeamline)
	  xzline->Draw("same");
	else
	  XZHistoBeam->GetXaxis()->SetRangeUser(0,80);
	if(XZHistoBeam->GetEntries() > 0){
	  cxzbeam->Update();
	  TPaletteAxis *bxzpalette = (TPaletteAxis*)XZHistoBeam->GetListOfFunctions()->FindObject("palette");
	  if(bxzpalette)
	    bxzpalette->SetX2NDC(0.92);
	  cxzbeam->Modified();
	}
	cxzbeam->SaveAs(imagestrxz.Data());

	TCanvas *cxybeam = new TCanvas(Form("CBeamXYrun%i-%ievent%i",run,subrun,event),Form("X-Y display for run %i-%i and event %i",run,subrun,event));
	cxybeam->SetFrameFillColor(kBlue+3);
	XYHistoBeam->Draw("colz");
	if(drawbeamline)
	  xyline->Draw("same");
	if(XYHistoBeam->GetEntries() > 0){
	  cxybeam->Update();
	  TPaletteAxis *bxypalette = (TPaletteAxis*)XYHistoBeam->GetListOfFunctions()->FindObject("palette");
	  if(bxypalette)
	    bxypalette->SetX2NDC(0.92);
	  cxybeam->Modified();
	}
	cxybeam->SaveAs(imagestrxy.Data());

	beamvec.push_back(imagestrxy);
	beamvec.push_back(imagestrxz);
	beamvec.push_back(imagestryz);

      }
    }
  }

  // Write in json file
  FILE *JsonspsFile = fopen(jsonfile.Data(),"w");
  fprintf(JsonspsFile,"[\n");
  fprintf(JsonspsFile,"   {\n");

  fprintf(JsonspsFile,"     \"Category\":\"2D event displays\",\n");
  fprintf(JsonspsFile,"      \"Files\": {\n");
  fprintf(JsonspsFile,"        \"Event Displays\":\"");
  for(UInt_t i=0; i < vec.size(); i++){
    TString strtolook = vec[i];
    if(i < vec.size()-1)
      fprintf(JsonspsFile,"%s,",strtolook.Data());
    else
      fprintf(JsonspsFile,"%s\",\n",strtolook.Data());
  }

  fprintf(JsonspsFile,"         \"Event Displays beam particle\":\"");
  for(UInt_t i=0; i < beamvec.size(); i++){
    TString strtolook = vec[i];
    if(i < vec.size()-1)
      fprintf(JsonspsFile,"%s,",strtolook.Data());
    else
      fprintf(JsonspsFile,"%s\"\n",strtolook.Data());
  }

  fprintf(JsonspsFile,"     }\n");

  fprintf(JsonspsFile,"   }\n");
  fprintf(JsonspsFile,"]\n");

  // Close file
  fclose(JsonspsFile);
  
}

// --------------------------------------------------
void PrintCRTSummary(TDirectory *dir, TString jsonfilename, TString srun, TString sdate){
  // --------------------------------------------------

  // Open file
  FILE *crtJsonFile = fopen(jsonfilename.Data(),"w");

  fprintf(crtJsonFile,"[\n");
  fprintf(crtJsonFile,"   {\n");

  fprintf(crtJsonFile,"      \"Type\": \"crt\"\n");
  
  fprintf(crtJsonFile,"   }\n");
  fprintf(crtJsonFile,"]\n");

  // Close file
  fclose(crtJsonFile);

}

//Helper objects for CRT plotting
namespace
{
  //Keep track of the old gStyle just before I create a new one so that I don't change 
  //global settings that will affect other plots.  
  class StyleSentry
  {
    public:
      StyleSentry(): fRestore(gStyle), fMyStyle(*gStyle) //Make sure I take a copy of whatever is in gStyle to 
                                                         //accumulate settings from other users.
      {
        //Histograms
        gStyle->SetOptTitle(1); //Turns on drawing the canvas title?
        gStyle->SetTitleSize(0.04); //Make the canvas title bigger
        //gStyle->SetOptStat(0); //Disable the statistics box on histograms
        gStyle->SetLabelSize(0.04, "X"); //Make x axis labels bigger
        gStyle->SetLabelSize(0.04, "Y"); //Make y axis labels bigger
        gStyle->SetTitleSize(0.04, "X"); //Make x axis titles bigger
        gStyle->SetTitleSize(0.04, "Y"); //Make y axis titles bigger
        gStyle->SetTitleOffset(1.4, "Y"); //Move the y axis titles farther away from the axis than the default distance
        gStyle->SetHistLineWidth(2); //Default in ROOT is 1

        //Make sure my style gets applied
        gROOT->ForceStyle();
        gStyle = &fMyStyle;     
      }

      ~StyleSentry() { gStyle = fRestore; }

    private:
      TStyle* fRestore; //Restore gStyle to this pointed object when StyleSentry goes out of scope
      TStyle fMyStyle; //My histogram drawing style.  I own it and intend to make sure gStyle doesn't try to use it 
                       //when this object goes out of scope.  
  };

  void PrintDirectory(TDirectory* dir, FILE* JSONFile)
  {
    fprintf(JSONFile, "%s", ("        \""+std::string(dir->GetName())+"\":\"").c_str()); //Start JSON Mapped value
    bool first = true;
    for(auto key: *(dir->GetListOfKeys()))
    {
      if(first)
      {
        first = false;
      }
      else fprintf(JSONFile, ",");

      auto obj = ((TKey*)key)->ReadObj();
      
      //If this object is a directory, don't do anything to it for now...
      auto nested = dynamic_cast<TDirectory*>(obj);
      if(nested) continue; //TODO: continue can be the root of much evil... Try harder to avoid using it.
      
      //I want to make sure I apply the "colz" option to TH2s 
      //and the "A*" option to TGraphs.  So, check whether obj 
      //is derived from either of those types.
      if(dynamic_cast<TH2*>(obj))
      {
        ((TH2*)obj)->SetStats(false);
        obj->Draw("colz");
      }
      else if(dynamic_cast<TH1*>(obj))
      {
        ((TH1*)obj)->SetStats(false);
        obj->Draw("HIST"); //Suppress error bars
      }
      else if(dynamic_cast<TGraph*>(obj))
      {
        obj->Draw("A*");
      }
      else obj->Draw();

      const auto name = std::string(dir->GetName())+obj->GetName()+".png";
      gPad->Print(name.c_str());
      fprintf(JSONFile, "%s", name.c_str());
    }
    fprintf(JSONFile,"\"\n     }\n"); //End JSON mapped value and map entry
  }
}

// --------------------------------------------------
void MakeCRTPlots(TDirectory *dir, TString jsonfile){
  // --------------------------------------------------

  //Make sure my changes to gStyle don't affect other functions
  ::StyleSentry style;

  FILE *JsoncrtFile = fopen(jsonfile.Data(),"w");
  fprintf(JsoncrtFile,"[\n");
  fprintf(JsoncrtFile,"   {\n");

  fprintf(JsoncrtFile,"     \"Category\":\"CRT\",\n"); //It seems like I could create other Categories in a similar way if I find the need
  fprintf(JsoncrtFile,"      \"Files\": {\n");

  for(auto key: *(dir->GetListOfKeys()))
  {
    auto obj = ((TKey*)key)->ReadObj();
    auto nested = dynamic_cast<TDirectory*>(obj);
    if(nested) PrintDirectory(nested, JsoncrtFile);
    //Ignore any objects in top CRT directory that aren't directories because I'm not producing any of those anyway.  
  }
  // These are example - replace with real png names
  /*fprintf(JsoncrtFile,"        \"File section 1\":\"");
  fprintf(JsoncrtFile,"File1.png,");
  fprintf(JsoncrtFile,"File2.png\",\n");

  fprintf(JsoncrtFile,"        \"File section 2\":\"");
  fprintf(JsoncrtFile,"File3.png,");
  fprintf(JsoncrtFile,"File4.png,");
  fprintf(JsoncrtFile,"File5.png\"\n");
  
  fprintf(JsoncrtFile,"     }\n");*/

  fprintf(JsoncrtFile,"   }\n");
  fprintf(JsoncrtFile,"]\n");

  // Close file
  fclose(JsoncrtFile);

}
