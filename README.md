# hotel-city-classifier



## Tables
Tables and fields definitions

### Missing values
All fields that can be empty are never null, as all null values have been replaced with 'NA' for varchar fields, -1 for int and float fields, 999 for coordinates fields.

### Tables IDs
All IDs are unique and are the primary key of the table. They are generated by hashing the URL of the hotel, and truncating the hash at the first 19 digits. This allows for a unique identifier of the hotel that is an integer, crucial for performance reasons. The ID is often used for join and for upsert operations, a string would be inappropriate for these operations, being way more expensive in terms of performance (memory usage, processing, time).
All the tables are indexed on the ID field, to speed up join and upsert operations.
The collision probability with the truncated hashed string is not zero, but extremely low in the context of this project.

### HOTEL
Table containing information about scraped hotels. All the info is taken from the hotel's page on the site, with the exception of the ID and the coordinates. The ID is a hash of the URL, as previously mentioned. The coordinates are retrieved from the Nominatim API, using the address of the hotel.

| Field | Datatype | Meaning |
| - | - | - |
| ID | int | Primary key, unique identifier of the hotel. Hash of hotel page URL |
| URL | varchar | URL of the hotel |
| NAME | varchar | Name of the hotel |
| ADDRESS | varchar | Address of the hotel |
| LATITUDE | float | Latitude of the hotel |
| LONGITUDE | float | Longitude of the hotel |
| ALTITUDE | float | Altitude of the hotel |
| DESCRIPTION | varchar | Description of the hotel, as read in the "About" section of the hotel page |
| RATING | float | Site rating of the hotel |
| REVIEWS | int | Site number of reviews |
| CATEGORY_RANK | varchar | Category rank of the hotel, for example "#264 of 499 hotels in New York City" or "#1 of 41 hostels in New York City" |
| STAR_RATING | float | Star rating of the hotel, as numbers of stars out of 5 |
| NEARBY_RESTAURANTS | int | Number of nearby restaurants, as per info reported inside "Location" section of the hotel's page |
| NEARBY_ATTRACTIONS | int | Number of nearby attractions, as per info reported inside "Location" section of the hotel's page |
| WALKERS_SCORE | int | Walkers score of the hotel, as per info reported inside "Location" section of the hotel's pag |
| PICTURES | int | Number of pictures on the hotel's page |
| AVERAGE_NIGHT_PRICE | int | Average night price, as per the "View prices for your travel dates" section of the hotel page |
| PRICE_RANGE_MIN | int | Minimum price range, reported at the bottom of the page. Not always present |
| PRICE_RANGE_MAX | int | Maximum price range, reported at the bottom of the page, reported at the bottom of the page. Not always present |
| PROPERTY_AMENITIES | varchar | Property amenities, for example: Wifi, Restaurant, Rooftop bar, Non-smoking hotel, Parking, etc. |
| ROOM_FEATURES | varchar | Room features, for example: Air conditioning, Safe, Hair dryer, Room service, etc. |
| ROOM_TYPES | varchar | Room types, for example: City view, Non-smoking rooms, Suites, etc. |
| LOCATION_RATING | float | Location rating, as per the "About" section |
| CLEANLINESS_RATING | float | Cleanliness rating, as per the "About" section |
| SERVICE_RATING | float | Service rating, as per the "About" section |
| VALUE_RATING | float | Value rating, as per the "About" section |
| ALSO_KNOWN_AS | varchar | Other hotel's names |
| FORMERLY_KNOWN_AS | varchar | Former hotel names |
| CITY_LOCATION | varchar | City location, as reported at the bottom of the page |
| NUMBER_OF_ROOMS | int | Number of rooms, as reported at the bottom of the page  |
| REVIEWS_SUMMARY | varchar | Summary of all the reviews made by AI, offered by the site in the "Reviews Summary" section |
| REVIEWS_KEYPOINT_LOCATION | varchar | Keypoint of the location made by AI, offered by the site in the "Reviews Summary" |
| REVIEWS_KEYPOINT_ATMOSPHERE | varchar | Keypoint of the atmosphere made by AI, offered by the site in the "Reviews Summary" |
| REVIEWS_KEYPOINT_ROOMS | varchar | Keypoint of the rooms made by AI, offered by the site in the "Reviews Summary" |
| REVIEWS_KEYPOINT_VALUE | varchar | Keypoint of the value made by AI, offered by the site in the "Reviews Summary" |
| REVIEWS_KEYPOINT_CLEANLINESS | varchar | Keypoint of the cleanliness made by AI, offered by the site in the "Reviews Summary" |
| REVIEWS_KEYPOINT_SERVICE | varchar | Keypoint of the service made by AI, offered by the site in the "Reviews Summary" |
| REVIEWS_KEYPOINT_AMENITIES | varchar | Keypoint of the amenities made by AI, offered by the site in the "Reviews Summary" |
| REVIEWS_5_EXCELLENT | int | Number of 5 points reviews (excellent) |
| REVIEWS_4_VERY_GOOD | int | Number of 4 points reviews (very good) |
| REVIEWS_3_AVERAGE | int | Number of 3 points reviews (average) |
| REVIEWS_2_POOR | int | Number of 2 points reviews (poor) |
| REVIEWS_1_TERRIBLE | int | Number of 1 points reviews (terrible) |
| REVIEWS_KEYWORDS | varchar | Keywords extracted from the reviews, shown above the reviews on the site |
| SCRAPED_TIMESTAMP | timestamp | Timestamp of scraping |
| INSERT_UPDATE_TIMESTAMP | timestamp | Timestamp of insertion or update |



