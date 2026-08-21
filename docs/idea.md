# DoonJuma

Jumapp, is a project which will help users to see the nearest masjid to his location and salat times of the masjid. In addition to it he will be able to see all masjids in the vicinity and their respective salat times as well.

---

## Features

### General Flow

*   Get user's current location.
*   Based on his current location or saved location or last known location (in this order)
*   Get the list of masjids in the vicinity
    * Masjid details 
    ``` text
        Masjid name 
        Indian standard address details including pre poplated state (Include only Uttarakhand as of now, we will use others later)
        Calculated latitude and lonigitude
        
        Transportation
            Accessible by public transport
            Highway masjid
            On Road masjid
        
        Map ID, if applicable
        Photos
        
        Salats
            Five time salats 
            Juma time 
            Women's salat place
            Library
        Programs 
            Maktab 
            Elders maktab
            tafseer ( day/time) multiple time schedule is possible in a day/week
            hadith lesson (day/time) multiple time schedule is possible in a day/week
            Other courses/programs
        Open/Close times
        Amenities 
            Wudu stations 
            Urinals
            Toilets
        Parking
            Masjid parking
            Street Parking
        Any other items?
    ```

*   Display the masjids on the app in a map view
*   Alternatively, User must be able to see the masjid list
*   User must be able to search, sort, and filter the masjids on map and list
*   Privilidged user must be able to add the masjid and modify the namaz timings
    * Two priviliged users, superadmin and masjid admin

### Date and Location

*   User must be able to see the location detail on dashboard like `Doiwala`
*   User must be able to see the date
*   User must be able to see the moonsighting commitee date from trusted source

### Salat timing calculations

We need to use a proven js file like adhan.js etc for salat timing calculation and provide all knobs for changing the settings (on UI settings page) like `calculation method` and `asr juristic method` etc.  
By default we need to have following settings

### Functionalities required

*   The app must show the time when offline using the cache
*   Provide Social login with username, password and Google Sign in
*   By default new created user must be a `user` role
*   Only privilidge user can assign following roles
    *   Masjid Editor
        *   Must be able to edit masjid details including time
    *   Salat Editor
        *   Must be able to edit the salat times only
        *   User must be able to make request to admin for becoming salat editor
    *   Salat time change history must be recorded
*   The next time salat should be highlighted
*   On Juma day, Juma time (Khutbah, Iqama) time must be shown and bolded
*   On Masjid detail page, All salat time must be shown
*   Masjid amenities like Parking, Toilet, Urinals must be shown on UI
*   Public Transporttaccess column must be provide,so that people know how can someone reach the masjid easily
*   Allow photos to be uploaded for each masjid with proper access

> `Make Hanafi settings for Dehradun city`

---

### Technical Stack

#### Frontend

*   React Native for iOS
*   React Native for Android
*   React Native with Expo for web
*   PWA App for desktop

#### Map

**Leaflet.js**

##### Tasks for map

*   Need to find out if leaflet.js can work on React Native
*   Integrate Leaflet.js to project

#### Database

**Neon Database**

##### Tasks for database

*   Neon DB for Database with geospatial queries
*   Find which libraries can we use for geospatial queries
*   Which ORM shall we select
*   We need to deploy frontend and backend on `Google Cloud Run` so need to check all constraints like long running tasks etc. can comfortably run on `GCR`