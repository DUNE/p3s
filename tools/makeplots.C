// makeplots.C
// based on Stefan Schmitt's hadd.C in tutorials/io
// makes a directory called html, puts png files in it,
// with an index.html file.
// to execute non-interactively:  root -b -l -q 'makeplots.C("rawtpcmonitor.root");'

#include <string.h>
#include "TChain.h"
#include "TFile.h"
#include "TH1.h"
#include "TTree.h"
#include "TKey.h"
#include "Riostream.h"
#include "TCanvas.h"
#include "stdio.h"
#include "TProfile.h"

TFile *Target;
TCanvas *c1;
FILE *indexhtml;

void mpa (TDirectory *dir);

void makeplots(TString infile="rawtpcmonitor.root")
{
  gSystem->mkdir("html");
  indexhtml = fopen("html/index.html","w");
  fprintf(indexhtml,"<h1>Histograms from %s</h1>\n",infile.Data());
  c1 = new TCanvas("c1","c1",800,800);
  TFile *f = new TFile(infile,"READ");
  TDirectory *current_sourcedir = gDirectory;
  mpa(current_sourcedir);
  fclose(indexhtml);
}

void mpa(TDirectory *current_sourcedir)
{


  // loop over all keys in this directory
  TIter nextkey( current_sourcedir->GetListOfKeys() );
  TKey *key, *oldkey=0;
  while ( (key = (TKey*)nextkey())) 
    {
    //plot only the highest cycle number for each key
    if (oldkey && !strcmp(oldkey->GetName(),key->GetName())) continue;

    // read object from  source file
    TObject *obj = key->ReadObj();

    if ( obj->IsA()->InheritsFrom( TH1::Class() ) ) 
      {
	// descendant of TH1 -> make a plot

	TH1 *h1 = (TH1*)obj;
	 
	if (h1->GetNbinsY()==1)
	  {
	    h1->SetStats(true);
	    if (obj->IsA()->InheritsFrom( TProfile::Class() ) )
	      {
  	         h1->SetStats(false);
	      } 
	    h1->Draw("hist,e0");
	  }
	else
	  {
	    h1->SetStats(false);
	    h1->Draw("colz");
	  }
	TString outfilename="html/";
	TString figname = key->GetName();
	figname.ReplaceAll("#","_");
	figname += ".png";
	outfilename += figname;
	c1->Print(outfilename);
	fprintf(indexhtml,"<a href=%s><img src=%s width=300></a>\n",figname.Data(),figname.Data());
	
      }
    else if ( obj->IsA()->InheritsFrom( TDirectory::Class() ) ) 
      {
	// it's a subdirectory

	//cout << "Found subdirectory " << obj->GetName() << endl;
        fprintf(indexhtml,"<h2>%s</h2>\n",obj->GetName());

        current_sourcedir->cd(obj->GetName());
	TDirectory *subdir = gDirectory;
	mpa(subdir);
	current_sourcedir->cd("..");
      } 
    else 
      {

	// object is of no type that we know or can handle
	cout << "Unknown object type, name: "
	     << obj->GetName() << " title: " << obj->GetTitle() << endl;
      }
  }
}


