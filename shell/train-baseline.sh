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
vinp=$DATA/valid/valid.32k.$src
vref=$MODEL_PATH/valid.$tgt.debpe
sed -r 's/(@@ )|(@@ ?$)//g' $DATA/valid/valid.$tgt > $vref
python -u $WORK_PATH/thumt/bin/trainer.py \
  --input $DATA/train/train.32k.$src.shuf $DATA/train/train.32k.$tgt.shuf \
  --vocabulary $DATA/train/vocab.32k.de-en.txt $DATA/train/vocab.32k.de-en.txt \
  --model transformer \
  --validation $vinp \
  --references $vref \
  --output $MODEL_PATH \
  --parameters=device_list=[$device],train_steps=100000,batch_size=4096,log_steps=100,eval_steps=1000,update_cycle=1 \
  --half \
  --hparam_set iwslt14deen 2>&1 | tee $MODEL_PATH/train.log.$time