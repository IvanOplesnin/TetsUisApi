import asyncio
import datetime
import json
import uuid

import aiohttp as http

from config import *


class ClientDataUIS:
    def __init__(self, token):
        self._token = token
        self._headers = HEADERS
        self._url = BASE_URL
        self._call_url = CALL_URL

    @staticmethod
    def _create_filter(field, operator, value):
        return {
            "field": field,
            "operator": operator,
            "value": value
        }

    async def _request(self, body):
        async with http.ClientSession() as session:
            async with session.post(self._url, json=body, headers=self._headers) as resp:
                if resp.status == 200:
                    return await resp.json()

    async def _call_request(self, body):
        async with http.ClientSession() as session:
            async with session.post(self._call_url, json=body, headers=self._headers) as resp:
                if resp.status == 200:
                    return await resp.json()

    async def get_my_numbers(self):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.virtual_numbers",
            "params": {
                "access_token": self._token,
            }
        }
        async with http.ClientSession() as session:
            async with session.post(self._url, json=body, headers=self._headers) as resp:
                if resp.status == 200:
                    return await resp.json()

    async def get_available_numbers(self, limit=10):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.available_virtual_numbers",
            "params": {
                "access_token": self._token,
                "limit": limit,
                "filter": {
                    "filters": [
                        self._create_filter("location_mnemonic", "=", "msk"),
                        self._create_filter("category", "=", "usual")
                    ],
                    "condition": "and"
                }
            }
        }
        return await self._request(body)

    async def add_number(self):
        available_numbers = await self.get_available_numbers(1)
        if not available_numbers.get("result"):
            print("No available numbers")
            return None
        phone = available_numbers.get("result").get("data")[0].get("phone_number")
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "enable.virtual_numbers",
            "params": {
                "access_token": self._token,
                "virtual_phone_number": phone
            }
        }
        return await self._request(body), phone

    async def delete_number(self, phone):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "disable.virtual_numbers",
            "params": {
                "access_token": self._token,
                "virtual_phone_number": phone
            }
        }

        return await self._request(body)

    async def _create_employee(
            self, first_name, last_name, patronymic, phone_number, extension_phone_number
    ):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "create.employees",
            "params": {
                "access_token": self._token,
                "first_name": first_name,
                "last_name": last_name,
                "patronymic": patronymic,
                "status": "available",
                "in_external_allowed_call_directions": ["in", "out"],
                "in_internal_allowed_call_directions": ["in", "out"],
                "out_external_allowed_call_directions": ["in", "out"],
                "out_internal_allowed_call_directions": ["in", "out"],
                "phone_numbers": [
                    {
                        "phone_number": phone_number,
                        "channels_count": 2,
                        "dial_time": 30,
                    }
                ],
                "extension": {
                    "extension_phone_number": extension_phone_number,
                }
            }
        }
        return await self._request(body)

    async def get_employees(self, filter=None):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.employees",
            "params": {
                "access_token": self._token,
            }
        }
        if filter:
            body["params"]["filter"] = filter
        print(body)
        return await self._request(body)

    async def create_employee(self, first_name, last_name, patronymic):
        resp, phone = await self.add_number()
        print(resp)
        if resp.get("error"):
            print(resp.get("error"))
            return None

        all_employees = await self.get_employees()
        print(all_employees)
        all_employees = all_employees.get("result").get("data")
        ext_phones = [ext.get("extension").get("extension_phone_number") for ext in all_employees
                      if ext.get("extension").get("extension_phone_number")]
        new_ext_phone = str(int(max(ext_phones)) + 1)
        return await self._create_employee(
            first_name, last_name, patronymic, phone, new_ext_phone
        )

    async def create_sip_line(self, employee_id):
        filter = self._create_filter(
            "id", "=", employee_id
        )
        employees = await self.get_employees(filter)
        if not employees.get("result"):
            print("No employees")
            return None
        print(employees.get("result"))
        phone = employees.get("result").get("data")[0].get("phone_numbers")[0].get("phone_number")

        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "create.sip_lines",
            "params": {
                "access_token": self._token,
                "employee_id": employee_id,
                "virtual_phone_number": phone
            }
        }
        return await self._request(body)

    async def get_campaigns(self):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.campaigns",
            "params": {
                "access_token": self._token
            }
        }
        return await self._request(body)

    async def get_sources(self):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.sources",
            "params": {
                "access_token": self._token
            }
        }
        return await self._request(body)

    async def get_sites(self):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.sites",
            "params": {
                "access_token": self._token
            }
        }
        return await self._request(body)

    async def get_sip_lines(self, employee_id):
        filter = self._create_filter(
            "employee_id", "=", employee_id
        )
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.sip_lines",
            "params": {
                "access_token": self._token,
                "filter": filter
            }
        }
        return await self._request(body)

    async def upload_calls(self):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "upload.calls",
            "params": {
                "access_token": self._token,
                "calls": [
                    {
                        "ext_id": str(uuid.uuid4()),
                        "calling_phone_number": "79096004875",
                        "called_phone_number": "79096004876",
                        "start_time": (datetime.datetime.now() - datetime.timedelta(
                            minutes=1
                        )).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "finish_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "is_lost": False,
                    }
                ]
            }
        }
        return await self._request(body)

    async def upload_emails(self, html):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "upload.emails",
            "params": {
                "access_token": self._token,
                "emails": [
                    {
                        "date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "sender_name": "Степан",
                        "subject": "Тест",
                        "message": "Тестовое сообщение",
                        "message_html": html,
                        "email_from": "i.oplesnin@comegic.dev",
                        "email_to": "aplesnin2010@yandex.ru"
                    }
                ]
            }
        }
        return await self._request(body)

    async def upload_offline_messages(self, message):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "upload.offline_messages",
            "params": {
                "access_token": self._token,
                "offline_messages": [
                    {
                        "date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "name": "Stepan",
                        "phone": "79096004875",
                        "site_id": 127332,
                        "message": message,
                        "form_name": "MyForm",
                        "ext_id": str(uuid.uuid4())
                    }
                ]
            }
        }
        return await self._request(body)

    async def get_report_calls(self):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.calls_report",
            "params": {
                "access_token": self._token,
                "date_from": (datetime.datetime.now() - datetime.timedelta(weeks=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "date_till": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
        return await self._request(body)

    @staticmethod
    def create_stage(name, ext_id, order=None):
        body = {
            "ext_id": ext_id,
            "name": name
        }
        if order:
            body["order"] = order
        return body

    async def create_sales_funnel(
            self, name, success_stage: dict, fail_stage: dict, stages: list[dict]
    ):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "create.sales_funnel",
            "params": {
                "access_token": self._token,
                "ext_id": str(uuid.uuid4()),
                "name": name,
                "stages": {
                    "success": success_stage,
                    "failed": fail_stage,
                    "in_process": stages
                }
            }
        }
        return await self._request(body)

    @staticmethod
    def create_contact(
            ext_id, name, phones: list[str] = None, emails: list[str] = None
    ):
        body = {
            "ext_id": ext_id,
            "name": name,
        }
        if phones:
            body["phone_numbers"] = phones

        if emails:
            body["emails"] = emails

        return body

    async def create_deal_contact(self, contacts: list[dict]):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "create.deal_contacts",
            "params": {
                "access_token": self._token,
                "contacts": contacts
            }
        }
        with open("fix.json", "w") as f:
            json.dump(
                body, f, indent=4
            )
        return await self._request(body)

    @staticmethod
    def _create_deal(
            ext_id, name, time, contacts_id: list[str], sales_funnel_id, stage_id,
            closed_time=None, user_fields=None
    ):
        body = {
            "ext_id": ext_id,
            "name": name,
            "created_date_time": time,
            "modified_date_time": time,
            "modified_stage_date_time": time,
            "contact_ext_ids": contacts_id,
            "main_contact_ext_id": contacts_id[0],
            "sales_funnel_ext_id": sales_funnel_id,
            "stage_ext_id": stage_id,
            "comments": "Тестовая сделка"
        }
        if closed_time:
            body["closed_date_time"] = closed_time
        if user_fields:
            body["user_fields"] = user_fields

        return body

    async def create_deal(self, deals: list[dict]):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "upload.deals_history",
            "params": {
                "access_token": self._token,
                "deals": deals
            }
        }
        return await self._request(body)

    async def get_deals_history(self):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.deals_history",
            "params": {
                "access_token": self._token
            }
        }
        return await self._request(body)

    async def create_user_fields(self, ext_id, name, type_):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "create.deal_user_field",
            "params": {
                "access_token": self._token,
                "ext_id": ext_id,
                "name": name,
                "data_type": type_
            }
        }
        return await self._request(body)

    async def get_scenarios(self):
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.scenarios",
            "params": {
                "access_token": self._token
            }
        }
        return await self._request(body)

    async def start_employee_call(self):
        body = {
            "jsonrpc": "2.0",
            "method": "start.employee_call",
            "id": "req1",
            "params": {
                "access_token": self._token,
                "first_call": "employee",
                "show_virtual_phone_number": True,
                "virtual_phone_number": "74950853409",
                "direction": "in",
                "contact": "79096004875",
                "employee": {
                    "id": 9699580,
                    "phone_number": "0486173"
                }
            }
        }
        return await self._call_request(body)

    async def start_scenario_call(self):
        body = {
            "jsonrpc": "2.0",
            "method": "start.scenario_call",
            "id": "req1",
            "params": {
                "access_token": self._token,
                "virtual_phone_number": "74950853409",
                "contact": "79096004875",
                "first_call": "employee",
                "scenario_id": 528589,
            }
        }

        return await self._call_request(body)

    async def start_virtual_call(self):
        body = {
            "jsonrpc": "2.0",
            "method": "start.vnumber_call",
            "id": "req1",
            "params": {
                "access_token": self._token,
                "virtual_phone_number": "74950853409",
                "direction": "in",
                "contact": "79096004875",
                "first_call": "employee",
                "show_virtual_phone_number": True,
            }
        }
        return await self._call_request(body)

    async def transfer_talk(self, session_id):
        body = {
            "jsonrpc": "2.0",
            "method": "transfer.talk",
            "id": "req1",
            "params": {
                "access_token": self._token,
                "call_session_id": session_id
            }
        }
        return await self._call_request(body)

    async def hold_call(self, session_id):
        body = {
            "jsonrpc": "2.0",
            "method": "hold.call",
            "id": "req1",
            "params": {
                "access_token": self._token,
                "call_session_id": session_id,
                "contact_message": {
                    "type": "tts",
                    "value": "Холд тест"
                }
            }
        }
        return await self._call_request(body)

    async def make_call(self, session_id, number):
        body = {
            "jsonrpc": "2.0",
            "method": "make.call",
            "id": "req1",
            "params": {
                "access_token": self._token,
                "call_session_id": session_id,
                "to": number
            }
        }
        return await self._call_request(body)


