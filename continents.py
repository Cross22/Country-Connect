import pygame
import string
import config

BIG = 0.9
MED = 0.75
SMALL = 0.5
TINY = 0.3

class NoSuchCountry(Exception):
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)
    
class NoSuchOcean(Exception):
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)    
    
class IntegrityProblem(Exception):
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)    
    
class Country(object):
    
    def __init__(self, coord, name, size, color, borders, oceans):
        self.name = name
        self.machine_name = string.lower(string.replace(name, ' ', '-'))         
        self.size = size
        self.color = color
        self.borders = borders
        self.oceans = oceans
        self.price = 10 * (len(self.borders) + len(self.oceans))
        self.number = 1;    #Number of this country to put in a deck
        
        #coord is a coordinate inside this country on a map of this country's continent resized to dimensions 1000x1000
        self.scale_factor = (float(config.map_size[0]) / 1000.)
        coord_x = coord[0] * self.scale_factor  
        coord_y = coord[1] * self.scale_factor
        self.coord = (int(coord_x), int(coord_y))
        if coord_x > config.map_size[0] or coord_y > config.map_size[1]:
            raise Exception("The coordinates for " + str(self) + " " + str(self.coord) + " don't seem to be right. They don't fit on the map.")        
    
    def load_image(self, dir):
        image_file = dir + '/' + self.machine_name + '.png'
#        print image_file
        self.image = pygame.image.load(image_file).convert_alpha()
        #Correct Color
        if self.color:
            try:
                image_pixel_array = pygame.PixelArray(self.image)                
                if self.color == config.COLOR1:
                    image_pixel_array.replace(config.GRAY1, self.color)
                elif self.color == config.COLOR2:
                    image_pixel_array.replace(config.GRAY2, self.color)
                elif self.color == config.COLOR3:
                    image_pixel_array.replace(config.GRAY3, self.color)
                elif self.color == config.COLOR4:
                    image_pixel_array.replace(config.GRAY4, self.color)
                elif self.color == config.COLOR5:
                    image_pixel_array.replace(config.GRAY5, self.color)
            except:
                pass
                              
        
    def __repr__(self):
        return str(self.name)    

class Ocean(object):
    
    def __init__(self, coord, name, number, borders):
        self.name = name
        self.number = number    #Number of this ocean to put in a deck
        self.borders = borders
        self.coord = coord
 
        image_file = 'assets/images/transport/ship.png'
        self.card_image = pygame.image.load(image_file).convert_alpha()
 
        self.scale_factor = (float(config.map_size[0]) / 1000.)    
        coord_x = coord[0] * self.scale_factor
        coord_y = coord[1] * self.scale_factor
        self.coord = (int(coord_x), int(coord_y)) 
        if coord_x > config.map_size[0] or coord_y > config.map_size[1]:
            raise Exception("The coordinates for " + str(self) + " " + str(self.coord) + " don't seem to be right. They don't fit on the map.")
                
        
    def __repr__(self):
        return str(self.name)        

