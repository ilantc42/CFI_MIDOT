# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from typing import Optional
import attr


@attr.s(frozen=True, auto_attribs=True)
class NgoTopRecipientSalary:
    recipient_title: str
    gross_salary_in_nis: float


@attr.s(frozen=True, auto_attribs=True)
class NgoTopRecipientsSalaries:
    top_earners_salaries: list[NgoTopRecipientSalary]
    report_year: int


@attr.s(frozen=True, auto_attribs=True)
class NgoGeneralInfo:
    ngo_name: str
    ngo_goal: str
    ngo_year_founded: int
    volunteers_num: Optional[int] = attr.ib(default=None)
    employees_num: Optional[int] = attr.ib(default=None)
    ngo_members_num: Optional[int] = attr.ib(default=None)


@attr.s(frozen=True, auto_attribs=True)
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

    expenses_salary_for_activities: int = attr.ib(default=0)
    other_expenses_for_activities: int = attr.ib(default=0)
    donations_value_for_money: int = attr.ib(default=0)

    # ------------ Computed ------------
    total_allocations: int = attr.ib(init=False)
    total_donations: int = attr.ib(init=False)
    total_expenses: int = attr.ib(init=False)
    total_service_income: int = attr.ib(init=False)
    total_other_income: int = attr.ib(init=False)
    # ------------ Ratios ------------
    program_expense_ratio: Optional[float] = attr.ib(init=False)
    administrative_expense_ratio: Optional[float] = attr.ib(init=False)

    @total_allocations.default
    def _total_allocations(self) -> int:
        return (
            self.allocations_from_government
            + self.allocations_from_local_authority
            + self.allocations_from_other_sources
        )

    @total_donations.default
    def _total_donations(self) -> int:
        return self.donations_from_aboard + self.donations_from_israel

    @total_expenses.default
    def _total_expenses(self) -> int:
        return (
            self.expenses_other
            + self.other_expenses_for_activities
            + self.expenses_for_management
            + self.expenses_salary_For_management
            + self.expenses_salary_for_activities
        )

    @total_service_income.default
    def _total_service_income(self) -> int:
        return (
            self.service_income_from_country
            + self.service_income_from_local_authority
            + self.service_income_from_other
        )

    @total_other_income.default
    def _total_other_income(self) -> int:
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
            self.expenses_salary_For_management
            + self.expenses_for_management
            + self.expenses_other
        )

        if total_administrative_expenses == 0 or self.total_expenses == 0:
            return None

        return (total_administrative_expenses / self.total_expenses) * 100


@attr.s(frozen=True, auto_attribs=True)
class NgoInfo:
    ngo_id: int

    general_info: NgoGeneralInfo
    financial_info: Optional[NgoFinanceInfo] = attr.ib(default=None)
    top_earners_info: Optional[NgoTopRecipientsSalaries] = attr.ib(default=None)

    @classmethod
    def from_resource_items(cls, ngo_id: int, resources_items: dict) -> "NgoInfo":
        return cls(ngo_id=ngo_id, **resources_items)