async def main():
    client = ClientDataUIS(TOKEN)
    employee = await client.create_employee(
        "Ivan", "Oplesnin", "Sergeevich"
    )
    print(employee)
    await asyncio.sleep(5)
    if res := employee.get("result").get("data"):
        id = res.get("id")
        print(id)

        sip_line = await client.create_sip_line(id)
        print(sip_line)


async def main_2():
    client = ClientDataUIS(TOKEN)
    all_numbers = await client.get_my_numbers()
    if list_numbers := all_numbers.get("result").get("data"):
        numbers: list[str] = [
            n.get("virtual_phone_number") for n in list_numbers
        ]

    for number in numbers:
        if not number.endswith("3409") and number.endswith("6044"):
            res = await client.delete_number(number)
            print(res)


async def main_3():
    client = ClientDataUIS(TOKEN)
    resp = await client.get_campaigns()
    print(resp)
    # sources = await client.get_sources()
    # with open("sources.json", "w") as f:
    #     json.dump(sources, f, indent=4)
    sites = await client.get_sites()
    print(sites)


async def main_4():
    client = ClientDataUIS(TOKEN)
    employee = await client.get_employees()
    if res := employee.get("result").get("data"):
        employees_id = [r.get("id") for r in res]
        sip_lines = {}
        for id in employees_id:
            res = await client.get_sip_lines(id)
            print(res)
            sip_line = res.get("result").get("data")
            sip_lines[id] = sip_line

        with open("sip_lines.json", "w") as f:
            json.dump(sip_lines, f, indent=4)


