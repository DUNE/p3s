#include "TH1F.h"
#include "TCanvas.h"
#include "TFile.h"
#include "TImage.h"

void rootTest() {
  TFile* accFile= new TFile("merge201803270002.root", "READ");
  TH1F* accHist0= (TH1F*) accFile->Get(TString("c0"));
  TH1F* accHist1= (TH1F*) accFile->Get(TString("c1"));
  TCanvas* canv = new TCanvas("canv","test", 800,800);
  canv->Divide(1,2);
  canv->cd(1);
  accHist0->Draw();
  accHist1->Draw();
  accHist1->Draw();
  accHist0->Draw();
  canv->cd(1);
  accHist1->Draw();
  canv->cd(0);
  accHist1->Draw();
  canv->cd(2);
  accHist1->Draw();
  canv->cd(1);
  accHist1->Draw();
  canv->Clear();
  canv->cd(1);
  accHist1->Draw();
  canv->Divide(1,2);
  canv->cd(1);
  accHist0->Draw();
  canv->cd(2);
  accHist0->Draw();
  accHist1->Draw();
  TImage *img = TImage::Create();
  img->FromPad(canv);
  img->WriteImage("foo3.png");
  gApplication->Terminate();
}