class Continent(object):
    
    def __init__(self, name, countries, oceans):
        self.name = name
        self.countries = countries
        self.oceans = oceans
        self.machine_name = string.lower(string.replace(self.name, ' ', '-')) 
        self.colors = [config.COLOR1, config.COLOR2, config.COLOR3, config.COLOR4, config.COLOR5]
        self.size = len(self.countries)
        
        self.load_map_image()
        self.load_country_images()
        
    def load_map_image(self):
        map_file = 'assets/images/continents/' + self.machine_name + '.png'
        text_image_file = 'assets/images/continents/' + self.machine_name + '_text.png'   
        self.map_image = pygame.image.load(map_file).convert_alpha()
        self.map_text = pygame.image.load(text_image_file).convert_alpha() 
        
        image_pixel_array = pygame.PixelArray(self.map_image)    
        image_pixel_array.replace(config.GRAY1, config.COLOR1)
        image_pixel_array.replace(config.GRAY2, config.COLOR2)
        image_pixel_array.replace(config.GRAY3, config.COLOR3)
        image_pixel_array.replace(config.GRAY4, config.COLOR4)
        image_pixel_array.replace(config.GRAY5, config.COLOR5) 
        image_pixel_array.replace(config.MAGENTA_OB, config.OB_COLOR)    
        image_pixel_array.replace(config.CREAM_OB, config.OB_COLOR)          
        
        self.map_image = pygame.transform.smoothscale(self.map_image, config.map_size)              
    
    def load_country_images(self):
        for country in self.countries:
            dir = "assets/images/countries/" + self.machine_name
            country.load_image(dir)
       
    def __repr__(self):
        return str(self.countries)      
        
    #Return the country with the given name
    def get_country(self, name):
        for country in self.countries:
            if country.name == name:
                return country
        #return False
        raise NoSuchCountry('No such country as ' + name + ' in ' + self.name)
    
    #Return the ocean with the given name
    def get_ocean(self, name):
        for ocean in self.oceans:
            if ocean.name == name:
                return ocean
        #return False
        raise NoSuchOcean('No such ocean as ' + name + ' in ' + self.name)    
    
    #Tests the country connections and ocean within this continent to make sure they match up
    def test_integrity(self):
        #Test country borders
        print '******************************'
        print 'Checking country borders...'
        print '******************************'
        for country in self.countries:
            for border_name in country.borders:
                bordering_country = self.get_country(border_name)
                for bordering_country_border_name in bordering_country.borders:
                    if bordering_country_border_name == country.name:  
                        match_found = True
                if match_found:
                    print 'Checked: ' + country.name + ' - ' + bordering_country.name
                    match_found = False
                    continue
                else:
                    raise IntegrityProblem(country.name + ' borders ' + bordering_country.name + ', but there is such border indicated in ' + bordering_country.name)
                
        #Test ocean borders, ocean-side
        print '******************************'
        print 'Checking oceans, ocean-side...'
        print '******************************'
        for ocean in self.oceans:
            for border_name in ocean.borders:
                bordering_country = self.get_country(border_name)
                for bordering_country_ocean_name in bordering_country.oceans:
                    if bordering_country_ocean_name == ocean.name:  
                        match_found = True 
                if match_found:
                    print 'Checked: ' + ocean.name + ' - ' + bordering_country.name
                    match_found = False
                    continue
                else:
                    raise IntegrityProblem(ocean.name + ' borders ' + bordering_country.name + ', but there is such ocean indicated in ' + bordering_country.name)

        #Test ocean borders, country-side
        print '******************************'
        print 'Checking oceans, country-side...'  
        print '******************************'      
        for country in self.countries:
            for ocean_name in country.oceans:
                bordering_ocean = self.get_ocean(ocean_name)
                for bordering_ocean_country_name in bordering_ocean.borders:
                    if bordering_ocean_country_name == country.name:  
                        match_found = True
                if match_found:
                    print 'Checked: ' + country.name + ' - ' + bordering_ocean.name
                    match_found = False
                    continue
                else:
                    raise IntegrityProblem(country.name + ' borders ' + bordering_ocean.name + ', but there is such border indicated in ' + bordering_ocean.name)                

        print '******************************'
        print 'Finished ' + self.name + ': everything is good!'
        print '******************************'
        raw_input("Press any key to continue")
                                                                    
