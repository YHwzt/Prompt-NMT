WORK_PATH="/home/wangzt/program/PromoptNMT"
MODEL_PATH="/data/user/WZT/data_de-en/prompt_model/baseline"
DATA_PATH="/data/user/WZT/iwslt14_de-en"
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
vinp=$DATA/valid/valid.toke.10kbpe.$src
vref=$DATA/valid/valid.toke.$tgt
#sed -r 's/(@@ )|(@@ ?$)//g' $DATA/valid/valid.$tgt > $vref
python -u $WORK_PATH/thumt/bin/trainer.py \
  --input $DATA/train/train.toke.10kbpe.shuf.$src $DATA/train/train.toke.10kbpe.shuf.$src \
  --vocabulary $DATA/train/vocab.toke.10kbpe.de-en.txt $DATA/train/vocab.toke.10kbpe.de-en.txt \
  --model transformer \
  --validation $vinp \
  --references $vref \
  --output $MODEL_PATH \
  --parameters=device_list=[$device],train_steps=100000,batch_size=4096,log_steps=100,eval_steps=1000,update_cycle=1 \
  --half \
  --hparam_set iwslt14deen 2>&1 | tee $MODEL_PATH/train.log.$time