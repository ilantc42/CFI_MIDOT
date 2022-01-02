# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from typing import Optional, Union

import attr
from attrs_strict import type_validator


def _add_type_validator(cls, fields):
    validated_fields = []
    for field in fields:
        if field.validator is not None:
            validated_fields.append(field)
            continue
        validated_fields.append(field.evolve(validator=type_validator()))
    return validated_fields


@attr.s(frozen=True, auto_attribs=True, field_transformer=_add_type_validator)
class NgoTopRecipientSalary:
    recipient_title: str
    gross_salary_in_nis: float


@attr.s(frozen=True, auto_attribs=True, field_transformer=_add_type_validator)
class NgoTopRecipientsSalaries:
    top_earners_salaries: list[NgoTopRecipientSalary]
    report_year: int


@attr.s(frozen=True, auto_attribs=True, field_transformer=_add_type_validator)
class NgoGeneralInfo:
    ngo_name: str
    ngo_year_founded: int
    ngo_goal: str = attr.ib(default="")
    volunteers_num: Optional[int] = attr.ib(default=None)
    employees_num: Optional[int] = attr.ib(default=None)
    ngo_members_num: Optional[int] = attr.ib(default=None)


@attr.s(frozen=True, auto_attribs=True, field_transformer=_add_type_validator)
class NgoFinanceInfo:
    report_year: int

    allocations_from_government: Union[int, float]
    allocations_from_local_authority: Union[int, float]
    allocations_from_other_sources: Union[int, float]

    donations_from_aboard: Union[int, float]
    donations_from_israel: Union[int, float]

    service_income_from_country: Union[int, float]
    service_income_from_local_authority: Union[int, float]
    service_income_from_other: Union[int, float]

    other_income_from_other_sources: Union[int, float]
    other_income_members_fee: Union[int, float]

    expenses_other: Union[int, float] = attr.ib(default=0)
    expenses_for_management: Union[int, float] = attr.ib(default=0)
    expenses_salary_for_management: Union[int, float] = attr.ib(default=0)
    expenses_salary_for_activities: Union[int, float] = attr.ib(default=0)
    other_expenses_for_activities: Union[int, float] = attr.ib(default=0)
    donations_value_for_money: Union[int, float] = attr.ib(default=0)

    # ------------ Computed ------------
    total_allocations: Union[int, float] = attr.ib(init=False)
    total_donations: Union[int, float] = attr.ib(init=False)
    total_expenses: Union[int, float] = attr.ib(init=False)
    total_service_income: Union[int, float] = attr.ib(init=False)
    total_other_income: Union[int, float] = attr.ib(init=False)
    # ------------ Ratios ------------
    program_expense_ratio: Optional[float] = attr.ib(init=False)
    administrative_expense_ratio: Optional[float] = attr.ib(init=False)

    @total_allocations.default
    def _total_allocations(self) -> Union[int, float]:
        return (
            self.allocations_from_government
            + self.allocations_from_local_authority
            + self.allocations_from_other_sources
        )

    @total_donations.default
    def _total_donations(self) -> Union[int, float]:
        return self.donations_from_aboard + self.donations_from_israel

    @total_expenses.default
    def _total_expenses(self) -> Union[int, float]:
        return (
            self.expenses_other
            + self.other_expenses_for_activities
            + self.expenses_for_management
            + self.expenses_salary_for_management
            + self.expenses_salary_for_activities
        )

    @total_service_income.default
    def _total_service_income(self) -> Union[int, float]:
        return (
            self.service_income_from_country
            + self.service_income_from_local_authority
            + self.service_income_from_other
        )

    @total_other_income.default
    def _total_other_income(self) -> Union[int, float]:
        return self.other_income_from_other_sources + self.other_income_members_fee

    # ------------ Ratios ------------
    @program_expense_ratio.default
    def _program_expense_ratio(self) -> Optional[float]:

        total_program_expenses = (
            self.other_expenses_for_activities + self.expenses_salary_for_activities
        )

        if total_program_expenses == 0 or self.total_expenses == 0:
            return None

        return (total_program_expenses / self.total_expenses) * 100

    @administrative_expense_ratio.default
    def _administrative_expense_ratio(self) -> Optional[float]:

        total_administrative_expenses = (
            self.expenses_salary_for_management
            + self.expenses_for_management
            + self.expenses_other
        )

        if total_administrative_expenses == 0 or self.total_expenses == 0:
            return None

        return (total_administrative_expenses / self.total_expenses) * 100


@attr.s(frozen=True, auto_attribs=True, field_transformer=_add_type_validator)
class NgoInfo:
    ngo_id: int

    general_info: NgoGeneralInfo
    financial_info: Optional[NgoFinanceInfo] = attr.ib(default=None)
    top_earners_info: Optional[NgoTopRecipientsSalaries] = attr.ib(default=None)

    @classmethod
    def from_resource_items(cls, ngo_id: int, resources_items: dict) -> "NgoInfo":
        return cls(ngo_id=ngo_id, **resources_items)
