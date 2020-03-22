import requests
import json
import country_converter as coco
import us
from sopel.module import commands, example, NOLIMIT
from sopel.tools import web
from sopel.formatting import *
from sopel import bot


def show_country_data(countries_json, matched_countries, search_string):
    for country_dict in countries_json:
        if country_dict['country'] == matched_countries[search_string]:
            country = country_dict['country']
            cases = country_dict['cases']
            cases_today = country_dict['todayCases']
            deaths = country_dict['deaths']
            deaths_today = country_dict['todayDeaths']
            recovered = country_dict['recovered']
            cases_per_mil = country_dict['casesPerOneMillion']

            msg = f'Infected in {country}: {cases:,} (+{cases_today:,}), deaths: {deaths:,} (+{deaths_today:,}), recovered: {recovered:,}, cases per million people: {cases_per_mil:,}'

            return msg


def show_state_data(state_name):
    states_json = requests.get('https://corona.lmao.ninja/states').json()
    for state_dict in states_json:
        if state_dict['state'] == state_name:
            state = state_dict['state']
            cases = state_dict['cases']
            cases_today = state_dict['todayCases']
            deaths = state_dict['deaths']
            deaths_today = state_dict['todayDeaths']
            recovered = state_dict['recovered']
            msg = f'Infected in {state}: {cases:,} (+{cases_today:,}), deaths: {deaths:,} (+{deaths_today:,}), recovered: {recovered:,}'
            return msg


def show_region_data(region_json, region_name):
    for region_dict in region_json:
        try:
            if region_dict['province'].lower() == region_name.lower():
                country = region_dict['country']
                province = region_dict['province']
                cases = int(region_dict['stats']['confirmed'])
                deaths = int(region_dict['stats']['deaths'])
                recovered = int(region_dict['stats']['recovered'])
                last_update = region_dict['updatedAt']
                msg = f'Infected in {province}, {country}: {cases:,}, deaths: {deaths:,}, recovered: {recovered:,}, last update at {last_update}'
                return msg
        except AttributeError:
            pass


def return_message(search_string):
    countries_json = requests.get('https://corona.lmao.ninja/countries').json()
    countries_list = [d['country'] for d in countries_json]
    matched_countries = coco.match(
        [search_string], countries_list, not_found='Not found')

    # first, check if country exists
    if matched_countries[search_string] != 'Not found':
        msg = show_country_data(
            countries_json, matched_countries, search_string)
        return msg
    else:
        # if not country, check if US state
        try:
            state = us.states.lookup(search_string).name
            msg = show_state_data(state)
            return msg
        # if not US state, check if international region
        except AttributeError:
            regions_json = requests.get(
                'https://corona.lmao.ninja/jhucsse').json()
            regions_list = [d['province'].lower()
                            for d in regions_json if d['province']]
            if search_string.lower() in regions_list:
                msg = show_region_data(regions_json, search_string)
                return msg
            else:
                msg = 'No country or region with that name found. Either it does not exist, or no data has been recorded yet'
                return msg


@commands('corona')
@example('.corona sweden')
def corona(bot, trigger):
    msg = return_message(trigger.group(2))
    bot.say(msg)
