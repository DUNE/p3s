# Script to convert 3D space point ROOT file to Bee's json file

## Compile

```bash
root -b -q loadClasses.C
```

## Run

```bash
root -b -q loadClasses.C 'run.C("input_root_file", "output_json_file")'
```