class Europe(Continent):
    
    def __init__(self):
        
        name = 'Europe'
        countries = []
        oceans = []
        
        color = config.COLOR5;
        countries.append(Country((535,664), "Austria", MED, color, ["Switzerland", "Germany", "Czech Republic", "Slovakia", "Hungary", "Slovenia", "Italy"], []))
        countries.append(Country((170,840), "Spain", BIG, color, ["Portugal", "France"], ["Med", "Atlantic"]))
        countries.append(Country((365,586), "Belgium", SMALL, color, ["France", "The Netherlands", "Luxemburg", "Germany"], ["Atlantic"]))
        countries.append(Country((703,865), "Greece", BIG, color, ["Albania", "Macedonia", "Bulgaria", "Turkey"], ["Med"]))
        countries.append(Country((736,679), "Romania", BIG, color, ["Bulgaria", "Serbia", "Hungary", "Ukraine", "Moldova"], []))        
        countries.append(Country((745,473), "Belarus", BIG, color, ["Ukraine", "Poland", "Lithuania", "Latvia", "Russia"], []))
        countries.append(Country((194,455), "Northern Ireland", SMALL, color, ["Ireland"], ["Atlantic"]))
        countries.append(Country((660,230), "Finland", BIG, color, ["Russia", "Sweden", "Norway"], ["Baltic"]))
        countries.append(Country((643,790), "Montenegro", SMALL, color, ["Bosnia & Herzegovina", "Serbia", "Albania"], ["Med"])) 
        
        color = config.COLOR4;
        countries.append(Country((317,685), "France", BIG, color, ["Spain", "Belgium", "Luxemburg", "Germany", "Switzerland", "Italy"], ["Med", "Atlantic"]))
        countries.append(Country((514,250), "Sweden", BIG, color, ["Finland", "Norway"], ["Baltic", "Atlantic"]))
        countries.append(Country((544,613), "Czech Republic", MED, color, ["Germany", "Poland", "Slovakia", "Austria"], []))
        countries.append(Country((540,710), "Slovenia", SMALL, color, ["Italy", "Austria", "Hungary", "Croatia"], ["Med"]))
        countries.append(Country((673,760), "Serbia", MED, color, ["Bosnia & Herzegovina", "Croatia", "Hungary", "Romania", "Bulgaria", "Macedonia", "Albania", "Montenegro"], []))
        countries.append(Country((820,565), "Ukraine", BIG, color, ["Romania", "Moldova", "Hungary", "Slovakia", "Poland", "Belarus", "Russia"], []))
        countries.append(Country((667,443), "Lithuania", MED, color, ["Poland", "Belarus", "Latvia"], ["Baltic"]))
        countries.append(Country((248,410), "Scotland", MED, color, ["England"], ["Atlantic"]))
        
        color = config.COLOR3;
        countries.append(Country((68, 850), "Portugal", MED, color, ["Spain"], ["Atlantic"]))
        countries.append(Country((458,580), "Germany", BIG, color, ["Switzerland", "Luxemburg", "Belgium", "France", "The Netherlands", "Denmark", "Poland", "Czech Republic", "Austria"], ["Atlantic", "Baltic"]))
        countries.append(Country((269,526), "England", MED, color, ["Wales", "Scotland"], ["Atlantic"]))
        countries.append(Country((628,679), "Hungary", MED, color, ["Croatia", "Slovenia", "Austria", "Slovakia", "Ukraine", "Romania", "Serbia"], []))
        countries.append(Country((610,760), "Bosnia & Herzegovina", MED, color, ["Croatia", "Serbia", "Montenegro"], ["Med"]))
        countries.append(Country((763,775), "Bulgaria", MED, color, ["Turkey", "Greece", "Macedonia", "Serbia", "Romania"], []))
        countries.append(Country((925,290), "Russia", BIG, color, ["Finland", "Estonia", "Latvia", "Belarus", "Ukraine", "Norway"], ["Baltic", "Atlantic"]))
        
        color = config.COLOR2;
        countries.append(Country((925,830), "Turkey", BIG, color, ["Greece", "Bulgaria"], ["Med"]))  
        countries.append(Country((640,790), "Macedonia", SMALL, color, ["Greece", "Albania", "Serbia", "Bulgaria"], []))
        countries.append(Country((500,790), "Italy", BIG, color, ["France", "Switzerland", "Austria", "Slovenia"], ["Med"]))
        countries.append(Country((386,613), "Luxemburg", TINY, color, ["France", "Belgium", "Germany"], []))
        countries.append(Country((167,490), "Ireland", MED, color, ["Northern Ireland"], ["Atlantic"]))
        countries.append(Country((443,450), "Denmark", MED, color, ["Germany"], ["Baltic", "Atlantic"]))
        countries.append(Country((680,353), "Estonia", SMALL, color, ["Russia", "Latvia"], ["Baltic"]))   
        countries.append(Country((616,547), "Poland", BIG, color, ["Belarus", "Ukraine", "Slovakia", "Czech Republic", "Germany", "Lithuania"], ["Baltic"]))
        countries.append(Country((796,637), "Moldova", SMALL, color, ["Ukraine", "Romania"], [])) 
        
        color = config.COLOR1;
        countries.append(Country((420,685), "Switzerland", SMALL, color, ["Italy", "France", "Germany", "Austria"], []))  
        countries.append(Country((385,538), "The Netherlands", MED, color, ["Belgium", "Germany"], ["Atlantic"]))
        countries.append(Country((230,520), "Wales", SMALL, color, ["England"], ["Atlantic"]))
        countries.append(Country((445,300), "Norway", BIG, color, ["Sweden", "Finland", "Russia"], ["Atlantic"]))
        countries.append(Country((690,398), "Latvia", MED, color, ["Estonia", "Russia", "Lithuania", "Belarus"], ["Baltic"]))
        countries.append(Country((622,628), "Slovakia", MED, color, ["Hungary", "Austria", "Czech Republic", "Poland", "Ukraine"], []))
        countries.append(Country((667,838), "Albania", SMALL, color, ["Greece", "Macedonia", "Serbia", "Montenegro"], ["Med"]))   
        countries.append(Country((575,710), "Croatia", MED, color, ["Bosnia & Herzegovina", "Serbia", "Hungary", "Slovenia"], ["Med"]))                 
        
        #Oceans
        oceans.append(Ocean((106,594), "Atlantic", 3, ["Sweden", "Russia", "Norway", "Denmark", "Germany", "The Netherlands", "Belgium", "France", "England", "Scotland", "Northern Ireland", "Ireland", "Wales", "Spain", "Portugal"]))
        oceans.append(Ocean((592,380), "Baltic", 1, ["Sweden", "Finland", "Russia", "Estonia", "Latvia", "Lithuania", "Poland", "Germany", "Denmark"]))
        oceans.append(Ocean((654,930), "Med", 2, ["Turkey", "Greece", "Albania", "Montenegro", "Bosnia & Herzegovina", "Croatia", "Slovenia", "Italy", "France", "Spain"]))
        
        # Call the base class constructor
        Continent.__init__(self, name, countries, oceans)     
        

