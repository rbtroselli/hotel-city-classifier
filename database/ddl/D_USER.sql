-- drop table if exists USER
-- ;  

create table if not exists USER (
    ID int primary key,
    URL varchar,
    NAME varchar,
    NAME_SHOWN varchar,
    CONTRIBUTIONS int,
    HELPFUL_VOTES int,
    LOCATION varchar,
    SCRAPED_TIMESTAMP timestamp default current_timestamp,
    INSERT_UPDATE_TIMESTAMP timestamp default current_timestamp
);
