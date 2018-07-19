#ifndef LIVEEVENT_H
#define LIVEEVENT_H

#include <vector>
#include <map>
#include <iostream>
#include <fstream>
#include "TString.h"

class TTree;
class TFile;
class TDatabasePDG;

class LiveEvent {
public:
    TFile *rootFile;
    ofstream jsonFile;
    TTree *T;

    int run;
    int subrun;
    int event;
    double evttime;
    std::vector<double> *vx;
    std::vector<double> *vy;
    std::vector<double> *vz;
    std::vector<double> *vcharge;

    LiveEvent();
    LiveEvent(const char* filename, const char* jsonFileName="0-3d.json");
    virtual ~LiveEvent();

    void ReadEventTree();
    void Write(int i=0);
    void WriteRandom();


    void print_vector(ostream& out, vector<double>& v, TString desc, bool end=false);
};

#endif