class Africa(Continent):
    
    def __init__(self):

        name = 'Africa'
        countries = []
        oceans = []
        
        color = config.COLOR1;
        countries.append(Country((422,104), "Tunisia", SMALL, color, ["Libya", "Algeria"], ["Med"]))     
        countries.append(Country((648,188), "Egypt", MED, color, ["Libya", "Sudan"], ["Med", "Indian"]))
        countries.append(Country((422,315), "Niger", BIG, color, ["Algeria", "Mali", "Burkina Faso", "Benin", "Nigeria", "Chad", "Libya"], []))
        countries.append(Country((150,352), "Senegal", SMALL, color, ["Mauritania", "Mali", "Guinea"], ["Atlantic"]))
        countries.append(Country((450,544), "Gabon", SMALL, color, ["Cameroon", "Congo"], ["Atlantic"]))
        countries.append(Country((695,515), "Uganda", SMALL, color, ["Sudan", "DROT Congo", "Rwanda", "Tanzania", "Kenya"], []))
        countries.append(Country((625,722), "Zambia", MED, color, ["Angola", "Namibia", "DROT Congo", "Botswana", "Zimbabwe", "Mozambique", "Tanzania"], []))
        countries.append(Country((845,782), "Madagascar", BIG, color, [], ["Indian"]))

        color = config.COLOR2;
        countries.append(Country((515,185), "Libya", BIG, color, ["Tunisia", "Algeria", "Niger", "Chad", "Sudan", "Egypt"], ["Med"]))     
        countries.append(Country((212,158), "Morocco", MED, color, ["Algeria", "Mauritania"], ["Med", "Atlantic"]))
        countries.append(Country((196,398), "Guinea", SMALL, color, ["Senegal", "Sierra Leone", "Liberia", "Ivory Coast", "Mali",], ["Atlantic"]))
        countries.append(Country((324,420), "Togo", SMALL, color, ["Ghana", "Burkina Faso", "Benin"], ["Atlantic"]))
        countries.append(Country((458,478), "Cameroon", MED, color, ["Nigeria", "Chad", "Central African Republic", "Congo", "Gabon",], ["Atlantic"]))
        countries.append(Country((878,414), "Somalia", MED, color, ["Ethiopia", "Kenya"], ["Indian"]))
        countries.append(Country((586,566), "DROT Congo", BIG, color, ["Sudan", "Central African Republic", "Congo", "Angola", "Zambia", "Tanzania", "Rwanda", "Uganda",], ["Atlantic"]))
        countries.append(Country((590,825), "Botswana", MED, color, ["Zambia", "Namibia", "South Africa", "Zimbabwe"], []))

        color = config.COLOR3;
        countries.append(Country((342,176), "Algeria", BIG, color, ["Tunisia", "Libya", "Niger", "Mali", "Mauritania", "Morocco"], ["Med"]))     
        countries.append(Country((252,434), "Ivory Coast", SMALL, color, ["Liberia", "Guinea", "Mali", "Burkina Faso", "Ghana"], ["Atlantic"]))
        countries.append(Country((526,326), "Chad", BIG, color, ["Libya", "Niger", "Nigeria", "Cameroon", "Central African Republic", "Sudan"], []))
        countries.append(Country((772,422), "Ethiopia", BIG, color, ["Eritrea", "Sudan", "Kenya", "Somalia"], ["Indian"]))
        countries.append(Country((656,570), "Rwanda", SMALL, color, ["Tanzania", "DROT Congo", "Uganda"], []))
        countries.append(Country((718,752), "Mozambique", BIG, color, ["Tanzania", "Zambia", "South Africa", "Zimbabwe"], ["Indian"]))
        countries.append(Country((508,825), "Namibia", BIG, color, ["Angola", "Zambia", "Botswana", "South Africa"], ["Atlantic"]))
        countries.append(Country((340,405), "Benin", BIG, color, ["Nigeria", "Niger", "Burkina Faso", "Togo"], ["Atlantic"]))
        
        color = config.COLOR4;
        countries.append(Country((198,282), "Mauritania", BIG, color, ["Morocco", "Algeria", "Mali", "Senegal"], ["Atlantic"]))     
        countries.append(Country((208,456), "Liberia", SMALL, color, ["Sierra Leone", "Guinea", "Ivory Coast"], ["Atlantic"]))
        countries.append(Country((295,372), "Burkina Faso", SMALL, color, ["Mali", "Ivory Coast", "Ghana", "Togo", "Benin", "Niger"], []))
        countries.append(Country((408,418), "Nigeria", MED, color, ["Benin", "Niger", "Chad", "Cameroon"], ["Atlantic"]))
        countries.append(Country((648,352), "Sudan", BIG, color, ["Egypt", "Libya", "Chad", "Central African Republic", "Kenya", "DROT Congo", "Uganda", "Ethiopia", "Eritrea"], ["Indian"]))
        countries.append(Country((495,550), "Congo", MED, color, ["Gabon", "Cameroon", "Central African Republic", "DROT Congo"], ["Atlantic"]))
        countries.append(Country((715,620), "Tanzania", BIG, color, ["Kenya", "Uganda", "Rwanda", "DROT Congo", "Zambia", "Mozambique"], ["Indian"]))
        countries.append(Country((590,922), "South Africa", BIG, color, ["Namibia", "Botswana", "Zimbabwe", "Mozambique"], ["Atlantic", "Indian"]))

        color = config.COLOR5;
        countries.append(Country((288,320), "Mali", BIG, color, ["Algeria", "Mauritania", "Senegal", "Guinea", "Ivory Coast", "Burkina Faso", "Niger", "Algeria"], []))     
        countries.append(Country((182,424), "Sierra Leone", SMALL, color, ["Guinea", "Liberia"], ["Atlantic"]))
        countries.append(Country((302,434), "Ghana", SMALL, color, ["Ivory Coast", "Burkina Faso", "Togo"], ["Atlantic"]))
        countries.append(Country((750,330), "Eritrea", SMALL, color, ["Sudan", "Ethiopia"], ["Indian"]))
        countries.append(Country((550,448), "Central African Republic", MED, color, ["Chad", "Sudan", "DROT Congo", "Congo", "Cameroon"], []))
        countries.append(Country((748,530), "Kenya", MED, color, ["Somalia", "Ethiopia", "Sudan", "Uganda", "Tanzania"], ["Indian"]))
        countries.append(Country((518,702), "Angola", BIG, color, ["DROT Congo", "Zambia", "Namibia"], ["Atlantic"]))
        countries.append(Country((654,782), "Zimbabwe", MED, color, ["Zambia", "Mozambique", "South Africa", "Botswana"], []))
        
        #Oceans
        oceans.append(Ocean((200,658), "Atlantic", 3, ["Morocco", "Mauritania", "Senegal", "Guinea", "Sierra Leone", "Liberia", "Ivory Coast", "Ghana", "Togo", "Benin", "Nigeria", "Cameroon", "Gabon", "Congo", "DROT Congo", "Angola", "Namibia", "South Africa"]))
        oceans.append(Ocean((938,542), "Indian", 1, ["South Africa", "Mozambique", "Madagascar", "Tanzania", "Kenya", "Somalia", "Ethiopia", "Eritrea", "Sudan", "Egypt"]))
        oceans.append(Ocean((544,52), "Med", 2, ["Egypt", "Libya", "Tunisia", "Algeria", "Morocco"]))
        
        # Call the base class constructor
        Continent.__init__(self, name, countries, oceans)   
        
