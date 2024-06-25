from rouge import Rouge
import json
import evaluate

from app.summary import text_rank_summary


def calc_text_rank_score(records, summary_part=0.1):
    references, predictions, sources = [], [], []
    for news in records:
        references.append(news['summary'])
        sources.append(news['text'])
        predicted_summary = text_rank_summary(news['text'], summary_part)
        predictions.append(predicted_summary)
    # Метрика Comet
    comet_score = evaluate.load('comet')
    comet_score = comet_score.compute(predictions=predictions, references=references, sources=sources)
    print("COMET: ", comet_score)
    # Метрика Rouge
    rouge = Rouge()
    rouge_score = rouge.get_scores(predictions, references, avg=True)
    print("ROUGE: ", end='')
    for key, value in rouge_score.items():
        print(f"{key}: {value},")
    return comet_score, rouge_score


all_news = []
with open('../app/gazeta_test.jsonl', 'r', encoding='utf-8') as json_file:
    json_list = list(json_file)
for json_str in json_list[:80]:
    result = json.loads(json_str)
    all_news.append(result)
calc_text_rank_score(all_news)

