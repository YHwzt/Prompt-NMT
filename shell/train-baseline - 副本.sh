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

# train
# vinp=$DATA/tmp/valid.$src
# vref=$MODEL_PATH/valid.$tgt.debpe
vinp=$DATA/valid.32k.$src
vref=$MODEL_PATH/valid.$tgt.debpe
sed -r 's/(@@ )|(@@ ?$)//g' $DATA/valid.$tgt > $vref
python -u $WORK_PATH/thumt/bin/trainer.py \
  --input $DATA/train.32k.$src.shuf $DATA/train.32k.$tgt.shuf \
  --vocabulary $DATA/vocab.32k.de-en.txt $DATA/vocab.32k.de-en.txt \
  --model transformer \
  --validation $vinp \
  --references $vref \
  --output $MODEL_PATH \
  --parameters=device_list=[$device],train_steps=100000,batch_size=4096,log_steps=100,eval_steps=1000,update_cycle=1 \
  --half \
  --hparam_set iwslt14deen 2>&1 | tee $MODEL_PATH/train.log.$time


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