class USA(Continent):
    
    def __init__(self):

        name = 'USA'
        countries = []
        oceans = []
        
        color = config.COLOR1;
        countries.append(Country((140,224), "Washington", BIG, color, ["Oregon", "Idaho"], ["Pacific"])) 
        countries.append(Country((196,556), "Arizona", BIG, color, ["California", "Nevada", "Utah", "Colorado", "New Mexico"], []))
        countries.append(Country((456,508), "Kansas", BIG, color, ["Nebraska", "Colorado", "Oklahoma", "Missouri"], []))
        countries.append(Country((608,372), "Wisconsin", MED, color, ["Minnesota", "Michigan", "Illinois", "Iowa"], []))
        countries.append(Country((736,468), "Ohio", MED, color, ["Michigan", "Indiana", "Kentucky", "West Virginia", "Pennsylvania"], []))
        countries.append(Country((564,604), "Arkansas", MED, color, ["Missouri", "Oklahoma", "Texas", "Louisiana", "Mississippi", "Tennesee"], []))
        countries.append(Country((816,568), "North Carolina", MED, color, ["Virginia", "Tennesee", "Georgia", "South Carolina"], ["Atlantic"]))
        countries.append(Country((874,490), "Delaware", TINY, color, ["New Jersey", "Pennsylvania", "Maryland"], ["Atlantic"]))
        countries.append(Country((923,407), "Rhode Island", TINY, color, ["Massachusettes", "Connecticut"], ["Atlantic"]))

        color = config.COLOR2;
        countries.append(Country((116,302), "Oregon", BIG, color, ["Washington", "Idaho", "Nevada", "California"], ["Pacific"])) 
        countries.append(Country((233,458), "Utah", BIG, color, ["Idaho", "Nevada", "Arizona", "New Mexico", "Colorado", "Wyoming"], []))
        countries.append(Country((443,368), "South Dakota", MED, color, ["Montana", "Wyoming", "Nebraska", "Iowa", "Minnesota", "North Dakota"], []))
        countries.append(Country((473,577), "Oklahoma", MED, color, ["Kansas", "Colorado", "New Mexico", "Texas", "Arkansas", "Missouri"], []))
        countries.append(Country((620,480), "Illinois", MED, color, ["Wisconsin", "Iowa", "Missouri", "Kentucky", "Indiana"], []))
        countries.append(Country((616,649), "Mississippi", MED, color, ["Louisiana", "Arkansas", "Tennesee", "Alabama"], ["Atlantic"]))
        countries.append(Country((778,511), "West Virginia", SMALL, color, ["Ohio", "Kentucky", "Virginia", "Maryland", "Pennsylvania"], []))
        countries.append(Country((793,616), "South Carolina", MED, color, ["North Carolina", "Georgia"], ["Atlantic"]))
        countries.append(Country((856,389), "New York", MED, color, ["Vermont", "Massachusettes", "Connecticut", "New Jersey", "Pennsylvania"], ["Atlantic"]))
        countries.append(Country((943,317), "Maine", MED, color, ["New Hampshire"], ["Atlantic"]))

        color = config.COLOR4;
        countries.append(Country((74,467), "California", BIG, color, ["Oregon", "Nevada", "Arizona"], ["Pacific"])) 
        countries.append(Country((203,329), "Idaho", BIG, color, ["Washington", "Oregon", "Nevada", "Utah", "Wyoming", "Montana"], []))
        countries.append(Country((335,482), "Colorado", BIG, color, ["Wyoming", "Utah", "Arizona", "New Mexico", "Oklahoma", "Kansas", "Nebraska"], []))
        countries.append(Country((449,300), "North Dakota", MED, color, ["Montana", "South Dakota", "Minnesota"], []))
        countries.append(Country((568,520), "Missouri", MED, color, ["Iowa", "Nebraska", "Kansas", "Oklahoma", "Kentucky", "Arkansas", "Tennesee", "Illinois"], []))
        countries.append(Country((694,395), "Michigan", MED, color, ["Wisconsin", "Indiana", "Ohio"], []))
        countries.append(Country((676,655), "Alabama", MED, color, ["Florida", "Georgia", "Tennesee", "Mississippi"], ["Atlantic"]))
        countries.append(Country((826,523), "Virginia", MED, color, ["North Carolina", "Tennesee", "Kentucky", "West Virginia", "Maryland"], ["Atlantic"]))
        countries.append(Country((886,458), "New Jersey", SMALL, color, ["New York", "Pennsylvania", "Delaware", "Connecticut"], ["Atlantic"]))
        countries.append(Country((892,365), "Vermont", SMALL, color, ["New Hampshire", "Massachusettes", "New York"], []))

        color = config.COLOR5;
        countries.append(Country((143,416), "Nevada", BIG, color, ["Idaho", "Oregon", "California", "Arizona", "Utah"], [])) 
        countries.append(Country((320,383), "Wyoming", BIG, color, ["Montana", "Idaho", "Utah", "Colorado", "Nebraska", "South Dakota"], []))
        countries.append(Country((308,580), "New Mexico", BIG, color, ["Arizona", "Utah", "Colorado", "Oklahoma", "Texas"], []))
        countries.append(Country((556,437), "Iowa", MED, color, ["Minnesota", "South Dakota", "Nebraska", "Missouri", "Illinois", "Wisconsin"], []))
        countries.append(Country((700,535), "Kentucky", MED, color, ["Illinois", "Missouri", "Tennesee", "Virginia", "West Virginia", "Ohio", "Indiana"], []))
        countries.append(Country((565,706), "Louisiana", MED, color, ["Texas", "Arkansas", "Mississippi"], ["Atlantic"]))
        countries.append(Country((745,652), "Georgia", MED, color, ["South Carolina", "Tennesee", "Alabama", "Florida", "North Carolina"], ["Atlantic"]))
        countries.append(Country((823,449), "Pennsylvania", MED, color, ["New York", "Ohio", "West Virginia", "Maryland", "Delaware", "New Jersey"], []))
        countries.append(Country((916,392), "Massachusettes", SMALL, color, ["New Hampshire", "Vermont", "New York", "Connecticut", "Rhode Island"], ["Atlantic"]))

        color = config.COLOR3;
        countries.append(Country((302,280), "Montana", BIG, color, ["Idaho", "Wyoming", "South Dakota", "North Dakota"], [])) 
        countries.append(Country((437,682), "Texas", BIG, color, ["New Mexico", "Oklahoma", "Arkansas", "Louisiana"], ["Atlantic"]))
        countries.append(Country((440,437), "Nebraska", MED, color, ["South Dakota", "Wyoming", "Colorado", "Kansas", "Missouri", "Iowa"], []))
        countries.append(Country((538,341), "Minnesota", BIG, color, ["Wisconsin", "Iowa", "South Dakota", "North Dakota"], []))
        countries.append(Country((679,577), "Tennesee", MED, color, ["Kentucky", "Missouri", "Arkansas", "Mississippi", "Alabama", "Georgia", "North Carolina", "Virginia"], []))
        countries.append(Country((784,742), "Florida", BIG, color, ["Georgia", "Alabama"], ["Atlantic"]))
        countries.append(Country((676,476), "Indiana", MED, color, ["Michigan", "Illinois", "Kentucky", "Ohio"], []))
        countries.append(Country((844,479), "Maryland", SMALL, color, ["Delaware", "Pennsylvania", "West Virginia", "Virginia"], ["Atlantic"]))
        countries.append(Country((909,416), "Connecticut", SMALL, color, ["Rhode Island", "Massachusettes", "New York", "New Jersey"], ["Atlantic"]))
        countries.append(Country((914,364), "New Hampshire", SMALL, color, ["Vermont", "Massachusettes", "Maine"], ["Atlantic"]))

        #Oceans
        oceans.append(Ocean((940,666), "Atlantic", 3, ["Maine", "New Hampshire", "Massachusettes", "Rhode Island", "Connecticut", "New York", "New Jersey", "Delaware", "Maryland", "Virginia", "North Carolina", "South Carolina", "Georgia", "Florida", "Alabama", "Mississippi", "Louisiana", "Texas"]))
        oceans.append(Ocean((24,256), "Pacific", 1, ["California", "Oregon", "Washington"]))
        
        # Call the base class constructor
        Continent.__init__(self, name, countries, oceans)   
     
