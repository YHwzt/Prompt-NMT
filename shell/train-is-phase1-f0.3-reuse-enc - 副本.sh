WORK_PATH="/home/wangtongli/wzt/PromptNMT"
MODEL_PATH="/data/user/WzT/is_phase1.1_fratio0.3_reuse_enc"
DATA_PATH="/data/user/WzT/de_en_data"
mkdir -p $MODEL_PATH
DATA=$DATA_PATH
device=0
src=de
tgt=en
time=$(date +'%m:%d:%H:%M')

# train
ratio=0.35
flip_ratio=0.3
vinp=$DATA/valid/valid.32k.$src
vref=$MODEL_PATH/valid.$tgt.debpe
sed -r 's/(@@ )|(@@ ?$)//g'  $DATA/valid/valid.$tgt > $vref
python -u $WORK_PATH/thumt/bin/trainer.py \
  --input $DATA/train/train.32k.$src.shuf $DATA/train/train.32k.$tgt.shuf \
  --vocabulary $DATA/train/vocab.32k.de-en.txt $DATA/train/vocab.32k.de-en.txt \
  --model phase1transformer \
  --validation $vinp \
  --references $vref \
  --output $MODEL_PATH \
  --parameters=device_list=[$device],train_steps=200000,batch_size=4096,log_steps=100,eval_steps=1000,keep_top_checkpoint_max=5,update_cycle=1,normalization="after",phase=1,ratio=$ratio,flip_ratio=$flip_ratio,sample_train_mode=0,sample_infer_mode=0,reuse_encoder=True  \
  --advice $DATA/train/train1.advices $DATA/valid/valid1.advices \
  --half \
  --hparam_set iwslt14deen 2>&1 | tee $MODEL_PATH/train.log.$time



# inference
for file in $MODEL_PATH/eval/model-[0-9]*.pt
do
  model=${file##*/}
  inp=$DATA/test/test.$src
  ref=$MODEL_PATH/eval/test.$tgt.debpe
  hyp=$MODEL_PATH/eval/test.$src.out.$model
  sed -r 's/(@@ )|(@@ ?$)//g'  $DATA/test/test.$tgt > $ref
  python -u $WORK_PATH/thumt/bin/translator.py \
    --models phase1transformer \
    --input $inp \
    --output $hyp \
    --vocabulary $DATA/train/vocab.32k.de-en.txt $DATA/train/vocab.32k.de-en.txt \
    --checkpoints $MODEL_PATH/eval --specific-ckpt $MODEL_PATH/eval/$model \
    --parameters=device_list=[$device],decode_batch_size=32,decode_alpha=0.6,beam_size=5,phase=1,ratio=$ratio,flip_ratio=$flip_ratio,sample_infer_mode=0,reuse_encoder=True \
    --advice $DATA/test/test1.advices 2>&1 | tee $MODEL_PATH/eval/test.log.$model.$time

  sed -r 's/(@@ )|(@@ ?$)//g'  $hyp > $hyp.debpe
  sacrebleu $ref -i $hyp.debpe -tok none -m bleu -w 4 -b > $MODEL_PATH/eval/bleu.log.$model.$time

  inp=$DATA/test/test.$src
  ref=$MODEL_PATH/eval/test.$tgt.debpe
  hyp=$MODEL_PATH/eval/test.$src.out.$model.noad
  sed -r 's/(@@ )|(@@ ?$)//g'  $DATA/test/test.$tgt > $ref
  python -u $WORK_PATH/thumt/bin/translator.py \
    --models phase1transformer \
    --input $inp \
    --output $hyp \
    --vocabulary $DATA/train/vocab.32k.de-en.txt $DATA/train/vocab.32k.de-en.txt \
    --checkpoints $MODEL_PATH/eval --specific-ckpt $MODEL_PATH/eval/$model \
    --parameters=device_list=[$device],decode_batch_size=32,decode_alpha=0.6,beam_size=5,phase=1,ratio=0,flip_ratio=$flip_ratio,sample_infer_mode=0,reuse_encoder=True \
    --advice $DATA/test/test1.advices 2>&1 | tee $MODEL_PATH/eval/test.log.$model.noad.$time

  sed -r 's/(@@ )|(@@ ?$)//g'  $hyp > $hyp.debpe
  sacrebleu $ref -i $hyp.debpe -tok none -m bleu -w 4 -b > $MODEL_PATH/eval/bleu.log.$model.noad.$time
done

