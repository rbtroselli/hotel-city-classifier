-- drop table if exists REVIEW
-- ;

create table if not exists REVIEW (
    ID int primary key,
    URL varchar,
    TITLE varchar,
    TEXT varchar,
    RATING int,
    MONTH_OF_REVIEW varchar,
    YEAR_OF_REVIEW int,
    MONTH_OF_STAY int,
    YEAR_OF_STAY int,
    LIKES int,
    PICS_FLAG int,
    LANGUAGE varchar,
    RESPONSE_FROM varchar,
    RESPONSE_TEXT varchar,
    RESPONSE_DATE varchar,
    RESPONSE_LANGUAGE varchar,
    USER_ID int,
    HOTEL_ID int,    s
    SCRAPED_TIMESTAMP timestamp default current_timestamp,
    INSERT_UPDATE_TIMESTAMP timestamp default current_timestamp
);

-- update result 
-- set REVIEWS_SCRAPED_FLAG = false 
-- where REVIEWS_SCRAPED_FLAG is true
-- ;