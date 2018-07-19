void run(const char* input="tmp/eventtree.root", const char* output="0-3d.json")
{
    gROOT->Reset();
    // gROOT->ProcessLine(".x loadClasses.C" );
    // gErrorIgnoreLevel=2001;
    LiveEvent ev(input, output);
    ev.WriteRandom();
}