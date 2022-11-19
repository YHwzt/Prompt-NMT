WORK_PATH="/home/wangzt/program/PromoptNMT"
MODEL_PATH="/data/user/WZT/data_de-en/prompt_model/phase1transformer1"
DATA_PATH="/data/user/WZT/iwslt14_de-en"
mkdir -p $MODEL_PATH
DATA=$DATA_PATH
export PYTHONPATH=$WORK_PATH
device=0
src=de
tgt=en
time=$(date +'%m:%d:%H:%M')

# train
ratio=0.35
flip_ratio=0.3
vinp=$DATA/valid/valid.$src
vref=$DATA/valid/valid.$tgt
#sed -r 's/(@@ )|(@@ ?$)//g'  $DATA/valid/valid.$tgt > $vref
python -u $WORK_PATH/thumt/bin/trainer.py \
  --input $DATA/train/train.toke.10kbpe.shuf.$src $DATA/train/train.toke.10kbpe.shuf.$tgt \
  --vocabulary $DATA/train/vocab.toke.10kbpe.de-en.txt $DATA/train/vocab.toke.10kbpe.de-en.txt \
  --model phase1transformer \
  --validation $vinp \
  --references $vref \
  --output $MODEL_PATH \
  --parameters=device_list=[$device],train_steps=200000,batch_size=4096,log_steps=100,eval_steps=1000,keep_top_checkpoint_max=5,update_cycle=1,normalization="after",phase=1,ratio=$ratio,flip_ratio=$flip_ratio,sample_train_mode=0,sample_infer_mode=0,reuse_encoder=True  \
  --advice $DATA/train/trainNew2.advices $DATA/valid/validNew2.advices \
  --half \
  --hparam_set iwslt14deen 2>&1 | tee $MODEL_PATH/train.log.$time

