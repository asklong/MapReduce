set -x


NAME="normalize_word"
REDUCER_NUM=10

MAPPER="${NAME}.mapper.py"
MAPPER_PATH="./$MAPPER"

REDUCER="${NAME}.reducer.py"
REDUCER_PATH="./$REDUCER"

# The mapping of the complex and the simple.
COMPLEX_SIMPLE="complex_simple"
COMPLEX_SIMPLE_PATH="./$COMPLEX_SIMPLE"

# The stop word of the project.
STOP_WORD="stop_word"
STOP_WORD_PATH="./$STOP_WORD"

USERDICT="userdict"
USERDICT_PATH="./$USERDICT"

day=`date -d "2 days ago" +%Y-%m-%d`

for TASK_ID in {1..1}
do
    INPUT="/user/jd_ad/ads_reco/kejin/word2vec/sku_infor/${day}/"
    OUTPUT="/user/jd_ad/ads_reco/kejin/word2vec/words/${day}"
    hadoop fs -test -e $OUTPUT
    if [ $? -eq 0 ]
    then
        hadoop fs -rmr $OUTPUT
    fi

    hadoop jar /software/servers/hadoop-2.2.0/share/hadoop/tools/lib/hadoop-streaming-2.2.0.jar  \
           -D mapred.job.priority=HIGH  \
           -D mapred.job.name="$NAME"  \
           -D mapred.reduce.tasks=$REDUCER_NUM \
           -cacheArchive "/user/jd_ad/yan.yan/archive/python2.7.tar.gz#python27"  \
           -input "${INPUT}" \
           -output "${OUTPUT}"  \
           -mapper "python27/bin/python2.7 ${MAPPER} --stop_word=$STOP_WORD --complex_simple=$COMPLEX_SIMPLE --userdict=$USERDICT" \
           -file "${MAPPER_PATH}" -file "$STOP_WORD_PATH" \
           -file "$COMPLEX_SIMPLE_PATH" -file $USERDICT_PATH \
           -reducer "python27/bin/python2.7 ${REDUCER}" \
           -file "${REDUCER_PATH}"
done

# -mapper "python27/bin/python2.7 ${MAPPER} --userdict=$USERDICT" \
# -mapper "python27/bin/python2.7 ${MAPPER} --stop_word=$STOP_WORD --complex_simple=$COMPLEX_SIMPLE --userdict=$USERDICT"     \