### Review
Table containing information about reviews of hotels. The ID is a hash of the URL of the review, as previously mentioned. The hotel ID is a foreign key to the HOTEL table.
Reviews are scraped from hotel page (each page loads 10 reviews). Reviews in all languages are scraped. Language indication is not present in the webpage itself, so it is detected by the language detection library langdetect. The response from the hotel is not always present, so the fields are often empty. 
Date of review is scraped as month and year. Precise date of the review is not present in the hotel page, but only in the page of the review itself, that has not been scraped due to the large number of reviews (= page loads needed).
User ID is also saved, being the hash of the user's profile URL. User info are stored in another table.

| Field | Datatype | Meaning |
| - | - | - |
| ID | int | Primary key, unique identifier of the review. Hash of review page URL |
| URL | varchar | URL of the review |
| TITLE | varchar | Title of the review |
| TEXT | varchar | Text of the review | 
| RATING | int | Rating given to the hotel by the user in the review |
| MONTH_OF_REVIEW | varchar | Month of the review |
| YEAR_OF_REVIEW | int | Year of the review |
| MONTH_OF_STAY | int | Month of the stay |
| YEAR_OF_STAY | int | Year of the stay |
| LIKES | int | Number of likes of the review |
| PICS_FLAG | int | Flag for presence of pictures in the review |
| LANGUAGE | varchar | Language of the review |
| RESPONSE_FROM | varchar | Response from the hotel |
| RESPONSE_TEXT | varchar | Text of the response |
| RESPONSE_DATE | varchar | Date of the response |
| RESPONSE_LANGUAGE | varchar | Language of the response |
| USER_ID | int | User ID, foreign key to the USER table |
| HOTEL_ID | int | Hotel ID, foreign key to the HOTEL table |
| SCRAPED_TIMESTAMP | timestamp | Timestamp of scraping |
| INSERT_UPDATE_TIMESTAMP | timestamp | Timestamp of insertion or update |


### HOTEL_MAPQUEST_LOCATION
Table containing information about the location of the hotel, as retrieved from the MapQuest API. This information is additional, added in a second moment after the scraping of the hotel page, needed because of the unreliability of the Nominatim API (around 20% of missing  coordinates). In case of ambiguous addresses, the MapQuest API returns more than one result, so the table can contain more than one row for the same hotel, ranked in order of probability of the match (RANK=0 being the most probable).
The ID is a hash of the HOTEL_ID concatenated to the result RANK. The hotel ID is a foreign key to the HOTEL table.
The admin area fields are the administrative areas of the location, from the most specific to the most general.
All the fields are what's returned in the JSON by the API, with the exception of the IDs. Documentation [here](https://developer.mapquest.com/documentation/geocoding-api/address/get/).


| Field | Datatype | Meaning |
| - | - | - |
| ID | int | Primary key, unique identifier of the location. Hash of HOTEL_ID concatenated to the result RANK |
| HOTEL_ID | int | Hotel ID, foreign key to the HOTEL table |
| RANK | int | Rank of the result, 0 being the most probable |
| STREET | varchar | Street of the location |
| ADMIN_AREA_6 | varchar | Administrative area 6 |
| ADMIN_AREA_6_TYPE | varchar | Administrative area 6 type |
| ADMIN_AREA_5 | varchar | Administrative area 5 |
| ADMIN_AREA_5_TYPE | varchar | Administrative area 5 type |
| ADMIN_AREA_4 | varchar | Administrative area 4 |
| ADMIN_AREA_4_TYPE | varchar | Administrative area 4 type |
| ADMIN_AREA_3 | varchar | Administrative area 3 |
| ADMIN_AREA_3_TYPE | varchar | Administrative area 3 type |
| ADMIN_AREA_1 | varchar | Administrative area 1 |
| ADMIN_AREA_1_TYPE | varchar | Administrative area 1 type |
| POSTAL_CODE | varchar | Postal code |
| GEOCODE_QUALITY_CODE | varchar | The five character quality code for the precision of the geocoded location |
| GEOCODE_QUALITY | varchar | The precision of the geocoded location |
| DRAG_POINT | boolean | Drag point |
| SIDE_OF_STREET | varchar | Specifies the side of street. Possible values: 'L' = left; 'R' = right; 'M' = mixed; 'N' = none (default) |
| LINK_ID | varchar | Link ID |
| UNKNOWN_INPUT | varchar | Unknown input |
| TYPE | varchar | Type |
| LATITUDE | float | Latitude for routing, it is the nearest point on a road for the entrance |
| LONGITUDE | float | Longitude for routing, it is the nearest point on a road for the entrance. |
| DISPLAY_LATITUDE | float | A lat that can be helpful when showing this address as a Point of Interest |
| DISPLAY_LONGITUDE | float | A lng that can be helpful when showing this address as a Point of Interest |
| MAP_URL | varchar | Map URL |
| INSERT_UPDATE_TIMESTAMP | timestamp | Timestamp of insertion or update |