class EastAsia(Continent):
    
    def __init__(self):

        name = 'East Asia'
        countries = []
        oceans = []
        
        color = config.COLOR1;
        countries.append(Country((358,152), "Russia", BIG, color, ["Kazakhstan", "China", "Mongolia", "North Korea"], ["Pacific"]))     
        countries.append(Country((668,654), "Philippines", MED, color, [], ["Pacific"])) 
        countries.append(Country((480,622), "Laos", MED, color, ["China", "Vietnam", "Cambodia", "Thailand", "Myanmar"], [])) 
        countries.append(Country((246,582), "India", BIG, color, ["Pakistan", "Nepal", "China", "Myanmar", "Bhutan", "Bangladesh"], ["Indian"]))
        countries.append(Country((156,418), "Tajikistan", MED, color, ["Kyrgyzstan", "Afghanistan", "China"], [])) 

        color = config.COLOR2;
        countries.append(Country((674,434), "South Korea", MED, color, ["North Korea"], ["Pacific"]))     
        countries.append(Country((606,856), "Indonesia", BIG, color, ["Papua New Guinea", "East Timor", "Malaysia"], ["Pacific", "Indian"])) 
        countries.append(Country((506,604), "Vietnam", MED, color, ["China", "Laos", "Cambodia"], ["Pacific"])) 
        countries.append(Country((350,536), "Bhutan", SMALL, color, ["India", "China"], []))
        countries.append(Country((122,452), "Afghanistan", MED, color, ["Tajikistan", "Pakistan", "China"], []))
        countries.append(Country((148,304), "Kazakhstan", BIG, color, ["Russia", "China", "Kyrgyzstan"], []))

        color = config.COLOR3;
        countries.append(Country((646,388), "North Korea", MED, color, ["China", "Russia", "South Korea"], ["Pacific"]))     
        countries.append(Country((404,318), "Mongolia", BIG, color, ["Russia", "China"], [])) 
        countries.append(Country((148,504), "Pakistan", MED, color, ["Afghanistan", "India", "China"], [])) 
        countries.append(Country((472,666), "Thailand", MED, color, ["Laos", "Cambodia", "Malaysia", "Myanmar"], ["Indian", "Pacific"]))
        countries.append(Country((652,578), "Taiwan", SMALL, color, [], ["Pacific"]))
        
        color = config.COLOR4;
        countries.append(Country((778,434), "Japan", BIG, color, [], ["Pacific"]))     
        countries.append(Country((610,602), "Myanmar", MED, color, ["India", "Bangladesh", "China", "Laos", "Thailand"], ["Indian"])) 
        countries.append(Country((490,796), "Malaysia", MED, color, ["Thailand", "Indonesia"], ["Indian", "Pacific"])) 
        countries.append(Country((900,908), "Papua New Guinea", MED, color, ["Indonesia"], ["Pacific"]))
        countries.append(Country((270,520), "Nepal", SMALL, color, ["India", "China"], []))
        countries.append(Country((166,376), "Kyrgyzstan", MED, color, ["Kazakhstan", "China", "Tajikistan"], []))

        color = config.COLOR5;
        countries.append(Country((448,458), "China", BIG, color, ["Mongolia", "Russia", "North Korea", "Vietnam", "Laos", "Myanmar", "India", "Bhutan", "Nepal", "Pakistan", "Afghanistan", "Tajikistan", "Kyrgyzstan", "Kazakhstan"], ["Pacific"]))     
        countries.append(Country((724,946), "East Timor", TINY, color, ["Indonesia"], ["Indian"])) 
        countries.append(Country((514,704), "Cambodia", MED, color, ["Vietnam", "Laos", "Thailand"], ["Pacific"])) 
        countries.append(Country((348,572), "Bangladesh", SMALL, color, ["India", "Myanmar"], ["Indian"]))
        countries.append(Country((278,766), "Sri Lanka", SMALL, color, [], ["Indian"]))
        
        #Oceans
        oceans.append(Ocean((257,838), "Indian", 1, ["India", "Sri Lanka", "Bangladesh", "Myanmar", "Thailand", "Malaysia", "Indonesia", "East Timor"]))
        oceans.append(Ocean((805,562), "Pacific", 2, ["Indonesia", "Papua New Guinea", "Malaysia", "Philippines", "Thailand", "Cambodia", "Vietnam", "China", "Taiwan", "South Korea", "North Korea", "Japan", "Russia"]))
        
        # Call the base class constructor
        Continent.__init__(self, name, countries, oceans)   
     
