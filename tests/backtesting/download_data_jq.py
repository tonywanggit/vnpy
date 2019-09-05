import jqdatasdk as jq

jq.auth("18964819560", "efun102@JQ")
df = jq.get_price("RB1910.XSGE", start_date="2019-07-01", end_date='2019-08-01', frequency='1m', skip_paused=True)

print(df)