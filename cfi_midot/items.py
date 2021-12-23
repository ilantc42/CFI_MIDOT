# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from typing import Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class NgoTopRecipientSalary:
    recipient_title: str
    gross_salary_in_nis: float


@dataclass(frozen=True)
class NgoTopRecipientsSalaries:
    top_earners_salaries: list[NgoTopRecipientSalary]
    report_year: int


@dataclass(frozen=True)
class NgoGeneralInfo:
    ngo_name: str
    ngo_goal: str
    ngo_year_founded: int
    volunteers_num: Optional[int] = field(default=None)
    employees_num: Optional[int] = field(default=None)
    ngo_members_num: Optional[int] = field(default=None)


@dataclass
class NgoFinanceInfo:
    report_year: int

    allocations_from_government: int
    allocations_from_local_authority: int
    allocations_from_other_sources: int

    donations_from_aboard: int
    donations_from_israel: int

    expenses_other: int
    expenses_for_management: int
    expenses_salary_For_management: int

    service_income_from_country: int
    service_income_from_local_authority: int
    service_income_from_other: int

    other_income_from_other_sources: int
    other_income_members_fee: int

    expenses_salary_for_activities: int = field(default=0)
    other_expenses_for_activities: int = field(default=0)
    donations_value_for_money: int = field(default=0)

    @property
    def total_allocations(self) -> int:
        return (
            self.allocations_from_government
            + self.allocations_from_local_authority
            + self.allocations_from_other_sources
        )

    @property
    def total_donations(self) -> int:
        return self.donations_from_aboard + self.donations_from_israel

    @property
    def total_expenses(self) -> int:
        return (
            self.expenses_other
            + self.other_expenses_for_activities
            + self.expenses_for_management
            + self.expenses_salary_For_management
            + self.expenses_salary_for_activities
        )

    @property
    def total_service_income(self) -> int:
        return (
            self.service_income_from_country
            + self.service_income_from_local_authority
            + self.service_income_from_other
        )

    @property
    def total_other_income(self) -> int:
        return self.other_income_from_other_sources + self.other_income_members_fee

    # ------------ Ratios ------------
    @property
    def program_expense_ratio(self) -> Optional[float]:

        total_program_expenses = (
            self.other_expenses_for_activities + self.expenses_salary_for_activities
        )

        if total_program_expenses == 0 or self.total_expenses == 0:
            return None

        return (total_program_expenses / self.total_expenses) * 100

    @property
    def administrative_expense_ratio(self) -> Optional[float]:

        total_administrative_expenses = (
            self.expenses_salary_For_management
            + self.expenses_for_management
            + self.expenses_other
        )

        if total_administrative_expenses == 0 or self.total_expenses == 0:
            return None

        return (total_administrative_expenses / self.total_expenses) * 100


@dataclass(frozen=True)
class NgoInfo:
    ngo_id: int

    general_info: NgoGeneralInfo
    financial_info: Optional[NgoFinanceInfo] = field(default=None)
    top_earners_info: Optional[NgoTopRecipientsSalaries] = field(default=None)

    @classmethod
    def from_resource_items(cls, ngo_id: int, resources_items: dict) -> "NgoInfo":
        return cls(ngo_id=ngo_id, **resources_items)
