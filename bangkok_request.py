import requests
import datetime
import os

TOKEN = os.environ.get('TOKEN_BANGKOK')

HEADERS = {'Ocp-Apim-Subscription-Key': TOKEN, }


def get_last_update_rate():
    url = 'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService/GetDateTimeLastUpdate'
    response = requests.get(url, headers=HEADERS)
    last_date_update = response.json()[0].get("Day").split('/')
    time_update = response.json()[0].get("Time")
    return dict(
        day=last_date_update[0],
        month=last_date_update[1],
        year=last_date_update[2],
        last_time_update=time_update
    )


def get_inner_family_value(value_rate='US Dollar 50-100', all=None):
    url = 'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService/Getfxfamily'
    response = requests.get(url, headers=HEADERS)
    if all is not None:
        return response.json()
    for value in response.json():
        if value.get('Description') == value_rate:
            return value.get('Family')
    return None


def get_x_rate_for_value(date_list, family, rate_info="TT"):
    now = datetime.datetime.now()
    tdd = now.day
    tmm = now.month
    tyyyy = now.year
    fdd = date_list.get('day')
    fmm = date_list.get('month')
    fyyyy = date_list.get('year')
    lang = 'en'
    url = f'https://bbl-sea-apim-p.azure-api.net/api/ExchangeRateService/GetChartfxrates/{fdd}/{fmm}/{fyyyy}/{tdd}/{tmm}/{tyyyy}/{family}/{lang}'
    response = requests.get(url, headers=HEADERS)
    data_needed = response.json()[-1]
    date = data_needed.get('Ddate').split('/')

    return dict(
        tt_rate=data_needed.get(rate_info),
        date=f"{date[1]}/{date[0]}/{date[2]}",
        time=data_needed.get('DTime')
    )


def get_bangkok_usd_rate_inner():
    last_update = get_last_update_rate()
    family = get_inner_family_value()
    if family is None:
        return get_inner_family_value(all=1)
    tt_rate = get_x_rate_for_value(last_update, family)
    if tt_rate is not None:
        return tt_rate


if __name__ == '__main__':

    last_update = get_last_update_rate()
    print(last_update)
    result = get_bangkok_usd_rate_inner()
    print(result)


