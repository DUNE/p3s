// makeplotsV6.C
// to execute non-interactively:  root -b -l -q 'makeplotsV6.C("rawtpcmonitor.root");'
// root -b -l -q 'makeplotsV6.C("rawtpcmonitor.root");' > /dev/null 2>&1

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

TCanvas *c1;

// These are per APA
int exp_deadch[6] = {0,0,0,0,0,0};
int exp_noisych1[6] = {0,0,0,0,0,0};
int exp_noisych2[6] = {0,0,0,0,0,0};

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
void PrintGausHitsJson(TDirectory *dir, TString jsonfilename);
void PrintSummaryPlots(FILE *file, TObjArray* dir, TString keyname, TString keyname2, TString runname, bool setlogy);
void IncludeOverflow(TH1 *h);
void SaveImageNameInJson(TString jsonfile, TString dirstr, std::vector<TString> imagevec);
TString FindImagesAndPrint(TString strtolook, TString strtolook2, TString dirstr, std::vector<TString> imagevec);
void PlotDistToMean(TH1 *h,Int_t mean);

void makeplotsV6(TString infile="rawtpcmonitor.root"){

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

  TRegexp re(".root");
  TString s_infile = infile;
  s_infile(re) = " ";
  //TString s_infile("TPCMonitor");

  // Define canvas
  c1 = new TCanvas("c1","c1",800,800);

  // Create summary json file
  for(int i=0; i < directories_in_file.size(); i++){
    TString dirstr = directories_in_file.at(i);
    if(dirstr.Contains("pdspnearlineheader")) continue;

    current_sourcedir->cd(dirstr.Data());
    TDirectory *subdir = gDirectory;
    TString subdirname = dirstr + TString("/");

    // Special for different modules
    if(dirstr.Contains("tpcmonitor")){
      subdirname = runstr + TString("_summary.json");
      PrintDeadNoisyChannelsJson(subdir, subdirname, runstr, datestr);
    }
    else if(dirstr.Contains("pdsphitmonitor")){
      subdirname = runstr + TString("_summary.json");
      PrintGausHitsJson(subdir, subdirname);
    }
    else if(dirstr.Contains("sspmonitor")){
      //
    }

    current_sourcedir->cd("..");
  }

  for(int i=0; i < directories_in_file.size(); i++){
    TString dirstr = directories_in_file.at(i);
    if(dirstr.Contains("pdspnearlineheader")) continue;
  }

  // Create json file containing the list of histograms
  TString jsonfile = runstr + TString("_FileList.json");
  FILE *jfile = fopen(jsonfile.Data(),"w");
  fprintf(jfile,"[\n");
  fclose(jfile);

  // Loop to save histograms
  for(int i=0; i < directories_in_file.size(); i++){
    TString dirstr = directories_in_file.at(i);

    if(dirstr.Contains("pdspnearlineheader")) continue;
    current_sourcedir->cd(dirstr.Data());
    TDirectory *subdir = gDirectory;

    // Save all histograms
    std::vector<TString> imagenamevec;
    TObjArray* vec = SaveHistosFromDirectory(subdir, runstr, datestr, imagenamevec);
    vec->SetName(subdir->GetName()); // important

    SaveImageNameInJson(jsonfile, dirstr, imagenamevec);

    // Make sumamry plot for tpcmonitor - this should probably move to its own class
    if(dirstr.Contains("tpcmonitor")){
      //std::cout << "INFO::Attempting to plot from " << dirstr.Data() << std::endl;
      if(SAVELISTOFDEADNOISYCHANNELS){
	PrintListofDeadNoisyChannels(vec, "fNDeadChannelsList",             "fNDeadChannelsList");
	PrintListofDeadNoisyChannels(vec, "fNNoisyChannelsListFromNSigma",  "fNNoisyChannelsListFromNSigma");
	PrintListofDeadNoisyChannels(vec, "fNNoisyChannelsListFromNCounts", "fNNoisyChannelsListFromNCounts");
      }
    } // end of tpcmonitor
    if(dirstr.Contains("pdsphitmonitor")){
      //std::cout << "INFO::Attempting to plot from " << dirstr.Data() << std::endl;
    }
    if(dirstr.Contains("sspmonitor")){
      //std::cout << "INFO::Attempting to plot from " << dirstr.Data() << std::endl;
    }
    
    delete vec;

    current_sourcedir->cd("..");
    
  }

  FILE *jcfile = fopen(jsonfile.Data(),"a");
  fprintf(jcfile,"]\n");
  fclose(jcfile);
  
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
	  cdate = asctime(gmtime(&epoch));
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
	    if(subrunfirst >= 100)
	      runid.Form("run%i_%i",runfirst,subrunfirst);
	    else if(subrunfirst >= 10)
	      runid.Form("run%i_0%i",runfirst,subrunfirst);
	    else if(subrunfirst >= 0)
	      runid.Form("run%i_00%i",runfirst,subrunfirst);
	  }
	  else if(runfirst >= 10000){
            if(subrunfirst >= 100)
              runid.Form("run0%i_%i",runfirst,subrunfirst);
            else if(subrunfirst >= 10)
              runid.Form("run0%i_0%i",runfirst,subrunfirst);
            else if(subrunfirst >= 0)
              runid.Form("run0%i_00%i",runfirst,subrunfirst);
          }
	  else if(runfirst >= 1000){
            if(subrunfirst >= 100)
              runid.Form("run00%i_%i",runfirst,subrunfirst);
            else if(subrunfirst >= 10)
              runid.Form("run00%i_0%i",runfirst,subrunfirst);
            else if(subrunfirst >= 0)
              runid.Form("run00%i_00%i",runfirst,subrunfirst);
	  }
	  else if(runfirst >= 100){
            if(subrunfirst >= 100)
              runid.Form("run000%i_%i",runfirst,subrunfirst);
            else if(subrunfirst >= 10)
              runid.Form("run000%i_0%i",runfirst,subrunfirst);
            else if(subrunfirst >= 0)
              runid.Form("run000%i_00%i",runfirst,subrunfirst);
          }
	  else if(runfirst >= 10){
            if(subrunfirst >= 100)
              runid.Form("run0000%i_%i",runfirst,subrunfirst);
            else if(subrunfirst >= 10)
              runid.Form("run0000%i_0%i",runfirst,subrunfirst);
            else if(subrunfirst >= 0)
              runid.Form("run0000%i_00%i",runfirst,subrunfirst);
          }
	  else if(runfirst >= 0){
            if(subrunfirst >= 100)
              runid.Form("run00000%i_%i",runfirst,subrunfirst);
            else if(subrunfirst >= 10)
              runid.Form("run00000%i_0%i",runfirst,subrunfirst);
            else if(subrunfirst >= 0)
              runid.Form("run00000%i_00%i",runfirst,subrunfirst);
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
      }
      
      //TString HistoTitle = runname + TString(":") + TString(h->GetTitle());
      TString HistoName = runname + TString("_") + TString(dir->GetName()) + TString("_") + objname;

      TH1 *h1 = (TH1*)h->Clone("hnew");
      h1->SetDirectory(0);
      h1->SetTitle(h->GetTitle());
      h1->SetName(HistoName.Data());

      h1->GetXaxis()->SetTitle(h->GetXaxis()->GetTitle());
      h1->GetYaxis()->SetTitle(h->GetYaxis()->GetTitle());
      h1->GetYaxis()->SetTitleOffset(1.4);

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

      // Add horizontal line for expected number of dead channels
      if(HistoName.Contains("NDeadChannelsHisto")){
	for(int i=1;i<=6;i++){
	  TLine *line = new TLine(h1->GetXaxis()->GetBinLowEdge(i),exp_deadch[i-1],h1->GetXaxis()->GetBinLowEdge(i)+h1->GetXaxis()->GetBinWidth(i),exp_deadch[i-1]);
          line->SetLineColor(kRed);
          line->SetLineWidth(2);
          line->Draw();
	}
      }
      else if(HistoName.Contains("NNoisyChannelsHistoFromNCounts")){
        for (int i=1;i<=6;i++){
          TLine *line = new TLine(h1->GetXaxis()->GetBinLowEdge(i), exp_noisych1[i-1],h1->GetXaxis()->GetBinLowEdge(i)+h1->GetXaxis()->GetBinWidth(i), exp_noisych1[i-1]);
          line->SetLineColor(kRed);
          line->SetLineWidth(2);
          line->Draw();
        }
      }
      else if(HistoName.Contains("NNoisyChannelsHistoFromNSigma")){
        for (int i=1;i<=6;i++){
          TLine *line = new TLine(h1->GetXaxis()->GetBinLowEdge(i), exp_noisych2[i-1],h1->GetXaxis()->GetBinLowEdge(i)+h1->GetXaxis()->GetBinWidth(i), exp_noisych2[i-1]);
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
      gPad->Update();
      TPaveText * pt = (TPaveText *)gPad->FindObject("title");
      TString datename_new = runname + TString("(taken on ") + datename + TString(")");
      pt->InsertText(datename_new.Data());
      pt->SetX1NDC(0.05);   pt->SetY1NDC(0.9);
      pt->SetX2NDC(0.75);    pt->SetY2NDC(0.99);
      pt->SetTextSize(0.03);
      pt->Draw();
    
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

  fprintf(deadchanJsonFile,"      \"NDead  Channels\": \"%s\",\n",deadchannel_str.Data());
  fprintf(deadchanJsonFile,"      \"NNoisy Channels-1\": \"%s\",\n",nois1channel_str.Data());
  fprintf(deadchanJsonFile,"      \"NNoisy Channels-2\": \"%s\"\n",nois2channel_str.Data());
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
      TString tempstr = Form("%f,",(float)h1->GetMean());
      
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
      TString tempstr = Form("%f,",(float)h1->GetMean());
      TString tempstr2 = Form("%f,",(float)h1->GetRMS());
      
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
      TString tempstr = Form("%f,",(float)h1->GetMean());
      TString tempstr2 = Form("%f,",(float)h1->GetRMS());

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
    fprintf(JsonFile,"     \"Files\":\n");

    fprintf(JsonFile,"       {\"Plots\":\"");
    TString filesstr = FindImagesAndPrint(dirstr, dirstr, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\"}\n");

    fprintf(JsonFile,"   },\n");
  }
  else if(dirstr.Contains("pdsphitmonitor")){ // Hit Monitor
    TString category("Hit Monitor");
    fprintf(JsonFile,"   {\n");
    fprintf(JsonFile,"     \"Category\":\"%s\",\n",category.Data());
    fprintf(JsonFile,"     \"Files\":\n");
    
    TString strtolook("NHitsAPA");
    fprintf(JsonFile,"       {\"Number of hits per APA per view\":\"");
    TString filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");
    
    strtolook = "HitChargeAPA";
    fprintf(JsonFile,"       \"Hit Charge distribution per APA per view\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");
    
    strtolook = "HitRMSAPA";
    fprintf(JsonFile,"       \"Hit RMS distribution per APA per view\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n"); 
    
    strtolook = "HitPeakTimeAPA";
    fprintf(JsonFile,"       \"Hit peak time distribution per APA per view\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n"); 
    
    strtolook = "fNHitsView";
    fprintf(JsonFile,"       \"Profiled number of hits\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n"); 
    
    strtolook = "fChargeView";
    fprintf(JsonFile,"       \"Profiled hit charge\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n"); 
    
    strtolook = "fRMSView";
    fprintf(JsonFile,"       \"Profiled hit RMS\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\"}\n"); 
    
    fprintf(JsonFile,"   },\n");
  }
  else if(dirstr.Contains("tpcmonitor")){ // TPC monitor
    TString category("TPC Monitor");
    fprintf(JsonFile,"   {\n");
    fprintf(JsonFile,"     \"Category\":\"%s\",\n",category.Data());
    fprintf(JsonFile,"     \"Files\":\n");
  
    TString strtolook("fChanRMSDist");
    fprintf(JsonFile,"       {\"RMS of ADC per view per APA for all channels\":\"");
    TString filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

    strtolook = "fChanMeanDist";
    fprintf(JsonFile,"       \"Mean of ADC per view per APA for all channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

    strtolook = "fChanRMS";
    TString strtolook2("pfx");
    fprintf(JsonFile,"       \"RMS of ADC per view per APA and per channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

    strtolook = "fChanMean";
    fprintf(JsonFile,"       \"Mean of ADC per view per APA and per channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

    strtolook = "Slot";
    strtolook2 = "RMSpfx";
    fprintf(JsonFile,"       \"RMS of channel ADC from slot\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

    strtolook = "Slot";
    strtolook2 = "Meanpfx";
    fprintf(JsonFile,"       \"Mean of channel ADC from slot\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook2, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

    strtolook = "fChanStuckCodeOnFrac";
    fprintf(JsonFile,"       \"Channel stuck code on\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

    strtolook = "fChanStuckCodeOffFrac";
    fprintf(JsonFile,"       \"Channel stuck code off\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

    strtolook = "fChanFFT";
    fprintf(JsonFile,"       \"FFT\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

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
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

    strtolook = "fNNoisyChannels";
    fprintf(JsonFile,"       \"Number of noisy channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\",\n");

    strtolook = "NTicks";
    fprintf(JsonFile,"       \"Number of Ticks in TPC channels\":\"");
    filesstr = FindImagesAndPrint(strtolook, strtolook, dirstr, imagevec);
    fprintf(JsonFile,"%s",filesstr.Data());
    fprintf(JsonFile,"\"}\n");

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
