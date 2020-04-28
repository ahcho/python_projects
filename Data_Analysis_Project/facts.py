'''
Author: Anna Cho
'''
#!/usr/bin/env python3

import bs4
import collections
import json
import pickle
import re
import requests
import statistics

class Facts(collections.defaultdict):
    """
    A dictionary of facts about communities in Santa Clara County.
    """
    
    # The California Dept. of Education 2012 to 2013 Accountability Progress Report
    _URL_APR_2013 = 'https://api.cde.ca.gov/Acnt2013/'
    _PATH_APR_SANTA_CLARA = '/2013GrthAPICo.aspx?cSelect=43,SANTA,CLARA'
    
    # The California Dept. of Education School Directory
    _URL_CDS = 'https://www.cde.ca.gov/SchoolDirectory/details?cdscode='
    
    # The American FactFinder page
    _URL_FF = 'https://factfinder.census.gov/'
    _URL_POP_DATA = _URL_FF + 'bkmk/table/1.0/en/DEC/10_DP/DPDP1/8600000US'
    _URL_HOME_DATA = _URL_FF + 'bkmk/table/1.0/en/ACS/16_5YR/DP04/8600000US'
    _URL_INCOME_DATA = _URL_FF + 'bkmk/table/1.0/en/ACS/16_5YR/DP03/8600000US'
    _URL_EDU_DATA = _URL_FF + 'bkmk/table/1.0/en/ACS/16_5YR/S1501/8600000US'
    
    # The page to request rendering for the American FactFinder
    _URL_FF_RENDER = ('https://factfinder.census.gov/'
                      'tablerestful/tableServices/renderProductData')
    
    def __init__(self):
        """
        Makes a dictionary by scraping information from the California
        Department of Education and the United States Census Bureau.
        """
        
        super().__init__(dict)
        
        with requests.Session() as self.session:
            self._eat_apr()
        
        del self.session
    
    def _eat_apr(self):
        links, ratings = self._get_school_links_and_ratings()
        self._get_location_and_school_data(links, ratings)
        self._postal_codes_to_del = []
        
        for postal_code in self:
            print('Processing', postal_code, end='... ')
            
            try:
                self._get_population_data(postal_code)
            
            except IndexError:
                self._postal_codes_to_del.append(postal_code)
                print('skipped')
                continue
            
            self._get_home_data(postal_code)
            self._get_income_data(postal_code)
            self._get_education_data(postal_code)
            print('done')
        
        del self._postal_codes_to_del
            
    def _get_school_links_and_ratings(self):
        response = self.session.get(__class__._URL_APR_2013 + __class__._PATH_APR_SANTA_CLARA)
        soup = bs4.BeautifulSoup(response.content)
        links = (anchor['href'] for anchor in soup.select('.medium_left a'))
        
        ratings = (
            int('0' + re.sub(r"\D", "", cell.text))
            for cell in soup.select('.medium_left + .medium_center')
        )
        
        return links, ratings
    
    def _get_location_and_school_data(self, links, ratings):
        ratings_by_postal_code = collections.defaultdict(list)
        
        for link, rating in zip(links, ratings):
            print('Processing', link, end='... ')
            
            try:
                location = self._get_location_data(self._get_cds(link))
                city, state, postal_code = location
                city.strip()
            
            except IndexError:
                print('error')
                continue
            
            self[postal_code]['city'] = city
            self[postal_code]['state'] = state
            ratings_by_postal_code[postal_code].append(rating)
            print('done')
        
        for postal_code, ratings in ratings_by_postal_code.items():
            self[postal_code]['schoolPerformance'] = {
                'medianSchoolRating': str(statistics.median(ratings)),
                'meanSchoolRating': str(statistics.mean(ratings))
            }
    
    def _get_cds(self, href):
        response = self.session.get(__class__._URL_APR_2013 + href)
        soup = bs4.BeautifulSoup(response.content)
        
        # county-district-school code
        return soup.select('#lbl_cdscode')[0].text.replace('-', '')
    
    def _get_location_data(self, cds):
        response = self.session.get(__class__._URL_CDS + cds)
        soup = bs4.BeautifulSoup(response.content)
        
        return re.findall(
            r'\r\n([\D ]+), (\w\w) (\d+)',
            soup.select('.details-field-label + td')[5].text
        )[0]
    
    def _get_population_data(self, postal_code):
        self.session.get(__class__._URL_POP_DATA + postal_code)
        response = self.session.get(__class__._URL_FF_RENDER)
        table = response.json()['ProductData']['productDataTable']
        soup = bs4.BeautifulSoup(table)
        
        self[postal_code]['population'] = {
            'total': soup.select('#r78 + .left')[0],
            'white': soup.select('#r80 + .left')[0],
            'blackOrAfricanAmerican': soup.select('#r81 + .left')[0],
            'native': soup.select('#r82 + .left')[0],
            'asian': soup.select('#r83 + .left')[0],
            'pacificIslander': soup.select('#r91 + .left')[0],
            'someOtherRace': soup.select('#r96 + .left')[0],
            'twoOrMoreRaces': soup.select('#r97 + .left')[0]
        }
        
        self[postal_code]['population'] = {
            race: number.text.replace(',', '')
            for race, number in self[postal_code]['population'].items()
        }
    
    def _get_home_data(self, postal_code):
        self.session.get(__class__._URL_HOME_DATA + postal_code)
        response = self.session.get(__class__._URL_FF_RENDER)
        soup = bs4.BeautifulSoup(response.content)
        
        self[postal_code]['medianHomeValue'] = re.sub(
            r'\D', '', soup.select('#r101 + .left')[0].text
        )
    
    def _get_income_data(self, postal_code):
        self.session.get(__class__._URL_INCOME_DATA + postal_code)
        response = self.session.get(__class__._URL_FF_RENDER)
        soup = bs4.BeautifulSoup(response.content)
        
        self[postal_code]['income'] = {
            'medianHouseholdIncome': soup.select('#r68 + .left')[0],
            'meanHouseholdIncome': soup.select('#r69 + .left')[0]
        }
        
        self[postal_code]['income'] = {
            measure: value.text.replace(',', '')
            for measure, value in self[postal_code]['income'].items()
        }
    
    def _get_education_data(self, postal_code):
        self.session.get(__class__._URL_EDU_DATA + postal_code)
        response = self.session.get(__class__._URL_FF_RENDER)
        soup = bs4.BeautifulSoup(response.content)
        
        self[postal_code]['education'] = {
            'percentHighSchoolGraduateOrHigher': soup.select('#r14 + td + td + td')[1],
            'percentBachelorsDegreeOrHigher': soup.select('#r15 + td + td + td')[0]
        }
        
        self[postal_code]['education'] = {
            category: percentage.text.replace('%', '')
            for category, percentage in self[postal_code]['education'].items()
        }
    
    def jsonify(self):
        return json.dumps(self)

if __name__ == '__main__':
    facts = Facts()
    
    with open('facts.json', 'w') as file:
        file.write(facts.jsonify())
