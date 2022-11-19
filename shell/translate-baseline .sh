WORK_PATH="/home/wangtongli/wzt/PromptNMT"
MODEL_PATH="/data/user/WzT/Prompt_baseline"
DATA_PATH="/data/user/WzT/de_en_data"
mkdir -p $MODEL_PATH
DATA=$DATA_PATH
export PYTHONPATH=$WORK_PATH
device=0
src=de
tgt=en
time=$(date +'%m:%d:%H:%M')

# inference
for file in $MODEL_PATH/eval/model-[0-9]*.pt
do
  model=${file##*/}
  inp=$DATA/test.$src
  ref=$MODEL_PATH/eval/test.$tgt.debpe
  hyp=$MODEL_PATH/eval/test.$src.out.$model
  sed -r 's/(@@ )|(@@ ?$)//g' $DATA/test.$tgt > $ref
  python -u $WORK_PATH/thumt/bin/translator.py \
    --models transformer \
    --input $inp \
    --output $hyp \
    --vocabulary $DATA/dict/vocab.de.txt $DATA/dict/vocab.en.txt \
    --checkpoints $MODEL_PATH/eval --specific-ckpt $MODEL_PATH/eval/$model \
    --parameters=device_list=[$device],decode_batch_size=32,decode_alpha=0.6,beam_size=5 2>&1 | tee $MODEL_PATH/eval/test.log.$model.$time
  sed -r 's/(@@ )|(@@ ?$)//g' $hyp > $hyp.debpe
  sacrebleu $ref -i $hyp.debpe -tok none -m bleu -w 4 -b > $MODEL_PATH/eval/bleu.log.$model.$time
done