async def main_5():
    client = ClientDataUIS(TOKEN)
    resp = await client.upload_calls()
    print(resp)


async def main_6():
    html_data = "hello"

    client = ClientDataUIS(TOKEN)
    resp = await client.upload_emails(html_data)
    print(resp)


async def upload_offline_messages():
    client = ClientDataUIS(TOKEN)
    resp = await client.upload_offline_messages("hello")
    print(resp)


async def get_report():
    client = ClientDataUIS(TOKEN)
    resp = await client.get_report_calls()
    if res := resp.get("result").get("data"):
        with open("report.json", "w") as f:
            json.dump(res, f, indent=4)


async def create_sales_funnel():
    client = ClientDataUIS(TOKEN)
    name = "Продажа квартиры"
    success_stage = client.create_stage(name="Квартира получена", ext_id="1000")
    fail_stage = client.create_stage(name="Сделка провалена", ext_id="10001")
    first_stage = client.create_stage(name="Отклик получен", ext_id="1", order=10)
    second_stage = client.create_stage(name="Договор аванса получен", ext_id="2", order=20)
    third_stage = client.create_stage(name="Аванс получен", ext_id="3", order=30)
    fourth_stage = client.create_stage(name="Финальный счет получен", ext_id="4", order=40)
    stages = [
        first_stage,
        second_stage,
        third_stage,
        fourth_stage,
    ]
    resp = await client.create_sales_funnel(name, success_stage, fail_stage, stages)
    print(resp)
    if res := resp.get("result").get("data"):
        with open("funnel_2.json", "w") as f:
            json.dump(res, f, indent=4)


