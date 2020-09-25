# Meal configurator

Django-powered database-driven website which allows users to browse, search for and add/edit culinary recipes. Demo hosted on heroku, static and media assets served via AWS S3.

## Key features

- Predefined ingredients allocated in various food categories for easier navigation, with additional data attached (price, caloric value, nutrition info)
- Simple form for adding new ingredients, which can be used in new recipe even before admin/moderator accept.
- Ingredient's list stored in session data, after adding all desired elements user can create new recipe taking adventage of prepopulated fields or search 
for already existing recipes containing particular ingredients. When search results are scarce, app provides partial matches.
- Page for posting recipes equipped with full-fledged WYSIWYG text editor, dynamic adding/removing form rows which exclude from options already chosen ingredients and few custom
validation methods (eg reminding user to provide explanation how to prepare omitted in description ingredients).
- Automatic calculation of recipe's macronutrients content, price and calory value, all dispalyed in regard to one serving.
- Logged in users can comment recipes.
- All posted content need to be accepted by an admin before becoming visible to other users.
- Three different modes for searching.
- Responsive design.

## Usage

Basic usage advices covered on front page with features ilustrated by screenshots. <a href="https://muconfi.herokuapp.com/">Check it out!</a>
If you have any suggestions or find a bug which need fixing, please contact me <a href="https://muconfi.herokuapp.com/contact-us/">here</a> or send an email to adress from the footer.
It's my first "serious" project in django, I built it from scratch while learning framework and other topics related to web development so it will be very helpfull to hear some opinions.




