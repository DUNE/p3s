firstFile=`ls -X ${P3S_INPUT_DIR} | head -n 1`
firstTime=`basename ${firstFile} .dec`
run=`basename ${P3S_INPUT_DIR} | egrep -o [0-9]+`
echo "[
   {
     \"run\": \"run${run}_${firstTime}_dl1\",
     \"TimeStamp\": \"00/00/00\",
     \"Type\": \"crt\"
   }
]"
