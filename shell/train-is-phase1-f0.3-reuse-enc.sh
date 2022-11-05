WORK_PATH="/home/wangtongli/wzt/PromptNMT"
MODEL_PATH="/data/user/WzT/is_phase1.1_fratio0.3_reuse_enc"
DATA_PATH="/data/user/WzT/de_en_data"
mkdir -p $MODEL_PATH
DATA=$DATA_PATH
device=0
src=de
tgt=en
time=$(date +'%m:%d:%H:%M')




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