class WestAsia(Continent):
    
    def __init__(self):

        name = 'West Asia'
        countries = []
        oceans = []
        
        color = config.COLOR1;
        countries.append(Country((786,378), "Tajikistan", MED, color, ["China", "Kyrgyzstan", "Uzbekistan", "Afghanistan"], []))     
        countries.append(Country((922,614), "India", BIG, color, ["Pakistan", "China"], ["Indian"]))     
        countries.append(Country((388,346), "Armenia", SMALL, color, ["Turkey", "Georgia", "Azerbaijan", "Iran"], []))     
        countries.append(Country((248,518), "Israel", SMALL, color, ["Lebanon", "Jordan", "Syria"], ["Indian"]))
        countries.append(Country((478,818), "Yemen", MED, color, ["Saudi Arabia", "Oman"], ["Indian"]))
        countries.append(Country((578,676), "UAE", SMALL, color, ["Saudi Arabia", "Oman"], ["Indian"]))

        color = config.COLOR2;
        countries.append(Country((714,186), "Kazakhstan", BIG, color, ["Russia", "China", "Kyrgyzstan", "Uzbekistan", "Turkmenistan"], ["Caspian"]))     
        countries.append(Country((748,466), "Afghanistan", BIG, color, ["Tajikistan", "China", "Pakistan", "Iran", "Turkmenistan", "Uzbekistan"], []))     
        countries.append(Country((360,310), "Georgia", SMALL, color, ["Russia", "Azerbaijan", "Armenia", "Turkey"], []))     
        countries.append(Country((306,444), "Syria", SMALL, color, ["Turkey", "Iraq", "Jordan", "Israel", "Lebanon"], ["Indian"]))
        countries.append(Country((210,448), "Cyprus", SMALL, color, [], ["Indian"]))
        countries.append(Country((514,622), "Bahrain", TINY, color, ["Saudi Arabia"], ["Indian"]))
        
        color = config.COLOR3;
        countries.append(Country((684,316), "Uzbekistan", BIG, color, ["Kazakhstan", "Kyrgyzstan", "Tajikistan", "Afghanistan", "Turkmenistan"], []))     
        countries.append(Country((434,342), "Azerbaijan", SMALL, color, ["Russia", "Georgia", "Armenia", "Iran"], ["Caspian"]))     
        countries.append(Country((248,364), "Turkey", BIG, color, ["Georgia", "Armenia", "Iran", "Iraq", "Syria"], ["Indian"]))     
        countries.append(Country((416,662), "Saudi Arabia", BIG, color, ["Jordan", "Yemen", "Oman", "UAE", "Qatar", "Bahrain", "Kuwait", "Iraq"], ["Indian"]))
        countries.append(Country((832,534), "Pakistan", BIG, color, ["India", "China", "Afghanistan", "Iran"], ["Indian"]))
        
        color = config.COLOR4;
        countries.append(Country((858,318), "Kyrgyzstan", MED, color, ["Kazakhstan", "Uzbekistan", "Tajikistan", "China"], []))     
        countries.append(Country((564,490), "Iran", BIG, color, ["Turkmenistan", "Afghanistan", "Pakistan", "Iraq", "Turkey", "Armenia", "Azerbaijan"], ["Indian", "Caspian"]))     
        countries.append(Country((272,528), "Jordan", SMALL, color, ["Iraq", "Saudi Arabia", "Israel", "Syria"], ["Indian"]))     
        countries.append(Country((526,638), "Qatar", TINY, color, ["Saudi Arabia"], ["Indian"]))
        countries.append(Country((454,560), "Kuwait", SMALL, color, ["Iraq", "Saudi Arabia"], ["Indian"]))
        countries.append(Country((504,50), "Russia", BIG, color, ["Kazakhstan", "Georgia", "Azerbaijan", "China"], ["Caspian"]))

        color = config.COLOR5;
        countries.append(Country((950, 372), "China", BIG, color, ["Russia", "India", "Pakistan", "Afghanistan", "Tajikistan", "Kyrgyzstan", "Kazakhstan"], []))     
        countries.append(Country((630,364), "Turkmenistan", BIG, color, ["Kazakhstan", "Uzbekistan", "Afghanistan", "Iran"], ["Caspian"]))     
        countries.append(Country((384,484), "Iraq", MED, color, ["Syria", "Turkey", "Iran", "Kuwait", "Saudi Arabia", "Jordan"], ["Indian"]))     
        countries.append(Country((626,714), "Oman", MED, color, ["UAE", "Yemen", "Saudi Arabia"], ["Indian"]))
        countries.append(Country((264,468), "Lebanon", TINY, color, ["Syria", "Israel"], ["Indian"]))
        countries.append(Country((796,930), "Maldives", MED, color, [], ["Indian"]))
        
        #Oceans
        oceans.append(Ocean((718,824), "Indian", 1, ["India", "Pakistan", "Iran", "Iraq", "Kuwait", "Saudi Arabia", "Bahrain", "Qatar", "UAE", "Oman", "Yemen", "Jordan", "Israel", "Lebanon", "Maldives", "Cyprus", "Syria", "Turkey"]))
        oceans.append(Ocean((476,318), "Caspian", 2, ["Russia", "Kazakhstan", "Turkmenistan", "Iran", "Azerbaijan"]))
        
        # Call the base class constructor
        Continent.__init__(self, name, countries, oceans)   
     
# this runs the main function if this script is called to run.
#  If it is imported as a module, we don't run the main function.
if __name__ == "__main__":
    europe = Europe()
    africa = Africa()
    usa = USA()
    east_asia = EastAsia()
    west_asia = WestAsia()
    
    europe.test_integrity()
    africa.test_integrity()
    usa.test_integrity()
    east_asia.test_integrity()
    west_asia.test_integrity()
        