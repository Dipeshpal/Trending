import string
import os
import spacy
from string import punctuation
from collections import Counter
import pytextrank
import collections
import numpy as np
import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib import rcParams
from wordcloud import WordCloud, STOPWORDS
import re
from trends_finder import get_trending_by_region
import json
from datetime import datetime

nlp = spacy.load(r"D:\Github\Trending\venv\Lib\site-packages\en_core_web_md\en_core_web_md-3.4.1")


def get_hotwords(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN']  # 1
    doc = nlp(text.lower())  # 2
    for token in doc:
        # 3
        if token.text in nlp.Defaults.stop_words or token.text in punctuation:
            continue
        # 4
        if token.pos_ in pos_tag:
            result.append(token.text)

    return result  # 5


def preprocess(sentence):
    sentence = str(sentence)
    sentence = sentence.lower()
    sentence = sentence.replace('{html}', "")
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', sentence)
    # remove '|' from text
    rem_punc = str.maketrans('', '', string.punctuation)
    cleantext = cleantext.translate(rem_punc)

    # replace laptops to laptop using regex
    pattern = re.compile(r"laptops")
    cleantext = pattern.sub("laptop", cleantext)

    return cleantext


df = pd.read_csv("videos_2022-10-22.csv")
all_text = ' '.join(df['Title'])
all_text = preprocess(all_text)


def get_most_common_words():
    # combine all the text in the dataframe
    output = set(get_hotwords(all_text))
    most_common_list = Counter(output).most_common(10)
    li = []
    for item in most_common_list:
        li.append(item[0])
    return li


def get_ranked_phrase_with_country_rank():
    nlp.add_pipe("textrank")
    doc = nlp(all_text)
    di = {}
    li = []
    for phrase in doc._.phrases[:20]:
        if phrase.text is not None:
            try:
                # capatilize the first letter of the phrase
                search_term = phrase.text.capitalize()
                print(f"fetching trends for: {search_term}")
                trends = get_trending_by_region(keyword_list=[search_term])
                li.append((phrase.text, trends))
                for k, v in trends.items():
                    trends[k] = int(v)
                # sys.exit()
                di[phrase.text] = trends
                # li.append({phrase.text: trends})
            except Exception as e:
                print("Something went wrong: ", e)
    # li to json
    if not os.path.exists('reports'):
        os.mkdir('reports')
    today = datetime.today().strftime('%Y-%m-%d')
    if not os.path.exists(f'reports/{today}'):
        os.mkdir(f'reports/{today}')
    print(di)
    with open(f'reports/{today}/ranked_phrase.json', 'w') as f:
        json.dump(di, f, indent=4)
    return li


def create_word_cloud():
    stopwords = STOPWORDS
    wordcloud = WordCloud(stopwords=stopwords, background_color="white", max_words=1000).generate(all_text)
    rcParams['figure.figsize'] = 10, 20
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    # plt.show()

    if not os.path.exists('reports'):
        os.mkdir('reports')
    today = datetime.today().strftime('%Y-%m-%d')
    if not os.path.exists(f'reports/{today}'):
        os.mkdir(f'reports/{today}')
    wordcloud.to_file(f'reports/{today}/wordcloud.png')

    # plt.show(wordcloud)
    plt.axis("off")
    # if not os.path.exists('reports'):
    #     os.mkdir('reports')
    # today = datetime.today().strftime('%Y-%m-%d')
    # if not os.path.exists(f'reports/{today}'):
    #     os.mkdir(f'reports/{today}')
    # plt.imsave(f'reports/{today}/wordcloud.png', wordcloud)
    filtered_words = [word for word in all_text.split() if word not in stopwords]
    counted_words = collections.Counter(filtered_words)
    words = []
    counts = []
    for letter, count in counted_words.most_common(20):
        words.append(letter)
        counts.append(count)
    colors = cm.rainbow(np.linspace(0, 1, 10))
    rcParams['figure.figsize'] = 20, 10
    plt.title('Top words in the headlines vs their count')
    plt.xlabel('Count')
    plt.ylabel('Words')
    plt.barh(words, counts, color=colors)
    # plt.show()
    if not os.path.exists('reports'):
        os.mkdir('reports')
    today = datetime.today().strftime('%Y-%m-%d')
    if not os.path.exists(f'reports/{today}'):
        os.mkdir(f'reports/{today}')
    plt.savefig(f'reports/{today}/word_count.png')


def report_generation():
    print("Generating report...")
    li = get_ranked_phrase_with_country_rank()
    top_phrase = []
    if not os.path.exists('reports'):
        os.mkdir('reports')
    today = datetime.today().strftime('%Y-%m-%d')
    if not os.path.exists(f'reports/{today}'):
        os.mkdir(f'reports/{today}')
    for item in li:
        top_phrase.append(item[0])
        report_file = f'reports/{today}/report_{item[0]}.csv'
        df = pd.DataFrame.from_dict(item[1], orient='index', columns=[item[0]])
        df.to_csv(report_file)

    for filename in os.listdir('reports'):
        if filename.endswith(".csv"):
            df_temp = pd.read_csv(f'reports/{today}{filename}')
            # rename 'Unnamed: 0' to 'phrase'
            df_temp.rename(columns={'Unnamed: 0': 'country'}, inplace=True)
            # rename last column to 'rank'
            df_temp.rename(columns={df_temp.columns[-1]: 'rank'}, inplace=True)
            df_temp.to_csv(f'reports/{today}/{filename}', index=False)


def main():
    create_word_cloud()
    # get_ranked_phrase_with_country_rank()
    report_generation()


if __name__ == '__main__':
    # create_word_cloud()
    # print(get_most_common_words())
    # # print(get_ranked_phrase_with_country_rank())
    # report_generation()
    main()