async def create_deal_contact():
    client = ClientDataUIS(TOKEN)
    contact_1 = client.create_contact(
        "001", "Сергей", phones=["79096004875"], emails=["test1@test.ru"]
    )
    contact_2 = client.create_contact(
        "002", "Иван", phones=["79124671624"], emails=["test2@test.ru"]
    )
    contact_3 = client.create_contact(
        "003", "Петр", phones=["79096004878"], emails=["test3@test.ru"]
    )
    contact_4 = client.create_contact(
        "004", "Степан", phones=["79096004879"], emails=["test4@test.ru"]
    )
    contact_5 = client.create_contact(
        "005", "Иоан", phones=["79096004870"], emails=["test5@test.ru"]
    )
    contact_6 = client.create_contact(
        "006", "Полина", phones=["79096004874"], emails=["test6@test.ru"]
    )

    contacts = [
        contact_1,
        contact_2,
        contact_3,
        contact_4,
        contact_5,
        contact_6
    ]

    resp = await client.create_deal_contact(contacts)
    print(resp)
    if res := resp.get("result").get("data"):
        with open("contacts.json", "w") as f:
            json.dump(res, f, indent=4)


async def create_deal():
    client = ClientDataUIS(TOKEN)
    name = "Тестовая сделка"
    time = datetime.datetime.now() - datetime.timedelta(days=7)
    funnel_id = "bca12b30-dbde-4294-ba19-26ee26e9d287"
    list_time = [(time + datetime.timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S") for i in
                 range(5)]
    list_stage_id = ["1", "2", "3", "4", "1000"]
    time_and_id = list(zip(list_time, list_stage_id))
    list_deal = []
    ext_id = "LuckyDeal001"
    user_fields = [
        {"ext_id": "001", "value": "Газовое отопление"},
        {"ext_id": "002", "value": 57}
    ]
    for time, stage_id in time_and_id:
        if stage_id != "1000":
            d = client._create_deal(
                ext_id=ext_id,
                name=name,
                time=time,
                contacts_id=["002", "005"],
                sales_funnel_id=funnel_id,
                stage_id=stage_id,
                user_fields=user_fields
            )
        else:
            d = client._create_deal(
                ext_id=ext_id,
                name=name,
                time=time,
                contacts_id=["002", "005"],
                sales_funnel_id=funnel_id,
                stage_id=stage_id,
                closed_time=time,
                user_fields=user_fields
            )
        list_deal.append(d)

    resp = await client.create_deal(list_deal)
    print(resp)


async def get_deals_history():
    client = ClientDataUIS(TOKEN)
    resp = await client.get_deals_history()
    print(resp)
    if res := resp.get("result").get("data"):
        with open("deals_history.json", "w") as f:
            json.dump(res, f, indent=4)


async def create_user_fields():
    list_params = [
        {"ext_id": "001", "name": "Отопление", "type_": "string"},
        {"ext_id": "002", "name": "Квадратные метры", "type_": "numeric"},
    ]
    client = ClientDataUIS(TOKEN)
    for params in list_params:
        if res := await client.create_user_fields(**params):
            print(res)


async def call_employee():
    client = ClientDataUIS(TOKEN)
    resp = await client.start_employee_call()
    print(resp)


async def get_scenarios():
    client = ClientDataUIS(TOKEN)
    resp = await client.get_scenarios()
    if res := resp.get("result").get("data"):
        with open("scenarios.json", "w") as f:
            json.dump(res, f, indent=4)


async def call_scenario():
    client = ClientDataUIS(TOKEN)
    resp = await client.start_scenario_call()
    print(resp)


async def virtual_number():
    client = ClientDataUIS(TOKEN)
    resp = await client.start_virtual_call()
    print(resp)


async def transfer_call():
    client = ClientDataUIS(TOKEN)
    new_call = await client.start_employee_call()
    print(new_call)
    call_id = new_call.get("result").get("data").get("call_session_id")
    if call_id:
        input("Нажмите Enter для перехода к следующему шагу")
        resp = await client.hold_call(call_id)
        print(resp)
        number = input("Ввести добавочный номер: ")
        resp = await client.make_call(call_id, number)
        print(resp)
        input("Нажмите Enter для перехода к следующему шагу")
        resp = await client.transfer_talk(call_id)
        print(resp)


if __name__ == '__main__':
    asyncio.run(transfer_call())
