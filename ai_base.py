bert모델 = "bert-base-multilingual-cased"  #@param ['bert-base-multilingual-cased', 'bert-large-cased', 'bert-base-chinese']


from IPython.display import clear_output
clear_output(wait=True)


import torch

from transformers import BertTokenizer
from transformers import BertForSequenceClassification, AdamW, BertConfig
from keras.utils import pad_sequences
import numpy as np


# 디바이스 설정
if torch.cuda.is_available():
    device = torch.device("cuda")
    print('There are %d GPU(s) available.' % torch.cuda.device_count())
    print('We will use the GPU:', torch.cuda.get_device_name(0))
else:
    device = torch.device("cpu")
    print('No GPU available, using the CPU instead.')


tokenizer = BertTokenizer.from_pretrained(bert모델, do_lower_case=False)

#model_fn = 'pytorch_model.bin'
#bert_model = 'bert-base-multilingual-cased'
#model_state_dict = torch.load(model_fn)
#model = BertForSequenceClassification.from_pretrained(bert_model, state_dict = model_state_dict, num_labels = 2)
#model.bert.load_state_dict(model.bert.state_dict())
model = BertForSequenceClassification.from_pretrained("zizin_model", num_labels=2)


print('환경 설정이 완료되었습니다.')

test_text = '[속보] 태평양 남서부 바누아투서 규모 7 지진 발생 -USGS'

# 입력 데이터 변환
def convert_input_data(sentences):

    # BERT의 토크나이저로 문장을 토큰으로 분리
    tokenized_texts = [tokenizer.tokenize(sent) for sent in sentences]

    # 입력 토큰의 최대 시퀀스 길이
    MAX_LEN = 128

    # 토큰을 숫자 인덱스로 변환
    input_ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_texts]

    # 문장을 MAX_LEN 길이에 맞게 자르고, 모자란 부분을 패딩 0으로 채움
    input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

    # 어텐션 마스크 초기화
    attention_masks = []

    # 어텐션 마스크를 패딩이 아니면 1, 패딩이면 0으로 설정
    # 패딩 부분은 BERT 모델에서 어텐션을 수행하지 않아 속도 향상
    for seq in input_ids:
        seq_mask = [float(i>0) for i in seq]
        attention_masks.append(seq_mask)

    # 데이터를 파이토치의 텐서로 변환
    inputs = torch.tensor(input_ids)
    masks = torch.tensor(attention_masks)

    return inputs, masks


# 문장 테스트
def t(sentences):

    # 평가모드로 변경
    model.eval()

    # 문장을 입력 데이터로 변환
    inputs, masks = convert_input_data(sentences)

    # 데이터를 GPU에 넣음
    b_input_ids = inputs.to(device)
    b_input_mask = masks.to(device)

    # 그래디언트 계산 안함
    with torch.no_grad():
        # Forward 수행
        outputs = model(b_input_ids,
                        token_type_ids=None,
                        attention_mask=b_input_mask)

    # 로스 구함
    logits = outputs[0]

    # CPU로 데이터 이동
    logits = logits.detach().cpu().numpy()

    return logits

def is_emergency(text, modelpath = "zizin_model"):
    model = BertForSequenceClassification.from_pretrained(modelpath, num_labels=2)
    logits = t([text])
    return np.argmax(logits)
   

#print(is_emergency(test_text))    # 1 이면 재난 