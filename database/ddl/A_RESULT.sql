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
    HOTEL_PAGE_MISSING_FLAG boolean default false,
    REVIEWS_SCRAPED_FLAG boolean default false,
    SCRAPED_TIMESTAMP timestamp default current_timestamp,
    INSERT_UPDATE_TIMESTAMP timestamp default current_timestamp
);

-- Missing hotel pages
update RESULT 
set HOTEL_PAGE_MISSING_FLAG = true 
where ID in (
    125499925038129775, 
    770026166187754581, 
    339691035998003708, 
    412576628361762944, 
    536178787309584515, 
    774820806311376200,
    114624814134122254,
    595268186930335958,
    53979305761493616,
    478870186275597606,
    569788813951343479,
    107546456573295582,
    441610308509094550,
    129414200016925038,
    563112637774334071,
    452984373842223311
);