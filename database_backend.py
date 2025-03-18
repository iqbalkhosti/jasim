import csv

class Database:

    car_catalog = [] # list for storing all information about cars
    categories = [] # list for storing all possible categories
    fav_cars = [] # list for storing favourite cars of users

    # constructor
    def __init__(self):
        with open("database.csv", "r") as file:
            reader = csv.DictReader(file)
            self.catalog = [row for row in reader]
            self.categories = reader.fieldnames

    # add a new car to the catalog
    def add_car(self, car_info):
        if not car_info["Year"].isdigit():
            print("Invalid Year. Year must be a number.")
            return
        print("For bulk adding, please edit CSV directly") #$
        self.catalog.append(car_info)

    # update an existing car
    def update_car(self, car_info):
        for item in self.catalog:
            if item["ID"] == car_info["ID"]:
                item.update(car_info)
                break

    # remove an existing car
    def remove_car(self, ID):
        for item in self.catalog:
            if item["ID"] == ID:
                self.catalog.remove(item)
                break

    # checks if a specific ID exists
    def if_exist(self, ID):
        for item in self.catalog:
            if item["ID"] == ID:
                return True
        return False

    # saves the catalog back to the csv
    def save_catalog(self):
        with open("database.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.categories)
            writer.writeheader()
            writer.writerows(self.catalog)

    '''
    i REALLY didn't like the way this was working earlier, as it made stuff very hard
    I've changed it fundamentally, please read all comments, which I've made very extensive

    search is used to find specific items based on a filter
    text is all the keywords sent by the user
    relevance is used when there are no perfect matches
    '''
    def search(self, text, relevance = False):
        terms = text.lower().split() # list of all filters
        results = [] # stores all matching results

        '''
        Old code for matching results. Very hard to understand and also not very manipulable.
        TODO: Left here in case needed, however please remove if tester finds no errors.
        '''
        #results = [item for item in self.get_car_catalog() if all(any(term in str(item[category]).lower() for category in self.get_categories()) for term in terms)] if terms else self.get_car_catalog()

        for item in self.get_car_catalog():
            terms_set = {term.lower() for term in terms} # all the terms saved as a set
            values_set = {value.lower() for value in item.values()} # all values of current car saved as a set

            if (relevance == True): # in the case that there were no perfect matches, run threshold check
                threshold = (len(terms_set & values_set)) / len(terms) # decimal based on how many terms match of total terms
                if threshold >= 0.4: # must match 40% to be included, feel free to change value
                    results.append(item)
            else: # checks for perfect matches
                if terms_set.issubset(values_set): # check for subsetting
                    results.append(item)

        '''
        if results is empty by here, and the relevance check has not been done
        use recursion to run again for relevance
        otherwise do not run again
        '''
        if len(results) is 0 and relevance is False:
            results = self.search(text, True)
        return results

    # catalog getter
    def get_car_catalog(self):
        return self.catalog
    
    # categories getter
    def get_categories(self):
        return self.categories
    
    # car getter
    def get_car(self, ID):
        for item in self.catalog:
            if item["ID"] == ID:
                return item
        return None
    
  #  FOR NOW, THIS IS HERE. WE MAY WANT TO MOVE THIS TO A NEW CLASS HOWEVER
    def save_fav_car(self, make, model, year, color):
        for i in self.catalog:
            if(i.get("Make")==make and i.get("Model")==model and i.get("Year")==str(year) and i.get("Color")==color):
                
                self.fav_cars.append(i)

    def filter_fav_cars(self, input2):
        self.filtered_list = []

        for d in self.fav_cars:
            for value in d.values():
                if input2 in value:
                    self.filtered_list.append(d)

        return self.filtered_list