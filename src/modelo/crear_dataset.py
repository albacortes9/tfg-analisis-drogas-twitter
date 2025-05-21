import pandas as pd
from sqlalchemy import create_engine

conn = create_engine("mysql+mysqlconnector://root:2003@localhost/twitter_analysis")

query = """
SELECT 
    t.text,
    t.media,
    CASE WHEN ub.country_code IN ('AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'KZ', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL', 'MK', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR', 'UA', 'GB', 'XK') THEN 1 ELSE 0 END AS is_europe,
    CASE WHEN ub.country_code IN ('DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CG', 'CD', 'CI', 'DJ', 'EG', 'GQ', 'ER', 'SZ', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'KE', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MU', 'MA', 'MZ', 'NA', 'NE', 'NG', 'RW', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'TZ', 'TG', 'TN', 'UG', 'EH', 'ZM', 'ZW') THEN 1 ELSE 0 END AS is_africa,
    CASE WHEN ub.country_code IN ('AS', 'AU', 'CK', 'FJ', 'PF', 'GU', 'KI', 'MH', 'FM', 'NR', 'NC', 'NZ', 'NU', 'MP', 'PW', 'PG', 'PN', 'WS', 'SB', 'TK', 'TO', 'TV', 'VU', 'WF') THEN 1 ELSE 0 END AS is_oceania,
    CASE WHEN ub.country_code IN ('AF', 'AM', 'AZ', 'BH', 'BD', 'BT', 'BN', 'KH', 'CN', 'TL', 'IN', 'ID', 'IR', 'IQ', 'IL', 'JP', 'JO', 'KW', 'KG', 'LA', 'LB', 'MY', 'MV', 'MN', 'MM', 'NP', 'KP', 'OM', 'PK', 'PS', 'PH', 'QA', 'SA', 'SG', 'KR', 'LK', 'SY', 'TW', 'TJ', 'TH', 'TR', 'TM', 'AE', 'UZ', 'VN', 'YE') THEN 1 ELSE 0 END AS is_asia,
    CASE WHEN ub.country_code IN ('AG', 'AR', 'BS', 'BB', 'BZ', 'BO', 'BR', 'CA', 'CL', 'CO', 'CR', 'CU', 'DM', 'DO', 'EC', 'SV', 'GD', 'GT', 'GY', 'HT', 'HN', 'JM', 'MX', 'NI', 'PA', 'PY', 'PE', 'KN', 'LC', 'VC', 'SR', 'TT', 'US', 'UY', 'VE') THEN 1 ELSE 0 END AS is_america,
    CASE WHEN ub.country_code IN ('AE', 'BH', 'CY', 'EG', 'IR', 'IQ', 'IL', 'JO', 'KW', 'LB', 'OM', 'PS', 'QA', 'SA', 'SY', 'TR', 'YE') THEN 1 ELSE 0 END AS is_middle_east,
    CASE WHEN m.tweet_id IS NOT NULL THEN 1 ELSE 0 END as mention,
    CASE WHEN rt.reference_type THEN 1 ELSE 0 END AS reference,
    tm.like_count,
    tm.retweet_count,
    tm.reply_count,
    tm.quote_count,
    u.verified AS user_verified,
    u.followers_count AS user_followers,
    u.following_count AS user_following,
    u.tweet_count AS user_tweet_count,
    u.listed_count AS user_listed_count,
    CASE WHEN u.location IS NOT NULL THEN 1 ELSE 0 END AS user_location,
    CASE WHEN tw.keyword_id = 1 THEN 1 ELSE 0 END AS mentions_ghb,
    CASE WHEN tw.keyword_id = 14 THEN 1 ELSE 0 END AS mentions_ecstasy,
    CASE WHEN tw.keyword_id = 31 THEN 1 ELSE 0 END AS mentions_2cb,
    ct.classification
FROM classified_tweets ct
LEFT JOIN tweet_metrics tm ON ct.tweet_id = tm.tweet_id
LEFT JOIN tweet_keyword tw ON tw.tweet_id = ct.tweet_id
LEFT JOIN ubication ub ON ub.tweet_id = ct.tweet_id
LEFT JOIN mention m ON m.tweet_id = ct.tweet_id
LEFT JOIN referenced_tweet rt ON rt.tweet_id = ct.tweet_id
LEFT JOIN tweet t ON ct.tweet_id = t.id
LEFT JOIN user u ON t.author_id = u.id
WHERE tw.keyword_id IN (1, 14, 31)
"""
df = pd.read_sql(query, conn)

df.to_csv("dataset_final.csv", index=False)
print("Exportado como 'dataset_final.xlsl'")
