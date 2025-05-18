import pandas as pd
from sqlalchemy import create_engine

conn = create_engine("mysql+mysqlconnector://root:2003@localhost/twitter_analysis")

query = """
SELECT 
	ct.tweet_id,
    t.text,
    tm.like_count,
    tm.retweet_count,
    tm.reply_count,
    tm.quote_count,
    u.verified AS user_verified,
    u.username,
    u.followers_count AS user_followers,
    u.following_count AS user_following,
    u.tweet_count AS user_tweet_count,
    u.listed_count AS user_listed_count,
    u.location AS user_location,
    CASE WHEN tw.keyword_id = 1 THEN 1 ELSE 0 END AS mentions_ghb,
    CASE WHEN tw.keyword_id = 14 THEN 1 ELSE 0 END AS mentions_ecstasy,
    CASE WHEN tw.keyword_id = 31 THEN 1 ELSE 0 END AS mentions_2cb,
    ct.classification
FROM classified_tweets ct
LEFT JOIN tweet_metrics tm ON ct.tweet_id = tm.tweet_id
LEFT JOIN tweet_keyword tw ON tw.tweet_id = ct.tweet_id
LEFT JOIN tweet t ON ct.tweet_id = t.id
LEFT JOIN user u ON t.author_id = u.id
WHERE tw.keyword_id IN (1, 14, 31)
"""
df = pd.read_sql(query, conn)

df.to_csv("dataset_final.csv", index=False)
print("Exportado como 'dataset_final.csv'")
