-- drop table if exists RESULT
-- ;

create table if not exists RESULT (
    ID int primary key,
    RATING float,
    REVIEWS int,
    URL varchar,
    PAGE int,
    RANK int,
    HOTEL_SCRAPED_FLAG boolean default false,
    HOTEL_GEOCODED_FLAG boolean default false,
    REVIEWS_SCRAPED_FLAG boolean default false,
    SCRAPED_TIMESTAMP timestamp default current_timestamp,
    INSERT_UPDATE_TIMESTAMP timestamp default current_timestamp
);
