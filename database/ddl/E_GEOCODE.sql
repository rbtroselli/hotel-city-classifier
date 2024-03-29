-- drop table if exists HOTEL_MAPQUEST_LOCATION
-- ;

create table if not exists HOTEL_MAPQUEST_LOCATION (
    ID int primary key,
    HOTEL_ID int,
    RANK int,
    STREET varchar,
    ADMIN_AREA_6 varchar,
    ADMIN_AREA_6_TYPE varchar,
    ADMIN_AREA_5 varchar,
    ADMIN_AREA_5_TYPE varchar,
    ADMIN_AREA_4 varchar,
    ADMIN_AREA_4_TYPE varchar,
    ADMIN_AREA_3 varchar,
    ADMIN_AREA_3_TYPE varchar,
    ADMIN_AREA_1 varchar,
    ADMIN_AREA_1_TYPE varchar,
    POSTAL_CODE varchar,
    GEOCODE_QUALITY_CODE varchar,
    GEOCODE_QUALITY varchar,
    DRAG_POINT boolean,
    SIDE_OF_STREET varchar,
    LINK_ID varchar,
    UNKNOWN_INPUT varchar,
    TYPE varchar,
    LATITUDE float,
    LONGITUDE float,
    DISPLAY_LATITUDE float,
    DISPLAY_LONGITUDE float,
    MAP_URL varchar,
    INSERT_UPDATE_TIMESTAMP timestamp default current_timestamp
);

-- drop table if exists HOTEL_MAPQUEST_RESPONSE
-- ;

create table if not exists HOTEL_MAPQUEST_RESPONSE (
    HOTEL_ID int primary key,
    RESPONSE_RAW varchar,
    INSERT_UPDATE_TIMESTAMP timestamp default current_timestamp
);