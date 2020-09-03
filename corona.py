import requests
import json
import country_converter as coco
import us
import arrow
from sopel.module import commands, example, NOLIMIT
from sopel.formatting import *
from sopel import bot


def show_all_data():
    all_json = requests.get('https://corona.lmao.ninja/v2/all').json()
    cases = all_json['cases']
    deaths = all_json['deaths']
    recovered = all_json['recovered']
    last_updated = all_json['updated']

    msg = f'Infected: {cases:,}, deaths: {deaths:,}, recovered: {recovered:,}'
    return msg


def show_country_data(search_string):
    countries_json = requests.get(
        'https://corona.lmao.ninja/v2/countries').json()
    countries_list = [d['country'] for d in countries_json]
    matched_countries = coco.match(
        [search_string], countries_list, not_found='Not found')
    if matched_countries[search_string] != 'Not found':
        for country_dict in countries_json:
            if country_dict['country'] == matched_countries[search_string]:
                country = country_dict['country']
                cases = country_dict['cases']
                cases_today = country_dict['todayCases']
                deaths = country_dict['deaths']
                deaths_today = country_dict['todayDeaths']
                recovered = country_dict['recovered']
                cases_per_mil = country_dict['casesPerOneMillion']
                tests_per_mil = country_dict['testsPerOneMillion']

                msg = f'Infected in {country}: {cases:,} (+{cases_today:,}), deaths: {deaths:,} (+{deaths_today:,}), recovered: {recovered:,}, cases per million people: {cases_per_mil:,}, tests per million people: {tests_per_mil:,}'

                return msg
    else:
        return None


def show_state_data(search_string):
    try:
        state_abbr = us.states.lookup(search_string).abbr
        state_name = us.states.lookup(search_string).name
    except AttributeError:
        return None

    states_json = requests.get(
        'https://covidtracking.com/api/states').json()

    for state_dict in states_json:
        if state_dict['state'] == state_abbr:
            positive = state_dict['positive']
            positive_increase = state_dict['positiveIncrease']
            hospitalized = state_dict['hospitalized']
            hospitalized_increase = state_dict['hospitalizedIncrease']
            deaths = state_dict['death']
            deaths_increase = state_dict['deathIncrease']
            total_tests = state_dict['totalTestResults']
            last_updated = arrow.get(
                state_dict['dateModified']).humanize(granularity="hour")

            msg = f'Infected in {state_name}: {positive:,} (+{positive_increase:,}), deaths: {deaths:,} (+{deaths_increase}), hospitalized: {hospitalized:,} (+{hospitalized_increase}), tests: {total_tests:,}. Last updated {last_updated}'

            return msg


def show_region_data(search_string):
    regions_json = requests.get(
        'https://corona.lmao.ninja/v2/jhucsse').json()
    regions_list = [d['province'].lower()
                    for d in regions_json if d['province']]
    if search_string.lower() in regions_list:
        for region_dict in regions_json:
            try:
                if region_dict['province'].lower() == search_string.lower():
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
    else:
        return None


def return_message(search_string):
    # if no country or region is entered, show global data
    if not search_string:
        global_message = show_all_data()
        return global_message

    # check if string is a country and return message for that country
    country_message = show_country_data(search_string)
    if country_message:
        return country_message

    # if it is not a country, check if it is a US state
    state_message = show_state_data(search_string)
    if state_message:
        return state_message

    # if it is not a US state, check if it is a region
    region_message = show_region_data(search_string)
    if region_message:
        return region_message

    # return if string cannot be found to be any of the above
    else:
        msg = 'No country or region with that name found. Either it does not exist, or no data has been recorded yet'
        return msg


@commands('corona')
@example('.corona sweden')
def corona(bot, trigger):
    msg = return_message(trigger.group(2))
    bot.say(msg)
