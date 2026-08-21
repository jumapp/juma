
# Architecture needs to address 

## Moonsighting date
- How do I display correct moonsighting date Need to find out. Perhaps look at hilal website and scrap from backend every evening

## Super Admin Role 
- We need to build a admin portal (mobile friendly) to allow assigning roles

## Timing calculation and edits 
All begin times are calculated with location using js package and adhan and iqama times are editable 

## Masjid Edits
- For photos upload, we will use google storage, No more than 5 pics/per masjid allowed. Keep this configurable in code 
- The flow needs to capture this 
    - Without signin, user must be able to see map/list but only next salat time. To see edit salat times, he must login. 
    - We will begin with google signin. We can use firebase like functionality to provide login
- Role Assignment 
    - The user can request to become admin 
    - Admin's name must show in masjid detail
    - Masjid's muazzin/imam must be given priority to become an admin
    - The request must come to admin portal for approval 
    - The request must include Name, phone, email and designation of admin

## User search 

- Vicinity must remain 2 KM by default
- Auth session - Refresh tokens, idle timeout, re-auth on sensitive actions
- 

## UX 
- Use skeletons for empty and loading states, Use indicator for cache and online/offline modes
- Min 44px touch targets 
- Show last updated times
- Validate times before submit
- One primary action per screen design is required
- Haptic on salat-time arrival; subtle animation on next-salat change; toast on save
- Keep a prominent counter for next iqama time


## Functionality 

- We need to provide audit logs when user's 
- Use standard open source rate limiting tool 
- Urdu, RTL support needs to be provided. We will choose appropriate font
- Use i18n lib
- Use open source/freeware analytics 
- Provide option to navigate to the masjid
- Share masjid cards with salat times and link to app


    

