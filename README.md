# Logic Website

## Description

Website that allows users to create arguments and share them with others.
The arguments should be structured and formatted uniformly somehow.

### Goal

Have arguments entered by users with evidence/sources for each premise.
The conclusions can then be turned into predictions on real future events.
Those predictions need to somehow be verified with evidence.
This should result in a score for the user or the theory (weighted by the amount of predictions are made).

The score should be a measure of how well the user/theory is able to predict the future.
The highest weighted arguments/theories might then be used as fine tune training data for a language model.
The trained model could then be used to automatically sift through new arguments added by users and point out contradictions.
The AI model should of course have a score as well by predicting on future events.

## Issues
### CSRF
If I pass the CSRF token in the header of the body with hx-headers, it doesn't work after I log in (for logout).
Likely because logout refreshes the CSRF token, but the hx-headers doesn't update it for the logout request.
If i pass the CSRF token for every POST request in the hx-header separately, it works.
Probably works, because the logout button gets sent after logging in and now the more recent CSRF token is used for the logout request.
But this is not how it should work, I feel like.
The hx-headers from the body should propagate to all the elements and have the correct CSRF token.


## Guidelines

### Single page app vs "traditional"
When to use href + hx-boost:
- When you want the url to change, so a decent change in the page.

When to use hx-get:
- When you want to get data from the server and update the page with it.

This can get confusing.
If you want to select a different article in a small box, one could just use hx-get.
But a user might want to share the link to the page with that article, so href + hx-boost might be better.
