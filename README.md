# ToryTrackerAlexa
Tory Tracker (short for Inventory Tracker) is a custom Alexa skill that helps with managing the frozen meals found in the inventory fridges at Meals On Wheels and More, a non profit
organization that delivers meals to vulnerable people (i.e. seniors, people recovering from illnesses).

Tory Tracker uses DynamoDB to manage the quantity of items in inventory, all items found on the database are from the Apetito menu (Apetito is Meals On Wheels' supplier)
Tory Tracker can update the quantity of items in the inventory database, either removing or adding, and query the quantity of a specific item.

## Usage
**"item"** refers to a menu item found on the [apetito menu](https://www.dropbox.com/s/cxzpxhirt6ftk3m/2019-20%20MOW%20Order%20Form.pdf?dl=0). The item's name is displayed on the food packaging
###  Query the Quantity of an Item
**You can ask:**
* Alexa, ask Tory Tracker are there “item”
* Alexa, ask Tory Tracker is there “item”
* Alexa, ask Tory Tracker how many “item” do we have

### Removing an Item
**You can ask:**
* Alexa, tell Tory Tracker to remove “item”
* Alexa, tell Tory Tracker to delete “item”

**Alexa will reply with:**
* “How many do you want to remove from the inventory list?”

**You can reply with a number:**
* “Seven”

### Adding an Item
**You can ask:**
* Alexa, tell Tory Tracker to add “item”
* Alexa, tell Tory Tracker there are “item”
* Alexa, tell Tory Tracker there is “item”

**Alexa will reply with:**
* “How many do you want to add to the inventory list?”

**You can reply with a number:**
* “Seven”

## Database setup
The DynamodDB database contains several tables, each table contain's a certain food group (i.e. pork, beef, poultry, soup). In order to query the database, you need to provide a partition key and a sort key. The partition key is the main item found on the food packaging (i.e. meatballs, fish, chicken) and the sort key is another item on the food's packaging (i.e. cheddar, squash) that creates a distinct pair (basically the primary key). This system ensure that Tory Tracker can understand the user as the input only needs to contain the 2 key words.
![dynamoDBtable](/db.png)
## Project Status
2020-08-13
Tory Tracker was tested for a week at Meals on Wheels North York on an Amazon Dot.
Tory Tracker was able to process the manjority of the request, however, users had to repeat their request a couple times as Tory Tracker
Minor issues with the speech to text. Tory Tracker could not correctly process certain words including "herbed fish" and "shepherd's pie".
The accuracy of Tory Tracker's database was not the best. Since this system relies on all the staff/volunteers at Meals on Wheels to participate in the use of Tory Tracker when adding or removing something from the inventory, Tory Tracker is unable to keep accurate records of the inventory's contents.  

2020-08-20
Fixed the bug with the incorrect processing of words with suffixes (i.e. ''s', 'ed') by changing the search keys used in the database
