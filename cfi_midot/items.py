# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


from dataclasses import dataclass, field


@dataclass(frozen=True)
class NgoTopRecipientSalary:
    recipient_title: str
    gross_salary_in_nis: float


@dataclass(frozen=True)
class NgoTopRecipientsSalaries:
    resource_name: str = field(default="top_earners_info", init=False)
    top_earners_salaries: list[NgoTopRecipientSalary]
    report_year: int


@dataclass(frozen=True)
class NgoGeneralInfo:
    resource_name: str = field(default="general_info", init=False)

    ngo_name: str
    ngo_goal: str
    ngo_year_founded: int


@dataclass
class NgoFinanceInfo:
    resource_name: str = field(default="financial_info", init=False)
    report_year: int

    allocations_from_government: int
    allocations_from_local_authority: int
    allocations_from_other_sources: int

    donations_from_aboard: int
    donations_from_israel: int
    donations_value_for_money: int

    expenses_other: int
    expenses_for_activities: int
    expenses_for_management: int
    expenses_salary_For_management: int
    expenses_salary_For_activities: int

    service_income_from_country: int
    service_income_from_local_authority: int
    service_income_from_other: int

    other_income_from_other_sources: int
    other_income_members_fee: int

    total_allocations: int = field(init=False)
    total_donations: int = field(init=False)
    total_expenses: int = field(init=False)
    total_service_income: int = field(init=False)
    total_other_income: int = field(init=False)

    def __post_init__(self) -> None:
        self.total_allocations = (
            self.allocations_from_government
            + self.allocations_from_local_authority
            + self.allocations_from_other_sources
        )
        self.total_donations = self.donations_from_aboard + self.donations_from_israel
        self.total_expenses = (
            self.expenses_other
            + self.expenses_for_activities
            + self.expenses_for_management
            + self.expenses_salary_For_management
            + self.expenses_salary_For_activities
        )
        self.total_service_income = (
            self.service_income_from_country
            + self.service_income_from_local_authority
            + self.service_income_from_other
        )
        self.total_other_income = (
            self.other_income_from_other_sources + self.other_income_members_fee
        )


@dataclass(frozen=True)
class NgoInfo:
    ngo_id: int

    general_info: NgoGeneralInfo
    financial_info: NgoFinanceInfo
    top_earners_info: NgoTopRecipientsSalaries

    @classmethod
    def from_resource_items(cls, ngo_id: int, resources_items: dict) -> "NgoInfo":
        return cls(ngo_id=ngo_id, **resources_items)
