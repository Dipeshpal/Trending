from pytrends.request import TrendReq

pytrend = TrendReq()


def get_trending_by_region(country='India', keyword_list=None):
    pytrend.build_payload(kw_list=keyword_list)
    df = pytrend.interest_by_region()
    df = df.sort_values(by=keyword_list[0], ascending=False)
    df2 = df.loc[country]
    res = df[:5].to_dict()[keyword_list[0]]
    res[country] = df2[keyword_list[0]]
    return res


if __name__ == '__main__':
    print(get_trending_by_region(keyword_list=['Iphone Iphone']))
