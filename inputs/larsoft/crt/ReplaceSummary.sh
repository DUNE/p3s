firstFile=`ls -X ${P3S_INPUT_DIR} | head -n 1`
firstTime=`basename ${firstFile} .dec`
run=`basename ${P3S_INPUT_DIR}`
echo "[
   {
     \"run\": \"run${run}_${firstTime}dl001\",
     \"TimeStamp\": \"00/00/00\",
     \"Type\": \"monitor\"
   }
]"
